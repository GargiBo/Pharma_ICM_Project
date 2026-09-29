from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import get_db, init_db, seed_db
from compensation import calculate_incentive

app = Flask(__name__)
app.secret_key = "pharmacom360-demo-secret"

@app.route("/")
def dashboard():
    db = get_db()
    stats = {
        "employees": db.execute("SELECT COUNT(*) c FROM employees").fetchone()["c"],
        "sales": db.execute("SELECT COALESCE(SUM(sales_amount),0) s FROM sales").fetchone()["s"],
        "payout": db.execute("SELECT COALESCE(SUM(final_incentive),0) p FROM incentive_results").fetchone()["p"],
        "avg_attainment": db.execute("""
            SELECT COALESCE(AVG(attainment),0) a FROM incentive_results
        """).fetchone()["a"]
    }
    regions = db.execute("""
        SELECT e.region, SUM(s.sales_amount) sales
        FROM sales s JOIN employees e ON e.employee_id=s.employee_id
        GROUP BY e.region ORDER BY sales DESC
    """).fetchall()
    recent = db.execute("""
        SELECT i.*, e.employee_name
        FROM incentive_results i JOIN employees e ON e.employee_id=i.employee_id
        ORDER BY i.id DESC LIMIT 10
    """).fetchall()
    return render_template("dashboard.html", stats=stats, regions=regions, recent=recent)

@app.route("/employees")
def employees():
    db = get_db()
    rows = db.execute("SELECT * FROM employees ORDER BY employee_id").fetchall()
    return render_template("employees.html", employees=rows)

@app.route("/products")
def products():
    db = get_db()
    rows = db.execute("SELECT * FROM products ORDER BY product_name").fetchall()
    return render_template("products.html", products=rows)

@app.route("/calculate/<employee_id>", methods=["GET", "POST"])
def calculate(employee_id):
    result = calculate_incentive(employee_id)
    if result is None:
        flash("Employee not found.")
        return redirect(url_for("employees"))
    if request.method == "POST":
        db = get_db()
        db.execute("""
            INSERT INTO incentive_results
            (employee_id, period, target_amount, actual_sales, attainment,
             base_incentive, product_bonus, quality_bonus, compliance_penalty,
             accelerator, final_incentive, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            result["employee_id"], result["period"], result["target_amount"],
            result["actual_sales"], result["attainment"], result["base_incentive"],
            result["product_bonus"], result["quality_bonus"], result["compliance_penalty"],
            result["accelerator"], result["final_incentive"], "PENDING"
        ))
        db.commit()
        flash("Incentive calculation saved as PENDING approval.")
        return redirect(url_for("approvals"))
    return render_template("calculate.html", r=result)

@app.route("/approvals")
def approvals():
    db = get_db()
    rows = db.execute("""
        SELECT i.*, e.employee_name
        FROM incentive_results i JOIN employees e ON e.employee_id=i.employee_id
        ORDER BY i.id DESC
    """).fetchall()
    return render_template("approvals.html", rows=rows)

@app.route("/approval/<int:result_id>/<action>", methods=["POST"])
def approval(result_id, action):
    if action not in ("approve", "reject"):
        return redirect(url_for("approvals"))
    status = "APPROVED" if action == "approve" else "REJECTED"
    db = get_db()
    row = db.execute("SELECT * FROM incentive_results WHERE id=?", (result_id,)).fetchone()
    if row:
        db.execute("UPDATE incentive_results SET status=? WHERE id=?", (status, result_id))
        db.execute("""
            INSERT INTO audit_log(result_id, action, old_status, new_status, reason)
            VALUES (?,?,?,?,?)
        """, (result_id, "STATUS_CHANGE", row["status"], status,
              "Manager approval" if action == "approve" else "Manager rejection"))
        db.commit()
        flash(f"Result {result_id} marked {status}.")
    return redirect(url_for("approvals"))

@app.route("/audit")
def audit():
    db = get_db()
    rows = db.execute("""
        SELECT a.*, e.employee_name
        FROM audit_log a
        LEFT JOIN incentive_results i ON i.id=a.result_id
        LEFT JOIN employees e ON e.employee_id=i.employee_id
        ORDER BY a.id DESC
    """).fetchall()
    return render_template("audit.html", rows=rows)

@app.route("/api/incentive/<employee_id>")
def api_incentive(employee_id):
    result = calculate_incentive(employee_id)
    if not result:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(result)

if __name__ == "__main__":
    init_db()
    seed_db()
    app.run(debug=True)
