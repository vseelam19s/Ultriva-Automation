# QA Automation Framework — Ultriva LMS

Automated test suite for https://engineering.ultrivalms.com/qals1011

## Project Structure

```
qa_automation/
├── config/
│   └── config.py            # URL, credentials, browser settings
├── pages/
│   ├── base_page.py         # Common Selenium helpers
│   ├── login_page.py        # Login page object
│   └── dashboard_page.py    # Dashboard page object
├── QASite/
│   ├── test_login.py        # TC-001 – TC-007  (Authentication)
│   ├── test_dashboard.py    # TC-101 – TC-107  (Dashboard UI)
│   └── test_navigation.py   # TC-201 – TC-205  (Navigation)
├── utils/
│   ├── driver_setup.py      # WebDriver factory (Chrome / Firefox / Edge)
│   └── excel_reporter.py    # Writes results to Excel with colour coding
├── reports/                 # Generated after each run
│   ├── test_results.xlsx
│   ├── report.html
│   └── screenshots/
├── conftest.py              # Pytest fixtures & hooks
├── pytest.ini               # Pytest configuration
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/vseelam19s/Ultriva-Automation.git
cd Ultriva-Automation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set secrets as environment variables (see `.env.example`); they are not stored in the repo:

```powershell
$env:TESTRAIL_API_KEY = "<your key>"
$env:TESTRAIL_EMAIL   = "<your email>"
$env:ULTRIVA_PASSWORD = "<test account password>"   # optional override
```

## Running Tests

```bash
# All tests
pytest

# Specific suite
pytest QASite/test_login.py
pytest QASite/test_dashboard.py
pytest QASite/test_navigation.py

# Headless (no browser window)
# Edit config/config.py and set HEADLESS = True
```

## Reports

After a run, open:
- `reports/test_results.xlsx`  — colour-coded Excel report (PASS=green, FAIL=red, SKIP=amber)
- `reports/report.html`        — pytest-html HTML report
- `reports/screenshots/`       — screenshots captured on each test

## Test Cases

| ID     | Name                                       | Module         |
|--------|--------------------------------------------|----------------|
| TC-001 | Login page loads with input fields         | Authentication |
| TC-002 | Valid login with buyeruser / Ultriva!23    | Authentication |
| TC-003 | Login rejected for invalid username        | Authentication |
| TC-004 | Login rejected for invalid password        | Authentication |
| TC-005 | Login rejected for empty credentials       | Authentication |
| TC-006 | Logout redirects back to login page        | Authentication |
| TC-007 | Login page has non-empty browser title     | Authentication |
| TC-101 | Dashboard loads after valid login          | Dashboard      |
| TC-102 | Navigation menu is present                 | Dashboard      |
| TC-103 | URL changes after login                    | Dashboard      |
| TC-104 | Page header is visible                     | Dashboard      |
| TC-105 | Menu items are populated                   | Dashboard      |
| TC-106 | Footer is present                          | Dashboard      |
| TC-107 | Dashboard browser title is non-empty       | Dashboard      |
| TC-201 | Browser back button does not crash         | Navigation     |
| TC-202 | Unauthenticated access redirects to login  | Navigation     |
| TC-203 | Session persists after page refresh        | Navigation     |
| TC-204 | All nav links have href attributes         | Navigation     |
| TC-205 | Invalid route shows 404/error page         | Navigation     |
