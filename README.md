# 💧 Ward Water Quality Reporter

> A transparent, honest groundwater quality search tool built for a college hackathon.
> Data source: Central Ground Water Board (CGWB), Tamil Nadu.

---

## 🔰 What This Project Does

The **Ward Water Quality Reporter** lets people look up groundwater quality records for
their area. It pulls data from an official cleaned CSV and shows exactly what measurements
exist, when they were taken, where they came from, and what is missing.

It **never invents** a measurement, date, ward link, or safety claim.

---

## 🚨 Problem It Solves

People often don't know:
- What water-quality data exists for their area.
- How old the data is.
- Whether a monitoring station is actually linked to their ward.
- What the data limitations are.

This tool shows all of that honestly, with source evidence and human approval before any
report is published.

---

## 🛠️ Technology Used

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Application core logic & data science |
| Flask 3.0+ | Modern web framework & REST endpoints |
| Docker & Docker Compose | Containerization & production deployment |
| Gunicorn | Production WSGI HTTP server |
| Pandas | CSV loading and high-performance data processing |
| SQLite | Storing report approval history |
| Pytest | Automated test suite (75 passed tests) |
| Plotly & Chart.js | Visual charts and water parameter trends |
| FPDF2 | Automated PDF report export |

---

## 📁 Folder Structure

```
Water_Predict/
├── app.py                  ← Flask web application entry point
├── Dockerfile              ← Production Docker container specification
├── docker-compose.yml      ← Container orchestration & volume mapping
├── .dockerignore           ← Container build exclusions
├── requirements.txt        ← Python package list
├── README.md               ← Documentation & guide
├── .gitignore
│
├── data/
│   └── tamil_nadu_groundwater_quality_cleaned.csv  ← Official CGWB dataset
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py       ← Load and inspect the CSV
│   ├── validation.py        ← Check columns, inputs, ward match
│   ├── filtering.py         ← Filter by district, station, date, parameter
│   ├── date_utils.py        ← Parse dates, label historical samples
│   ├── normalization.py     ← Convert mg/L ↔ µg/L
│   ├── source_verification.py ← Track provenance of every result
│   ├── analysis.py          ← Main search pipeline
│   ├── report_generator.py  ← Build draft reports & PDF generator
│   └── approval.py          ← SQLite-backed approval workflow
│
├── static/
│   ├── css/style.css        ← Modern responsive styling & design tokens
│   ├── js/app.js            ← Dynamic frontend filters, charts & search logic
│   └── img/                 ← Static images & assets
│
├── templates/
│   ├── base.html            ← Base layout with navigation and footer
│   ├── index.html           ← Search & live water quality exploration dashboard
│   ├── report.html          ← Draft report view & approval flow
│   ├── approvals.html       ← Approved report history & audit trail
│   └── about.html           ← Methodology, CGWB sources & honest limitations
│
├── tests/
│   ├── __init__.py
│   ├── test_validation.py   ← Column and input validation tests
│   ├── test_dates.py        ← Date parsing and historical label tests (TC2)
│   ├── test_normalization.py ← Unit conversion tests (TC3)
│   └── test_scenarios.py    ← TC1, TC2, TC3, TC4 integration tests
│
└── outputs/
    └── reports.db           ← Auto-created SQLite database
```

---

## ⚙️ How to Install Dependencies Locally

Open a terminal in the project folder and run:

```powershell
pip install -r requirements.txt
```

---

## ▶️ How to Start the Application

### Option A: Local Python Run

```powershell
python app.py
```

Then open your browser at: **http://localhost:5000**

---

### Option B: Docker Run (Production Container)

Make sure Docker Desktop is running, then execute:

```powershell
docker compose up --build
```

Or using standard Docker CLI:

```powershell
docker build -t ward-water-reporter .
docker run -p 5000:5000 ward-water-reporter
```

Then open your browser at: **http://localhost:5000**

> ⚠️ **You must place the CSV file first!**
> Copy your file to: `data/tamil_nadu_groundwater_quality_cleaned.csv`
> Then refresh the browser page.

---

## 🧪 How to Run the Tests

```powershell
pytest tests/ -v
```

Expected result: All tests pass ✅ (the tests that use the real CSV are separate
and require the file to be present).

---

## 📂 How the Data Is Loaded

