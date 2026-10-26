import time
import pytest
from utils.driver_setup import get_driver
from utils.excel_reporter import ExcelReporter
from config.config import USERNAME, PASSWORD, TESTRAIL_ENABLED
from pages.login_page import LoginPage


# ── Session-scoped Excel reporter ────────────────────────────────────────────
@pytest.fixture(scope="session")
def reporter():
    rep = ExcelReporter()
    yield rep
    path = rep.save()
    print(f"\n[Report] Saved to: {path}")


# ── Per-test browser driver ───────────────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    drv = get_driver()
    yield drv
    drv.quit()


# ── Authenticated driver (logs in before test, logs out after) ────────────────
@pytest.fixture(scope="function")
def auth_driver(driver, reporter):
    login_page = LoginPage(driver)
    login_page.login(USERNAME, PASSWORD)
    yield driver
    try:
        login_page.logout()
    except Exception:
        pass


# ── Helper: record a result to Excel ─────────────────────────────────────────
@pytest.fixture(scope="function")
def record(reporter, request):
    """
    Usage inside a test:
        def test_foo(record):
            record.start()
            ...
            record.done("PASS")   # or "FAIL" / "SKIP"
    """
    class Recorder:
        def __init__(self):
            self._start = None
            self.test_id   = None
            self.name      = request.node.name
            self.module    = request.node.module.__name__
            self.error     = ""
            self.screenshot = ""

        def start(self, test_id=None):
            self._start   = time.time()
            self.test_id  = test_id

        def done(self, status="PASS"):
            duration = round(time.time() - (self._start or time.time()), 2)
            reporter.add_result(
                test_id    = self.test_id or self.name,
                test_name  = self.name,
                module     = self.module,
                status     = status,
                duration   = duration,
                error_msg  = self.error,
                screenshot = self.screenshot,
            )

    return Recorder()


# ── TestRail Integration ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def testrail():
    """
    Session-scoped TestRail client.

    Skips silently when TESTRAIL_ENABLED=False so tests still run locally
    without requiring TestRail credentials.

    Usage inside a test:
        def test_login(driver, testrail):
            run_id = testrail.get_or_create_run()
            # ... test body ...
            testrail.add_result(run_id, case_id=1001, status="passed")
    """
    if not TESTRAIL_ENABLED:
        yield None
        return

    from utils.testrail_client import TestRailClient
    client = TestRailClient()
    yield client


@pytest.fixture(scope="session")
def testrail_run(testrail):
    """
    Provides a TestRail run ID for the whole session.

    Automatically creates a run at session start (if TESTRAIL_AUTO_CREATE_RUN=True)
    and closes it at session end.

    Usage:
        def test_foo(driver, testrail, testrail_run):
            # testrail_run is the integer run ID
            testrail.add_result(testrail_run, case_id=2001, status="passed")
    """
    if testrail is None:
        yield None
        return

    run_id = testrail.get_or_create_run()
    yield run_id
    testrail.close_run(run_id)

