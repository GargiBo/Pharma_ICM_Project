# PharmaComp360

**Life Sciences Incentive Compensation Management (ICM) Demo**

PharmaComp360 is a portfolio project that demonstrates how a pharmaceutical sales organization can calculate and manage incentive compensation using configurable business rules.

## Business flow

Sales Data → Targets/Quota → Attainment → Compensation Rule → Accelerator → Product Bonus → Quality/Compliance Adjustment → Final Incentive → Manager Approval → Audit Trail

## Features

- Employee and sales-force hierarchy
- Product and therapeutic-area setup
- Target/quota management
- Configurable attainment-based compensation rules
- Accelerators for over-achievement
- Product-based incentive bonus
- Quality bonus and compliance penalty demonstration
- Compensation calculation API
- Manager approval/rejection workflow
- Audit trail
- Executive dashboard
- Sample synthetic life-sciences data

## Tech stack

- Python
- Flask
- SQLite
- HTML/CSS/Jinja
- REST API
- Git/GitHub ready

## Run locally

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Run:
```bash
python app.py
```

Open:
`http://127.0.0.1:5000`

The SQLite database is created and seeded automatically on first run.

## Demo API

```text
GET /api/incentive/EMP001
```

## Project structure

```text
PharmaComp360/
├── app.py
├── database.py
├── compensation.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── employees.html
│   ├── products.html
│   ├── calculate.html
│   ├── approvals.html
│   └── audit.html
└── static/
    └── style.css
```

## Important note

All employee, product, sales and compensation data in this demo is synthetic. It is not based on confidential customer, patient, or pharmaceutical-company information.

## Future enhancement

For a production-grade ICM implementation, the calculation layer can be extended with effective-dated compensation plans, plan versions, quota allocation, role-based access control, Excel ingestion, PostgreSQL, SSO, payroll integration, and richer audit/versioning.
