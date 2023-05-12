import time
from datetime import datetime

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from constants.incident import Incident
from constants.service_now import ServiceNowConstants
from pages.incidents import incidents_search
from pages.service_now import ServiceNow
from pages.utils import wait_until_ok, define_owner, write_file
from skype import unassigned_ticket, post_message
from sql_lite import get_bd_data, store_data, get_specify_bd_data
from tests import input_data


class AssignProcess(ServiceNow):

    def __init__(self, driver, ):
        super().__init__(driver)
        self.const = ServiceNowConstants
        self.incident_const = Incident
        self.query = input_data.query
        self.waiter = WebDriverWait(driver=driver, timeout=5)

    @wait_until_ok(timeout=6, period=0.5)
    def set_assign_to(self, ):
        """Choosing Incident owner and assign him in a defined que,
        after that recording Incident in DataBase"""

        if datetime.now() >= input_data.start_time:
            incidents = incidents_search(self.driver)
            iframe = self.driver.find_element(by=By.XPATH, value=self.const.BODY_XPATH)

            for incident in incidents:
                incident_number = self.incident_const.INCIDENT_NUMBER
                incident_owner = self.incident_const.INCIDENT_OWNER
                incident_time = incident[self.incident_const.INCIDENT_TIME]
                incident_type_owner_xpath = self.type_of_incident(incident[incident_number])
                que_list = get_bd_data()
                if not get_specify_bd_data(incident[incident_number]):
                    self.search_incident(incident)
                    self.alert_handling(iframe, incident)
                    try:
                        self.driver.switch_to.frame(iframe)
                        if self.is_element_exist(xpath=incident_type_owner_xpath):
                            filled_incident_owner = self.get_element_value(xpath=incident_type_owner_xpath)
                            que_owner = define_owner(que_list=que_list, owners_que_list=self.query,
                                                     filled_owner=filled_incident_owner)
                            prev_owner = self.check_exist_owner()
                            if not filled_incident_owner and not prev_owner and unassigned_ticket(incident_time, input_data.start_time):
                                message = f'Шановні! Є непризначений інцидент: {incident[incident_number]}'
                                post_message(msg=message)
                            elif not filled_incident_owner:
                                if prev_owner:
                                    incident[incident_owner] = prev_owner
                                else:
                                    incident[incident_owner] = que_owner
                                    store_data(incident[incident_number], incident_time, incident[incident_owner])
                                self.assign_to(incident_type_owner_xpath, incident[incident_owner])
                                time.sleep(3)
                            elif filled_incident_owner == que_owner:
                                store_data(incident[incident_number], incident_time, filled_incident_owner)
                            else:
                                pass
                        self.driver.switch_to.default_content()
                    except (Exception, NoSuchElementException) as ex:
                        que_owner = define_owner(que_list=que_list, owners_que_list=self.query)
                        incident[incident_owner] = que_owner
                        store_data(incident[incident_number], incident_time, incident[incident_owner])
                        write_file('set_assign_to() if incident_type_owner_xpath do not exist', ex)
                else:
                    self.search_incident(incident)
                    self.driver.switch_to.frame(iframe)
                    try:
                        if self.is_element_exist(xpath=incident_type_owner_xpath):
                            filled_incident_owner = self.get_element_value(xpath=incident_type_owner_xpath)
                            if not filled_incident_owner:
                                incident_owner = get_specify_bd_data(incident[incident_number])[2]
                                self.assign_to(incident_type_owner_xpath, incident_owner)
                        self.driver.switch_to.default_content()
                    except (BaseException, Exception) as ex:
                        write_file('get_specify_bd_data() Block Else', ex)
