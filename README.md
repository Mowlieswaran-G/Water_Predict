# 💧 WardWater — Ward Water Quality Reporter & Groundwater Telemetry System

> **An institutional-grade environmental intelligence and groundwater quality governance platform for Tamil Nadu**, designed to provide transparent, verified water chemistry records, historical sample auditing, and human-in-the-loop regulatory approval using official **Central Ground Water Board (CGWB)** data.

WardWater is an intelligent web-based environmental inspection and telemetry platform that empowers citizens, municipal inspectors, senior hydrologists, and environmental regulatory officers to audit groundwater safety. Users can query water records across 31 Tamil Nadu districts and Urban Local Bodies (ULBs), inspect 41 chemical and physical parameters against **BIS IS 10500:2012** and **WHO** standards, normalize units transparently, track sample age with automatic historical warnings, and execute regulatory approval workflows before publishing official reports.

The application is built with **Python 3.11, Flask 3.0, Gunicorn, Pandas, SQLite3, Plotly, Chart.js, FPDF2, and Docker**, featuring a modern **Revenlo SaaS Design System** with native Dark and Light modes, a white-theme authentication portal, and seamless deployment on **Render Cloud**.

🔗 **Live App:** [ward-water-quality-reporter.onrender.com](https://ward-water-quality-reporter.onrender.com)  
📂 **Repository:** [github.com/Mowlieswaran-G/Water_Predict](https://github.com/Mowlieswaran-G/Water_Predict)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-Live-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-88%20Passed-44cc11?style=for-the-badge&logo=pytest&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## 📋 Table of Contents

- [Overview](#overview)
- [What WardWater Does](#what-wardwater-does)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Multi-Dataset Foundation](#multi-dataset-foundation)
- [Data Ingestion & Preprocessing](#data-ingestion--preprocessing)
- [Search & Telemetry Pipeline](#search--telemetry-pipeline)
- [Water Quality Standards & Normalization](#water-quality-standards--normalization)
- [Human Approval & Governance Workflow](#human-approval--governance-workflow)
- [Results and Analytics](#results-and-analytics)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [Example Workflow](#example-workflow)
- [User Interface & Design System](#user-interface--design-system)
- [Core Components](#core-components)
- [Security Considerations](#security-considerations)
- [Potential Municipal & Industrial Applications](#potential-municipal--industrial-applications)
- [Advantages](#advantages)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Testing Strategy](#testing-strategy)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Author](#author)
- [Project Summary](#project-summary)

---

<a id="overview"></a>
## 🧠 Overview

Groundwater quality is critical to public health, industrial safety, and agricultural sustainability across Tamil Nadu. However, traditional public access to environmental water telemetry suffers from critical limitations:

- **Data Opacity**: Raw lab measurements are often locked in unstructured records or complex scientific spreadsheets that citizens and local administrators cannot easily interpret.
- **Outdated Records Masquerading as Real-Time Data**: Water quality tests collected years ago are frequently presented without clear collection timestamps or age warnings.
- **Unverified Spatial Associations**: Regional monitoring wells are often falsely conflated with municipal piped drinking-water networks, misleading the public regarding actual tap water potability.
- **Lack of Governance & Human Oversight**: Automated reports are sometimes generated without regulatory inspection, provenance tracking, or audit trails.

WardWater resolves these challenges by introducing a **Truth-in-Data governance framework** that couples verified Central Ground Water Board (CGWB) telemetry with automated unit normalization, strict historical warnings, BIS/WHO standard comparisons, and mandatory human sign-off before regulatory report publication.

---

<a id="what-wardwater-does"></a>
## 🔎 What WardWater Does

```
                  User Query (District, Station, Ward, Date, Parameters)
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │            Multi-Dataset Ingestion            │
                    │   Cleaned CGWB  •  Raw Chemistry  •  ULB Wards │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │         Validation & Guardrail Engine         │
                    │   District Check  •  Station Filter  • Dates  │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │      Unit Normalization & Age Computation     │
                    │   mg/L ↔ µg/L Conversion  •  >365d Warning    │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │         Scientific Standards Engine           │
                    │     BIS IS 10500:2012 Limits  •  WHO Bounds   │
                    └───────────────────────┬───────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         Interactive Telemetry                           Draft Regulatory Report
         Search & Visual Charts                                     │
                    │                                               ▼
                    │                               ┌───────────────────────────────┐
                    │                               │    Human Approval Pipeline    │
                    │                               │   Officer Review  •  Audit    │
                    │                               └───────────────┬───────────────┘
                    │                                               │
                    ▼                                               ▼
         Public Citizen Insights                         Approved Official Publication
         Gauges • Tables • Trends                        PDF Export • CSV • SQLite Audit
```

---

<a id="key-features"></a>
## ✨ Key Features

### 1. 🔍 Truth-in-Data Groundwater Search
Search groundwater quality across 31 Tamil Nadu districts with zero synthetic data invention. If a station, ward, or chemical reading does not exist, the platform explicitly reports its absence.

### 2. 📅 Dynamic Sample Age & Historical Warning System
Every monitoring record is evaluated dynamically against the current system date. Any test older than **365 days** is prominently labeled with an amber **Historical Record** alert showing the exact collection date and elapsed age in days.

### 3. ⚖️ Multi-Role Governance (RBAC)
Tailored portals and dedicated permissions for four distinct environmental roles:
- **Environmental Officer** (`/dashboard/officer`): Review draft telemetry, approve/reject publications, and maintain compliance records.
- **Municipal Quality Inspector** (`/dashboard/inspector`): Audit ward contamination flags and coordinate field investigations.
- **Senior Hydrologist** (`/dashboard/hydrologist`): Monitor aquifer chemical trends, well depths, and electrical conductivity.
- **Public Citizen / Researcher** (`/dashboard/citizen`): Open access to approved records, district summaries, and public queries.

### 4. 🔬 Scientific Water Quality Benchmarking
Evaluates water readings against official standards:
- **Bureau of Indian Standards (BIS IS 10500:2012)**: Acceptable and permissible drinking limits.
- **World Health Organization (WHO)**: International guideline limits for toxic and heavy metal parameters.

### 5. 🔄 Transparent Unit Normalization
Converts units automatically (`1 mg/L = 1,000 µg/L`) while preserving the original recorded unit for full transparency. Non-concentration parameters (such as pH) are strictly protected against invalid mathematical conversions.

### 6. 📄 Automated Regulatory Export (PDF & CSV)
Generate verifiable, institutional-grade PDF inspection reports with official water drop seals, provenance notes, reviewer audit logs, and raw CSV exports.

### 7. 🎨 Revenlo SaaS Design System (Dark & Light Theme)
Executive user interface featuring:
- Seamless Dark Mode and Light Mode switching with `localStorage` persistence.
- Collapsible sidebar navigation, live search shortcuts, and status pill badges.
- Split-screen white-theme authentication portal with an untouched, full-bleed cosmic water telemetry visual.

---

<a id="architecture-overview"></a>
## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Revenlo SaaS UI Layer                             │
│       Executive Shell  •  Topbar & Dark/Light Toggle  •  White Auth        │
│       Role Dashboards (Officer, Inspector, Hydrologist, Citizen)            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Flask Application Layer                            │
│     app.py  •  Jinja2 Templates  •  Session Auth  •  REST Endpoints        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Core Analytics Layer                              │
│       src/analysis.py           src/validation.py      src/water_standards  │
│       src/date_utils.py         src/normalization.py   src/source_verif     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Data Storage & Governance Layer                       │
│    data/*.csv (Cleaned, Raw, ULBs)  •  outputs/reports.db (SQLite Audit)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

<a id="multi-dataset-foundation"></a>
## 🗃️ Multi-Dataset Foundation

WardWater integrates three specialized datasets to provide complete administrative and chemical coverage:

```
                                  Tamil Nadu Multi-Dataset Hub
                                               │
         ┌─────────────────────────────────────┼─────────────────────────────────────┐
         ▼                                     ▼                                     ▼
 ┌───────────────┐                     ┌───────────────┐                     ┌───────────────┐
 │ Cleaned CGWB  │                     │ Raw Station   │                     │ ULB & Ward    │
 │  1,189 Rows   │                     │  1,223 Rows   │                     │  Directory    │
 │ 41 Parameters │                     │ Original Codes│                     │  25 ULBs      │
 └───────────────┘                     └───────────────┘                     └───────────────┘
```

| Dataset | File Path | Records | Scope |
|---|---|---|---|
| **Cleaned Groundwater Telemetry** | `data/tamil_nadu_groundwater_quality_cleaned.csv` | 1,189 | 31 districts, 41 physical/chemical parameters (pH, TDS, Nitrate, Fluoride, Hardness, etc.) |
| **Raw Station Chemistry** | `data/tamil_nadu_groundwater_quality_raw.csv` | 1,223 | Original station telemetry codes, field collection logs, and uncurated metrics |
| **Tamil Nadu ULB / Ward Directory** | `data/tamil_nadu_ulb_wards.csv` | 25 ULBs | Administrative Urban Local Bodies (Municipal Corporations, Municipalities, Town Panchayats) |

---

<a id="data-ingestion--preprocessing"></a>
## 📥 Data Ingestion & Preprocessing

The ingestion pipeline (`src/data_loader.py` & `src/validation.py`) enforces strict validation rules:

```
CSV File on Disk
       │
       ▼
Strip Leading / Trailing Whitespace
       │
       ▼
Dynamic Column Type Inspection
       │
       ▼
Identify District, Station & Date Headers
       │
       ▼
Extract Valid Numeric Parameter Columns
       │
       ▼
Build In-Memory DatasetProfile
```

- **Whitespace Sanitation**: Strips invisible trailing spaces from column names and string cells.
- **Empty Column Quarantine**: Columns containing 100% missing values are isolated and reported.
- **Zero Invention**: If a file or station is missing, the platform raises an explicit HTTP 503 or friendly error page rather than synthesizing placeholder data.

---

<a id="search--telemetry-pipeline"></a>
## 🔬 Search & Telemetry Pipeline

```
Search Query Received
         │
         ▼
Validate District & Station Selection
         │
         ▼
Filter Records by Date Window (30d, 90d, 365d, All Time)
         │
         ▼
Apply Unit Normalization (mg/L ↔ µg/L)
         │
         ▼
Evaluate Historical Sample Age (>365 Days)
         │
         ▼
Cross-Reference BIS IS 10500:2012 Standards
         │
         ▼
Generate Statistical Summary (Mean, Min, Max, Permissible Status)
```

---

<a id="water-quality-standards--normalization"></a>
## 🧪 Water Quality Standards & Normalization

Implemented in `src/water_standards.py` and `src/normalization.py`.

### 📐 Unit Normalization Rules
- **1 mg/L = 1,000 µg/L**
- **1 µg/L = 0.001 mg/L**
- **Blocked Conversions**: Dimensionless and non-concentration metrics (pH, Electrical Conductivity, Turbidity) are strictly guarded against invalid unit arithmetic.
- **Dual Provenance**: Displays both the raw collected value with its original unit and the standardized value.

### 📋 Key Parameter Thresholds (BIS IS 10500:2012)

| Parameter | Acceptable Limit | Permissible Limit | Health Impact If Exceeded |
|---|---|---|---|
| **pH** | 6.5 – 8.5 | No relaxation | Mucous membrane irritation, pipe corrosion |
| **Total Dissolved Solids (TDS)** | 500 mg/L | 2,000 mg/L | Gastrointestinal irritation, scaling |
| **Nitrate (NO₃)** | 45 mg/L | No relaxation | Methemoglobinemia (Blue Baby Syndrome) |
| **Fluoride (F)** | 1.0 mg/L | 1.5 mg/L | Dental and skeletal fluorosis |
| **Chloride (Cl)** | 250 mg/L | 1,000 mg/L | Unpleasant salty taste, corrosive to metal |
| **Total Hardness** | 200 mg/L | 600 mg/L | Encrustation in plumbing, poor lathering |

---

<a id="human-approval--governance-workflow"></a>
## ⚖️ Human Approval & Governance Workflow

```
Draft Report Generated
          │
          ▼
Displayed in Regulatory Review Console
          │
          ▼
Environmental Officer Audits Telemetry & Warnings
          │
     ┌────┴────┐
     ▼         ▼
  Approve    Reject
     │         │
     ▼         ▼
Signed in    Logged with
SQLite DB    Rejection Notes
     │         │
     ▼         ▼
Published    Restricted
to Public    Internal Audit
```

1. **Mandatory Human Sign-off**: Reports are created in **DRAFT** status and are never published automatically.
2. **SQLite Audit Trail** (`outputs/reports.db`): Stores report ID, reviewer username, approval timestamp, and compliance decisions.
3. **Public Accountability**: Once approved, reports become discoverable by citizens and researchers with verified sign-off badges.

---

<a id="results-and-analytics"></a>
## 📊 Results and Analytics

**Search Summary Output Example:**
```
District: Coimbatore
Station: Sulur (Monitoring Well)
Ward Association: Sulur Town Panchayat (Unverified Match)
Sample Date: 2021-05-14 (Historical — 1,988 days elapsed)
Parameters Analyzed: 18
Permissible Compliance: 3 Parameters Exceed BIS Limits (Fluoride: 1.8 mg/L, TDS: 2,140 mg/L, Total Hardness: 680 mg/L)
Approval Status: Approved for Public Release (Reviewed by: Dr. Rajesh Kannan, Environmental Officer)
```

**Visual Telemetry Analytics:**
- Interactive parameter distribution charts (Chart.js & Plotly).
- Telemetry gauge indicators showing Acceptable vs. Permissible vs. Exceeded ranges.
- Downloadable official PDF summary report and raw CSV exports.

---

<a id="project-structure"></a>
## 📂 Project Structure

```
Water_Predict/
│
├── app.py                            → Main Flask application & routing controller
├── Dockerfile                        → Production Docker container specification
├── docker-compose.yml                → Docker Compose orchestration & live volume mounts
├── render.yaml                       → Cloud deployment blueprint for Render
├── Procfile                          → Cloud WSGI process definition
├── requirements.txt                  → Python package specifications
├── README.md                         → Comprehensive documentation
├── .gitignore                        → Git version control exclusions
│
├── data/                             → Official Tamil Nadu datasets
│   ├── tamil_nadu_groundwater_quality_cleaned.csv   → Cleaned CGWB telemetry (1,189 rows)
│   ├── tamil_nadu_groundwater_quality_raw.csv       → Raw CGWB station chemistry (1,223 rows)
│   └── tamil_nadu_ulb_wards.csv                     → Tamil Nadu ULB & Ward directory
│
├── src/                              → Core Python analytical modules
│   ├── __init__.py
│   ├── analysis.py                   → Search query executor & parameter analytics
│   ├── approval.py                   → SQLite approval workflow & audit trail engine
│   ├── auth.py                       → User authentication & Role-Based Access Control
│   ├── data_loader.py                → CSV ingestion & column schema inspector
│   ├── date_utils.py                 → Dynamic sample age & historical label parser
│   ├── filtering.py                  → Multi-dimensional parameter & date filters
│   ├── normalization.py              → Safe unit conversion (mg/L ↔ µg/L)
│   ├── report_generator.py           → Draft report builder & automated PDF engine
│   ├── source_verification.py        → Dataset provenance & limitation trackers
│   ├── validation.py                 → Input sanitation & schema guardrails
│   └── water_standards.py            → BIS IS 10500:2012 & WHO chemical bounds
│
├── static/                           → Web presentation assets
│   ├── css/
│   │   └── style.css                 → Revenlo SaaS stylesheet & Dark/Light tokens
│   ├── js/
│   │   └── app.js                    → Dynamic UI filtering, charts & search logic
│   └── img/
│       └── login_showcase.jpg        → Full-bleed cosmic water visual for auth portal
│
├── templates/                        → Jinja2 HTML templates
│   ├── base.html                     → App shell with sidebar, topbar & theme switchers
│   ├── home.html                     → Search explorer & multi-dataset browser
│   ├── login.html                    → White-theme split-screen login & registration
│   ├── report.html                   → Draft report view & regulatory approval flow
│   ├── results.html                  → Query results, telemetry tables & charts
│   ├── history.html                  → Historical sample audit & trend comparisons
│   ├── detail.html                   → Station drill-down & parameter analysis
│   ├── error.html                    → User-friendly error pages
│   └── dashboards/                   → Dedicated role-based portals
│       ├── officer.html              → Environmental Officer audit dashboard
│       ├── inspector.html            → Municipal Quality Inspector dashboard
│       ├── hydrologist.html          → Senior Hydrologist telemetry dashboard
│       └── citizen.html              → Public Citizen inquiry & search portal
│
├── tests/                            → Automated Pytest test suite (88 tests)
│   ├── __init__.py
│   ├── test_auth.py                  → Authentication, PBKDF2 & RBAC tests
│   ├── test_datasets_integration.py  → 3-dataset schema & loader tests
│   ├── test_dates.py                 → Date parsing & historical age computation tests
│   ├── test_normalization.py         → Unit conversion & parameter guardrail tests
│   ├── test_scenarios.py             → Hackathon TC1–TC4 integration tests
│   └── test_validation.py            → Column schema & input sanitation tests
│
└── outputs/                          → Application artifacts
    └── reports.db                    → SQLite database for approvals & accounts
```

---

<a id="technology-stack"></a>
## 🛠️ Technology Stack

<p>
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
<img src="https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white" alt="Gunicorn"/>
<img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="Pandas"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"/>
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly"/>
<img src="https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="Pytest"/>
<img src="https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white" alt="Render"/>
</p>

| Layer | Technology | Details |
|---|---|---|
| **Programming Language** | Python 3.11+ | High-performance data processing & backend logic |
| **Web Framework** | Flask 3.0+ | RESTful routing, template engine, and request handling |
| **WSGI Server** | Gunicorn 26.2+ | Production WSGI HTTP server with multi-worker concurrency |
| **Data Engine** | Pandas & NumPy | High-performance CSV parsing, filtering & statistics |
| **Governance Database** | SQLite3 | Local ACID-compliant database for user accounts & audit trails |
| **Visual Charts** | Plotly & Chart.js | Parameter distribution charts and trend visualizations |
| **Document Generation** | FPDF2 | Automated regulatory compliance PDF exports |
| **Containerization** | Docker & Docker Compose | Portable container deployment across cloud hosts |
| **Testing Engine** | Pytest 9.1+ | 88 automated unit, schema, and integration tests |
| **Cloud Host** | Render | Production Docker container web service |

---

<a id="role-based-access-control-rbac"></a>
## 👥 Role-Based Access Control (RBAC)

The application includes four pre-configured governance roles with salted PBKDF2 authentication:

| Role | Default Username | Default Password | Primary Portal | Core Permissions |
|---|---|---|---|---|
| ⚖️ **Environmental Officer** | `officer` | `officer2026` | `/dashboard/officer` | Review draft reports, grant official publication approval, audit compliance |
| 🏛️ **Municipal Inspector** | `inspector` | `inspector2026` | `/dashboard/inspector` | Log ward contamination flags, schedule on-site inspections, audit field samples |
| 🧪 **Senior Hydrologist** | `hydrologist` | `hydro2026` | `/dashboard/hydrologist` | Deep well telemetry, aquifer chemical shifts, EC & salinity tracking |
| 👥 **Public Citizen** | `citizen` | `citizen2026` | `/dashboard/citizen` | Open groundwater search, review approved reports, submit citizen queries |

---

<a id="installation"></a>
## 💻 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Mowlieswaran-G/Water_Predict.git
cd Water_Predict
```

### 2. Create and Activate Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

<a id="running-locally"></a>
## ▶️ Running Locally

### Option A: Local Python Server
```bash
python app.py
```
Open your browser at: **`http://localhost:5000`**

### Option B: Local Docker Container
```bash
docker compose up -d --build
```
Open your browser at: **`http://localhost:5000`**

To inspect container logs:
```bash
docker compose logs -f web
```

---

<a id="deployment"></a>
## 🌐 Deployment

WardWater is optimized for automated deployment on **Render Cloud** using the included `Dockerfile` and `render.yaml` blueprint.

```
GitHub Repository (Mowlieswaran-G/Water_Predict)
                     │
                     ▼
             Render Cloud Build
                     │
                     ▼
          Docker Container Build
   (Python 3.11-slim, Ingest Datasets, Gunicorn)
                     │
                     ▼
         Healthcheck at /healthz (200 OK)
                     │
                     ▼
        Live Production Web Service
   ward-water-quality-reporter.onrender.com
```

### Automated Render Deployment:
1. Fork or push to your GitHub account.
2. Sign in to [dashboard.render.com](https://dashboard.render.com/).
3. Click **New +** → **Blueprint** → Select `Water_Predict`.
4. Render automatically reads [`render.yaml`](./render.yaml), configures the container, verifies the `/healthz` endpoint, and deploys.

---

<a id="example-workflow"></a>
## 🧪 Example Workflow

1. **Sign In** — Open the portal and sign in with your credentials or click "Sign up" to create an account.
2. **Search Telemetry** — Select a District (e.g. *Coimbatore*), choose a Station (*Sulur*), and optionally specify an Urban Local Body ward.
3. **Inspect Sample Age** — Review the sample collection date; samples older than 365 days display a prominent amber *Historical* warning.
4. **Compare Standards** — Evaluate chemical parameters (pH, TDS, Nitrate, Fluoride) against BIS IS 10500:2012 thresholds.
5. **Draft Regulatory Report** — Generate an official report draft showing raw and normalized units with unverified ward matching disclaimers.
6. **Regulatory Approval** — An Environmental Officer reviews the draft and approves publication with a permanent timestamped audit log.
7. **Export Document** — Download the approved report as an official PDF or CSV data export.

---

<a id="user-interface--design-system"></a>
## 🖥️ User Interface & Design System

The platform features the **Revenlo SaaS Design System**:
- **Dark Mode & Light Mode**: Instant toggle in the top navigation bar with auto-saved preference.
- **Collapsible Sidebar**: Quick search bar, section navigation, and role status pill.
- **Split-Screen Authentication**: Untouched cosmic water visual on the left, paired with a clean white-theme login and registration form on the right.
- **Responsive Telemetry Cards**: Metric boxes, status gauges, and data tables that adapt smoothly from widescreen desktops to mobile devices.

---

<a id="core-components"></a>
## 🧩 Core Components

- **`app.py`** — Main Flask controller: handles routing, session management, REST API endpoints, search execution, and export routes.
- **`src/auth.py`** — User authentication engine: SQLite user management, salted PBKDF2 password hashing, and role verification.
- **`src/data_loader.py`** — Data ingestion engine: loads Cleaned CSV, Raw CSV, and ULB directory with dynamic column type identification.
- **`src/validation.py`** — Guardrail engine: validates district and station existence, parameter availability, and ward matching.
- **`src/date_utils.py`** — Temporal analysis engine: parses ISO dates and computes dynamic sample age against system time.
- **`src/normalization.py`** — Scientific unit normalization: converts mg/L ↔ µg/L while protecting dimensionless metrics.
- **`src/water_standards.py`** — Official water limits: stores BIS IS 10500:2012 and WHO permissible chemical boundaries.
- **`src/approval.py`** — Regulatory governance engine: manages draft creation, officer review, and SQLite audit logging.
- **`src/report_generator.py`** — Document builder: compiles report metadata and generates downloadable PDF reports.

---

<a id="security-considerations"></a>
## 🔐 Security Considerations

- **Salted Password Hashing**: Passwords are never stored in plaintext; hashed using PBKDF2-SHA256 with cryptographically secure salts.
- **SQL Injection Prevention**: All SQLite queries use parameterized SQL bindings (`?`).
- **No In-Memory Secret Commits**: Sensitive session secrets are configured through environment variables (`SECRET_KEY`).
- **Input Sanitization**: All user query inputs are stripped of leading/trailing whitespace and validated against official dataset profiles.

---

<a id="potential-municipal--industrial-applications"></a>
## 🏛️ Potential Municipal & Industrial Applications

- **Municipal Water Boards (TWAD / CMWSSB)** — Cross-referencing groundwater aquifer chemistry against municipal tap pipeline planning.
- **Environmental Protection Authorities** — Tracking industrial discharge impact on regional groundwater tables.
- **Public Health Departments** — Monitoring high-nitrate and high-fluoride zones to prevent fluorosis and waterborne illnesses.
- **Agricultural & Industrial Borewell Auditing** — Evaluating salinity (TDS & Electrical Conductivity) for irrigation and boiler feeds.
- **Academic & Hydrological Research** — Studying long-term chemical shifts in Tamil Nadu's subsurface aquifers.

---

<a id="advantages"></a>
## 🚀 Advantages

- **Zero Data Fabrication** — Absolute fidelity to official Central Ground Water Board records.
- **Historical Honesty** — Transparently warns users when samples are old (>365 days).
- **Spatial Accountability** — Clearly separates regional aquifer monitoring wells from municipal piped tap water.
- **Human Oversight** — Prevents automated publication of regulatory reports without officer review.
- **Turnkey Cloud Deployment** — Production-ready Docker container with instant Render deployment.

---

<a id="current-limitations"></a>
## ⚠️ Current Limitations

1. **Groundwater Only** — Data reflects monitoring wells, not municipal distribution tap pipes. Results cannot certify tap water potability.
2. **Periodic Sampling** — CGWB collects samples periodically (often annually or seasonally), not as a continuous real-time streaming feed.
3. **No Direct Ward Mapping in Source Data** — CGWB records specify districts and station villages, but do not contain official municipal ward boundary polygons.

---

<a id="future-improvements"></a>
## 🔮 Future Improvements

1. **Live TWAD API Integration** — Connect directly to Tamil Nadu Water Supply & Drainage Board real-time feeds.
2. **GIS Ward Polygon Mapping** — Incorporate GeoJSON ward boundary shapefiles for precise spatial station-to-ward intersecting.
3. **IoT Sensor Ingestion** — Support real-time telemetry from automated municipal sensor stations.
4. **Multi-Language Support (தமிழ்)** — Bilingual interface in English and Tamil for grassroots citizen accessibility.
5. **SMS & WhatsApp Alerts** — Automated community notifications when new water test reports are officially approved for a ward.

---

<a id="testing-strategy"></a>
## 🧪 Testing Strategy

The automated test suite in `tests/` contains **88 unit and integration tests** executing via Pytest:

```powershell
python -m pytest -v
```

### 📋 Test Coverage Breakdown:
- **`tests/test_auth.py` (9 tests)** — User registration, PBKDF2 hashing, role assignment, login session handling.
- **`tests/test_datasets_integration.py` (4 tests)** — Schema verification across all 3 integrated datasets.
- **`tests/test_dates.py` (18 tests)** — Dynamic sample age computation, leap years, historical sample labeling.
- **`tests/test_normalization.py` (12 tests)** — Unit conversions (mg/L ↔ µg/L), non-concentration unit protections.
- **`tests/test_scenarios.py` (19 tests)** — Hackathon verification scenarios:
  - **TC1**: Ward selection shows *Unverified Match* without false piped water claims.
  - **TC2**: Sample older than 365 days flagged with *Historical* label.
  - **TC3**: Unit normalization verified (`1 mg/L = 1000 µg/L`).
  - **TC4**: Missing ward displays explicit *No direct data found* notice.
- **`tests/test_validation.py` (26 tests)** — Column schema checks, whitespace trimming, input sanitation.

---

<a id="project-status"></a>
## 📌 Project Status

| Metric | Status |
|---|---|
| **Project Type** | Environmental Intelligence & Groundwater Governance Platform |
| **Dataset Source** | Central Ground Water Board (CGWB), Government of India |
| **Records Integrated** | 1,189 Cleaned Records • 1,223 Raw Records • 25 ULBs |
| **Framework** | Flask 3.0+ / Gunicorn WSGI |
| **Interface** | Revenlo SaaS (Dark & Light Modes) |
| **Test Suite** | 88 Passed Tests (100% Pass Rate) |
| **Live Deployment** | [ward-water-quality-reporter.onrender.com](https://ward-water-quality-reporter.onrender.com) |
| **Status** | Production Ready / Deployed Working Platform |

---

<a id="contributing"></a>
## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome:

1. **Fork the Repository**
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/environmental-enhancement
   ```
3. **Commit Your Changes**:
   ```bash
   git commit -m "feat: add GIS ward boundary intersection"
   ```
4. **Push to the Branch**:
   ```bash
   git push origin feature/environmental-enhancement
   ```
5. **Open a Pull Request**

---

<a id="license"></a>
## 📜 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Mowlieswaran G

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="disclaimer"></a>
## ⚠️ Disclaimer

WardWater is an environmental intelligence platform built for public transparency and institutional research. The groundwater measurements displayed reflect monitoring well samples analyzed by the Central Ground Water Board (CGWB) and do not represent certified municipal drinking-water tap pipeline connections.

Before making domestic, municipal, or industrial drinking water safety decisions, users should consult official municipal water testing laboratories or local public health authorities.

---

<a id="author"></a>
## 👨💻 Author

**Mowlieswaran G**

- **GitHub**: [@Mowlieswaran-G](https://github.com/Mowlieswaran-G)
- **Repository**: [Mowlieswaran-G/Water_Predict](https://github.com/Mowlieswaran-G/Water_Predict)
- **Live Deployment**: [ward-water-quality-reporter.onrender.com](https://ward-water-quality-reporter.onrender.com)

---

<a id="project-summary"></a>
## ⭐ Project Summary

WardWater bridges the critical divide between institutional scientific telemetry and accessible public governance. By uniting official **Central Ground Water Board (CGWB)** datasets, **automated scientific normalization**, **BIS/WHO health benchmarks**, and **human-in-the-loop regulatory approval** into a single cohesive SaaS platform, WardWater transforms complex groundwater chemistry into actionable, transparent environmental intelligence.