1. `src/data_loader.py` reads the CSV from `data/`.
2. It strips whitespace from all string columns.
3. It inspects every column to find district, station, and date columns by name.
4. It identifies which columns have at least one numeric value (these become parameters).
5. It never invents rows — if the file is missing, an error is shown.

---

## 🔄 How Unit Conversion Works

- **1 mg/L = 1,000 µg/L** (milligrams per litre to micrograms per litre)
- **1 µg/L = 0.001 mg/L**
- pH and other non-concentration units are blocked from conversion.
- Unknown units are flagged: "Unit unknown — comparison unavailable."
- Both the original value+unit and the converted value+unit are always shown.
- Test fixtures are clearly marked `is_synthetic=True` and never shown as real data.

---

## 📅 How Historical Records Are Handled

- Sample age is calculated from the real system date (not hardcoded).
- Any sample older than **365 days** is labelled **"Historical"**.
- The exact collection date is always shown.
- If you search "Last 30 days" but only older records exist, you see:
  *"No samples were found within the selected period. Older records may be available."*

---

## 🔗 How Sources Are Verified

Every displayed result shows:
- **Dataset name**: Tamil Nadu Groundwater Quality (Cleaned CSV)
- **Official source**: Central Ground Water Board (CGWB) — India
- **Data type**: Groundwater chemistry from monitoring wells (NOT tap water)
- **Ward mapping**: No verified ward-to-station mapping exists in this dataset.
- If a URL or station ID exists in the CSV, it is shown. If not, that is stated clearly.

---

## ✅ How Human Approval Works

1. User runs a search.
2. Application finds real records and builds a **DRAFT** report.
3. Draft shows all warnings, source references, and limitations.
4. **A human must review and click Approve or Reject.**
5. Only after approval is the report marked "Approved for publication."
6. Approval is stored in SQLite with the reviewer's name and timestamp.
7. Reports are **never auto-published**.

---

## ⚠️ Dataset Limitations

| Limitation | Impact |
|------------|--------|
| Groundwater monitoring wells, not tap water | Results cannot certify drinking-water safety |
| No verified ward-to-station mapping | Ward matches are always "Unverified" |
| Year-level dates only (if no full date) | Cannot confirm samples are from a specific month |
| No individual lab report URLs | Cannot link to original lab PDF |
| Historical records only (older than 1 year) | "Last 30 days" will show no results |

---

## 🚀 What Would Be Needed for True Ward-Level Coverage

1. An official, regularly updated ward-to-monitoring-station mapping table.
2. Verified tap-water test results from municipal laboratories.
3. Full date-time stamps on each sample.
4. Individual lab report document links per sample.
5. Automated daily data ingestion pipeline.
6. State-level API integration with Tamil Nadu Water Supply & Drainage Board (TWAD).

---

## 🏆 Hackathon Presentation Outline

### 1. Problem Statement
People lack transparent access to water-quality data for their specific ward.
Official data exists but is not easily searchable or verifiable.

### 2. Proposed Solution
A local web app that honestly surfaces available groundwater records with full
source transparency, historical labelling, ward-match verification status, and
mandatory human approval before any report is published.

### 3. User Workflow
Search district → select station → enter ward (optional) → choose date period
→ choose parameters → get results → view source evidence → generate draft report
→ reviewer approves → download CSV.

### 4. System Architecture
CSV → Pandas → DatasetProfile → Search Pipeline → Flask Application & Responsive UI → SQLite Approval DB

### 5. Dataset and Limitations
CGWB Tamil Nadu groundwater chemistry dataset. No ward mapping. Groundwater only.
Not certified drinking-water results.

### 6. Four Test Cases
- **TC1**: Ward selected → Unverified match shown, never claimed as verified.
- **TC2**: Old sample → Labelled "Historical (collected N days ago)".
- **TC3**: 1 mg/L = 1000 µg/L after normalization (synthetic fixture).
- **TC4**: Missing ward → "No data found for this ward in the available dataset."

### 7. Safeguards
- Ward match always "Unverified" without official mapping.
- Human must approve before publication.
- No auto-publication.
- No invented measurements.
- Synthetic test fixtures never shown as real data.

### 8. Future Improvements
- Tamil Nadu TWAD API integration for live tap-water data.
- Verified ward-station mapping database.
- SMS/email alerts for new sample results.
- Multi-language support (Tamil).
- Mobile-responsive design improvements.

---

*Built with honesty and transparency for the public good. 💧*
#   W a t e r _ P r e d i c t  
 #   W a t e r _ P r e d i c t  
 