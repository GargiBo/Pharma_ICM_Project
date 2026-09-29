import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "pharmacom360.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        employee_name TEXT NOT NULL,
        role TEXT NOT NULL,
        region TEXT NOT NULL,
        territory TEXT NOT NULL,
        manager_id TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        incentive_rate REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        period TEXT NOT NULL,
        target_amount REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        sale_date TEXT NOT NULL,
        sales_amount REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS compensation_rules (
        rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        min_achievement REAL NOT NULL,
        max_achievement REAL NOT NULL,
        incentive_rate REAL NOT NULL,
        multiplier REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS incentive_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        period TEXT NOT NULL,
        target_amount REAL,
        actual_sales REAL,
        attainment REAL,
        base_incentive REAL,
        product_bonus REAL,
        quality_bonus REAL,
        compliance_penalty REAL,
        accelerator REAL,
        final_incentive REAL,
        status TEXT DEFAULT 'PENDING'
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result_id INTEGER,
        action TEXT,
        old_status TEXT,
        new_status TEXT,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    db.commit()

def seed_db():
    db = get_db()
    if db.execute("SELECT COUNT(*) c FROM employees").fetchone()["c"] > 0:
        return

    employees = [
        ("EMP001","Rahul Sharma","Medical Representative","East","Kolkata","MGR001"),
        ("EMP002","Priya Das","Medical Representative","East","Howrah","MGR001"),
        ("EMP003","Amit Roy","Territory Manager","East","Siliguri","MGR002"),
        ("EMP004","Sneha Sen","Medical Representative","West","Mumbai","MGR003"),
        ("EMP005","Arjun Mehta","Medical Representative","North","Delhi","MGR004"),
        ("EMP006","Riya Nair","Medical Representative","South","Bengaluru","MGR005")
    ]
    products = [
        ("P001","CardioCare","Cardiology",0.05),
        ("P002","NeuroCare","Neurology",0.08),
        ("P003","DiabCare","Diabetes",0.10),
        ("P004","OncoCare","Oncology",0.12)
    ]
    rules = [
        (0,79.99,0.00,1.00),
        (80,99.99,0.05,1.00),
        (100,109.99,0.10,1.00),
        (110,119.99,0.15,1.25),
        (120,9999,0.20,1.50)
    ]
    db.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", employees)
    db.executemany("INSERT INTO products VALUES (?,?,?,?)", products)
    db.executemany("""
        INSERT INTO compensation_rules
        (min_achievement,max_achievement,incentive_rate,multiplier)
        VALUES (?,?,?,?)
    """, rules)

    targets = []
    sales = []
    values = [
        ("EMP001","P001",1000000,1150000),
        ("EMP002","P002",1200000,1000000),
        ("EMP003","P003",1500000,1800000),
        ("EMP004","P004",900000,1170000),
        ("EMP005","P001",1300000,1560000),
        ("EMP006","P003",1100000,770000)
    ]
    for emp, prod, target, actual in values:
        targets.append((emp, prod, "2026-09", target))
        sales.append((emp, prod, "2026-09-15", actual))
    db.executemany("""
        INSERT INTO targets(employee_id,product_id,period,target_amount)
        VALUES (?,?,?,?)
    """, targets)
    db.executemany("""
        INSERT INTO sales(employee_id,product_id,sale_date,sales_amount)
        VALUES (?,?,?,?)
    """, sales)
    db.commit()
