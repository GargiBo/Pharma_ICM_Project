from database import get_db

def calculate_incentive(employee_id, period="2026-09"):
    db = get_db()
    employee = db.execute(
        "SELECT * FROM employees WHERE employee_id=?", (employee_id,)
    ).fetchone()
    if not employee:
        return None

    target_row = db.execute("""
        SELECT COALESCE(SUM(target_amount),0) target
        FROM targets WHERE employee_id=? AND period=?
    """, (employee_id, period)).fetchone()
    sales_row = db.execute("""
        SELECT COALESCE(SUM(s.sales_amount),0) actual
        FROM sales s WHERE s.employee_id=? AND substr(s.sale_date,1,7)=?
    """, (employee_id, period)).fetchone()

    target = float(target_row["target"])
    actual = float(sales_row["actual"])
    attainment = (actual / target * 100) if target else 0

    rule = db.execute("""
        SELECT * FROM compensation_rules
        WHERE ? >= min_achievement AND ? <= max_achievement
        ORDER BY min_achievement DESC LIMIT 1
    """, (attainment, attainment)).fetchone()

    rate = float(rule["incentive_rate"]) if rule else 0
    accelerator = float(rule["multiplier"]) if rule else 1
    base_incentive = actual * rate

    product_rows = db.execute("""
        SELECT s.product_id, SUM(s.sales_amount) amount,
               p.incentive_rate
        FROM sales s JOIN products p ON p.product_id=s.product_id
        WHERE s.employee_id=? AND substr(s.sale_date,1,7)=?
        GROUP BY s.product_id, p.incentive_rate
    """, (employee_id, period)).fetchall()

    product_bonus = sum(float(r["amount"]) * float(r["incentive_rate"]) for r in product_rows)

    # Demo quality/compliance values; in a real system these would be sourced from a quality table.
    quality_bonus = actual * 0.01 if attainment >= 100 else 0
    compliance_penalty = actual * 0.005 if attainment < 80 else 0

    final_incentive = (
        base_incentive * accelerator
        + product_bonus
        + quality_bonus
        - compliance_penalty
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee["employee_name"],
        "role": employee["role"],
        "region": employee["region"],
        "territory": employee["territory"],
        "period": period,
        "target_amount": target,
        "actual_sales": actual,
        "attainment": round(attainment, 2),
        "base_incentive": round(base_incentive, 2),
        "product_bonus": round(product_bonus, 2),
        "quality_bonus": round(quality_bonus, 2),
        "compliance_penalty": round(compliance_penalty, 2),
        "accelerator": accelerator,
        "final_incentive": round(final_incentive, 2)
    }
