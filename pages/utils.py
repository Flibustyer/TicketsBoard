import asyncio
import datetime
import logging
import os.path
import time
import uuid
from functools import wraps

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from constants.base import BaseConstants
from constants.incident import Incident
from constants.service_now import ServiceNowConstants


def create_driver():
    """Create driver according to provided browser.
        In this case we are opening Chrome window in a Debug mode"""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(executable_path=BaseConstants.DRIVER_PATH_CHROME, chrome_options=chrome_options)
    driver.implicitly_wait(1)
    return driver


def wait_until_ok(timeout=5, period=0.25):
    """Retries function until ok (or 5 seconds)"""
    log = logging.getLogger("[WaitUntilOk]")

    def decorator(original_function):

        def wrapper(*args, **kwargs):
            end_time = datetime.datetime.now() + datetime.timedelta(
                seconds=timeout
            )
            while True:
                try:
                    return original_function(*args, **kwargs)
                except Exception as err:
                    log.warning(f"Catching : {err}")
                    if datetime.datetime.now() > end_time:
                        raise err
                    asyncio.sleep(period)

        return wrapper

    return decorator


def log_wrapper(func):
    """Add logs for method based on the docstring"""

    def wrapper(*args, **kwargs):
        log = logging.getLogger("[LogDecorator]")
        result = func(*args, **kwargs)
        # log.info(f"{func.__doc__}; Args: {args};")
        log.info(func.__doc__)
        return result

    return wrapper


def is_file_empty(file_name):
    """ Check if file is empty by reading first character in it"""
    # open ile in read mode
    with open(file_name, 'r') as read_obj:
        # read first character
        one_char = read_obj.read(1)
        # if not fetched then file is empty
        if one_char:
            return True
    return False


def define_owner(que_list, owners_que_list, filled_owner=''):
    """Defining owners que"""
    if que_list:
        try:
            x = que_list[-1][2]
            index = owners_que_list.index(x)
            if index == len(owners_que_list) - 1:
                return owners_que_list[0]
            else:
                return owners_que_list[index + 1]
        except (BaseException, Exception):
            try:
                if filled_owner:
                    index = owners_que_list.index(filled_owner)
                    return owners_que_list[index]
                return owners_que_list[0]
            except(BaseException, Exception) as ex:
                print('define_owner() Exception = ', ex)
    else:
        return owners_que_list[0]


def skip_on(exception, reason="Default reason"):
    """Func below is the real decorator and will receive the test function as param"""

    def decorator_func(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Try to run the test
                return f(*args, **kwargs)
            except exception:
                # If exception of given type happens
                # just swallow it and raise pytest.Skip with given reason
                pytest.skip(reason)

        return wrapper

    return decorator_func


def is_date(item):
    """
    Return whether the string can be interpreted as a date.

    """
    format_type = '%d.%m.%Y %H:%M:%S'
    try:
        res = bool(datetime.datetime.strptime(item, format_type))
    except ValueError:
        res = False
    return res


def generate_db_id():
    """Generate Id for SQLite data base"""
    uuid_str = str(uuid.uuid4()).split("-")[-1]
    return uuid_str


def incident_sr_view(driver, url, form_xpath, type_of_inc):
    """Getting incident numbers and incidents time from the view with active incidents"""
    incidents = []
    incident_info = {}
    const = ServiceNowConstants

    try:
        driver.get(url)
        time.sleep(3)
        iframe = driver.find_element(by=By.XPATH, value=const.BODY_XPATH)
        driver.switch_to.frame(iframe)
        incidents_page = driver.find_element(by=By.XPATH, value=form_xpath).text.split("\n")
        if incidents_page:
            iterate = 0
            for count, item in enumerate(incidents_page):
                if item.startswith('Select record for action:'):
                    index = item.find(type_of_inc)
                    incident_info[Incident.INCIDENT_NUMBER] = item[index:]
                    iterate = count + 1
                if count == iterate and is_date(item):
                    incident_info[Incident.INCIDENT_TIME] = datetime.datetime.strptime(item,
                                                                                       '%d.%m.%Y %H:%M:%S') - \
                                                            datetime.timedelta(hours=1)
                    incidents.append(incident_info)
                    incident_info = {}
        driver.switch_to.default_content()
    except (BaseException, Exception) as ex:
        write_file(f"incident_sr_view(), time = {str(datetime.datetime.now())},  Exception = ", ex)
    return incidents


def write_file(func_name, exception=''):
    """Write exceptions into incidents.txt file"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "incidents.txt")
        with open(file_path, 'a') as f:
            f.write(f'{func_name},Exception = {exception}')
            f.write('\n')
    except (BaseException, Exception) as ex:
        print("write_file() Exception =  ", ex)
