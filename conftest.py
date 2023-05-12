import pytest as pytest

from pages.assign_process import AssignProcess
from pages.utils import create_driver


@pytest.fixture()
def driver():
    """Create selenium driver. We are not closing it,
        because we are working with permanent open Chrome window in a Debug mode"""
    driver = create_driver()
    yield driver
    # driver.close()


@pytest.fixture()
def service_now_page(driver):
    """Create start page object"""
    return AssignProcess(driver)
