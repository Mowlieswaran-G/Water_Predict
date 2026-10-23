# 💧 Ward Water Quality Reporter (WardWater)

> **A Transparent, Honest Groundwater Telemetry & Multi-Role Governance Platform for Tamil Nadu.**  
> Built for institutional transparency, data-backed environmental accountability, and citizen access.  
> **Official Data Source:** Central Ground Water Board (CGWB), Ministry of Jal Shakti, Government of India.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Pytest](https://img.shields.io/badge/Tests-88%20Passed-44cc11?logo=pytest&logoColor=white)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Theme](https://img.shields.io/badge/UI-Dark%20%26%20Light%20Modes-0284c7)](#-revenlo-saas-design-system)

---

## 🌟 Overview & Core Philosophy

The **Ward Water Quality Reporter** enables residents, field inspectors, hydrologists, and environmental officers to inspect official groundwater quality telemetry across Tamil Nadu's districts and Urban Local Bodies (ULBs).

Unlike generic portals, this platform enforces a strict **Truth-in-Data** standard:
- **Never invents data**: If a parameter, date, or station link does not exist in the official dataset, it is explicitly reported as unavailable.
- **Accurate Historical Labelling**: Any water sample collected more than **365 days ago** is prominently flagged with a warning badge showing the exact collection date and sample age.
- **Unverified Ward Match Disclaimer**: Because CGWB wells monitor regional aquifers rather than municipal tap pipelines, ward-level associations are explicitly labeled as *Unverified Approximation*.
- **Mandatory Human Approval**: No regulatory compliance report can be published without explicit sign-off by a designated Environmental Officer.

---

## 🚀 Key Features

### 1. 📊 Three Integrated Datasets
- **Cleaned Groundwater Telemetry (`data/tamil_nadu_groundwater_quality_cleaned.csv`)**: 1,189 verified CGWB records across 31 districts, tracking 41 physical and chemical parameters (pH, TDS, Nitrate, Fluoride, Chloride, Hardness, Heavy Metals).
- **Raw Station Telemetry (`data/tamil_nadu_groundwater_quality_raw.csv`)**: 1,223 raw station telemetry records with original parameter codes and field notes.
- **Tamil Nadu ULB / Ward Directory (`data/tamil_nadu_ulb_wards.csv`)**: 25 Urban Local Bodies categorized by administrative type (Municipal Corporations, Municipalities, Town Panchayats).

### 2. 👥 Role-Based Governance (RBAC)
Dedicated authenticated dashboards tailored for each stakeholder:
- ⚖️ **Environmental Officer** (`/dashboard/officer`): Audit draft telemetry reports, conduct compliance reviews, and issue official publication approvals.
- 🏛️ **Municipal Quality Inspector** (`/dashboard/inspector`): Monitor ward contamination flags, schedule on-site inspections, and audit supply safety.
- 🧪 **Senior Hydrologist** (`/dashboard/hydrologist`): Analyze aquifer chemical trends, CGWB well metrics, depth telemetry, and seasonal salinity shifts.
- 👥 **Public Citizen / Researcher** (`/dashboard/citizen`): Search open groundwater records, review approved ward water reports, and submit citizen inquiries.

### 3. 🎨 Modern SaaS Design System (Dark & Light Theme)
- Full support for both **Light Mode** and **Dark Mode** with instant theme toggling and `localStorage` persistence.
- Executive sidebar navigation with quick search, collapsible toggle, and live user status badges.
- **Split-Screen Authentication**: Full-bleed cosmic water telemetry visual on the left paired with a clean white-theme login and registration form on the right.

### 4. 🔬 Scientific Water Quality Standards & Normalization
- Built-in BIS (Bureau of Indian Standards IS 10500:2012) and WHO drinking water guideline limits (`src/water_standards.py`).
- Automated, safe unit normalization (`1 mg/L = 1,000 µg/L`) with strict guards preventing non-concentration units (like pH) from invalid conversion.
- One-click export to official **PDF** and **CSV** formats.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Core & Logic** | Python 3.11+, Pandas, NumPy |
| **Web Framework** | Flask 3.0+, Jinja2, Werkzeug Security |
| **WSGI Server** | Gunicorn (Multi-worker production server) |
| **Data Storage** | SQLite3 (`outputs/reports.db` for approval audit logs & user accounts) |
| **Data Sources** | Central Ground Water Board (CGWB) & TN Urban Development CSVs |
| **Visualization** | Chart.js, Plotly, Custom SVG Telemetry Gauges |
| **Export Engine** | FPDF2 for automated regulatory PDF generation |
| **Containerization**| Docker, Docker Compose |
| **Testing** | Pytest (88 unit and integration tests) |

---

## 📁 Repository Structure

```
Water_Predict/
├── app.py                            # Flask application controller & routes
├── Dockerfile                        # Production Docker container definition
├── docker-compose.yml                # Docker Compose config with live volume mounts
├── requirements.txt                  # Python dependency specifications
├── README.md                         # Project documentation
│
├── data/                             # Official datasets
│   ├── tamil_nadu_groundwater_quality_cleaned.csv   # Cleaned CGWB dataset (1,189 records)
│   ├── tamil_nadu_groundwater_quality_raw.csv       # Raw CGWB station telemetry (1,223 records)
│   └── tamil_nadu_ulb_wards.csv                     # Tamil Nadu ULB & Ward directory
│
├── src/                              # Core processing modules
│   ├── __init__.py
│   ├── analysis.py                   # Search pipeline, summary computation & metrics
│   ├── approval.py                   # SQLite approval workflow & audit trail
│   ├── auth.py                       # User management, salted password hashes & RBAC
│   ├── data_loader.py                # Multi-dataset loader & dynamic column inspection
│   ├── date_utils.py                 # Historical sample age computation & ISO date parser
│   ├── filtering.py                  # District, station, date range, and parameter filters
│   ├── normalization.py              # Unit conversions (mg/L ↔ µg/L) & guardrails
│   ├── report_generator.py           # Draft report builder & automated PDF generator
│   ├── source_verification.py        # Provenance, dataset metadata & limitation tracking
│   ├── validation.py                 # Column validation, input sanitation & ward checks
│   └── water_standards.py            # BIS IS 10500 & WHO permissible limits database
│
├── static/
│   ├── css/
│   │   └── style.css                 # Main stylesheet (Design tokens, Dark/Light modes)
│   ├── js/
│   │   └── app.js                    # Dynamic frontend filtering, charts & search logic
│   └── img/
│       └── login_showcase.jpg        # Telemetry crystal visual for login showcase
│
├── templates/
│   ├── base.html                     # Main shell with sidebar, topbar & theme controls
│   ├── home.html                     # Search explorer & multi-dataset browser
│   ├── login.html                    # White-theme split-screen login & registration
│   ├── report.html                   # Draft water quality report & approval flow
│   ├── results.html                  # Search query result tables & telemetry gauges
│   ├── history.html                  # Historical sample tracking & trend comparisons
│   ├── detail.html                   # Station drill-down & parameter analysis
│   ├── error.html                    # User-friendly error templates
│   └── dashboards/                   # Dedicated role-based portals
│       ├── officer.html              # Environmental Officer dashboard
│       ├── inspector.html            # Municipal Quality Inspector dashboard
│       ├── hydrologist.html          # Senior Hydrologist analytics dashboard
│       └── citizen.html              # Public Citizen & community research portal
│
├── tests/                            # Automated test suite (88 tests)
│   ├── __init__.py
│   ├── test_auth.py                  # User authentication & role verification tests
│   ├── test_datasets_integration.py  # 3-dataset schema & loader integration tests
│   ├── test_dates.py                 # Date parsing & historical age computation tests
│   ├── test_normalization.py         # Unit conversion & parameter guardrail tests
│   ├── test_scenarios.py             # Hackathon test cases TC1–TC4 integration tests
│   └── test_validation.py            # Column schema & input sanitation tests
│
└── outputs/
    └── reports.db                    # SQLite database (auto-created on first run)
```

---

## ⚡ Quick Start Guide

### Option 1: Docker (Recommended)

Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is running, then run:

```bash
docker compose up -d --build
```

The application will be live at: **`http://localhost:5000`**

To view logs or stop the container:
```bash
docker compose logs -f
docker compose down
```

---

### Option 2: Local Python Environment

1. **Clone the repository and enter the directory**:
   ```bash
   cd Water_Predict
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the web application**:
   ```bash
   python app.py
   ```

5. **Open your browser**:
   Navigate to **`http://localhost:5000`**

---

## 🔐 Demo Accounts & Credentials

The application is pre-seeded with accounts for all 4 governance roles:

| Role | Username | Password | Default Dashboard |
|---|---|---|---|
| **Environmental Officer** | `officer` | `officer2026` | `/dashboard/officer` |
| **Municipal Inspector** | `inspector` | `inspector2026` | `/dashboard/inspector` |
| **Senior Hydrologist** | `hydrologist` | `hydro2026` | `/dashboard/hydrologist` |
| **Public Citizen** | `citizen` | `citizen2026` | `/dashboard/citizen` |

> 💡 **User Registration**: You can also create a new account directly from the login page by clicking **"Sign up"** and selecting your designated role.

---

## 🧪 Automated Testing

The project includes an automated test suite covering authentication, multi-dataset loading, date utilities, unit conversion, and test scenarios.

Run the test suite:
```powershell
python -m pytest -v
```

### Test Suite Summary:
```
============================= test session starts =============================
tests/test_auth.py .........                                             [ 10%]
tests/test_datasets_integration.py ....                                  [ 14%]
tests/test_dates.py ..................                                   [ 35%]
tests/test_normalization.py ............                                 [ 48%]
tests/test_scenarios.py ...................                              [ 70%]
tests/test_validation.py ..........................                      [100%]
============================= 88 passed in 2.62s ==============================
```

---

## 📋 Hackathon Scenarios Tested (TC1 – TC4)

| Test Case | Scenario | Expected Behavior | Verification |
|---|---|---|---|
| **TC1** | Search with Ward specified | Shows water data with **Unverified Match** badge; never falsely claims piped tap connection. | Verified in `test_scenarios.py` |
| **TC2** | Sample older than 365 days | Prominently labels sample as **Historical** with exact days elapsed. | Verified in `test_dates.py` |
| **TC3** | Concentration unit mismatch | Normalizes `1 mg/L = 1000 µg/L` transparently; protects non-concentration units. | Verified in `test_normalization.py` |
| **TC4** | Missing ward in dataset | Displays clear notice: *"No direct monitoring records found for this ward."* | Verified in `test_scenarios.py` |

---

## 🛡️ Integrity, Transparency & Limitations

| Limitation | Technical Reason | Public Safeguard |
|---|---|---|
| **Groundwater Only** | CGWB samples monitoring wells, not municipal distribution pipes. | Clearly labeled as *Groundwater Telemetry*; cannot certify tap drinking water. |
| **Historical Data** | Official state lab tests are periodic rather than continuous real-time feeds. | Exact collection year/date is displayed with sample age warnings. |
| **No Auto-Publishing** | Automated pipelines could publish false alarms without review. | Human approval required from an Environmental Officer before report release. |

---

## 📄 License & Attribution

- **Data Attribution**: Central Ground Water Board (CGWB), Department of Water Resources, Ministry of Jal Shakti, Government of India.
- **License**: Released under the **MIT License**.
- Built with transparent science for public health and water accountability. 💧