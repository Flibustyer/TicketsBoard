import time
from datetime import datetime

from selenium.webdriver.common.by import By

from constants.incident import Incident
from constants.service_now import ServiceNowConstants
from pages.base import BasePage
from pages.utils import write_file
from tests import input_data


class ServiceNow(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.const = ServiceNowConstants
        self.incident_const = Incident
        self.query = input_data.query

    def type_of_incident(self, incident):
        """Defining type of Incident and returning its xpath"""
        if incident.startswith('RITM'):
            assign_to_xpath = self.const.SERVICE_REQUEST_ASSIGN_FOR_XPATH
        else:
            assign_to_xpath = self.const.INCIDENT_ASSIGN_FOR_XPATH
        return assign_to_xpath

    def check_exist_owner(self):
        """Checking if the system has previous Incident owner"""
        existing_owner = ''
        try:
            if self.is_element_exist(xpath=self.const.INCIDENT_PREVIOUS_OWNER):
                previous_owner = self.driver.find_elements(by=By.XPATH, value=self.const.INCIDENT_ASSIGN_TO_XPATH)
                if previous_owner:
                    for item in previous_owner:
                        if item.text.startswith('Assigned to'):
                            owner = item.text.split('\n')[1]
                            for employee in ServiceNowConstants.employees:
                                if employee == owner:
                                    existing_owner = employee
            return existing_owner
        except (Exception, BaseExceptionGroup) as ex:
            write_file("check_exist_owner() Exception = ", ex)

    def assign_to(self, incident_type_owner_xpath, owner):
        """Assigning Incident owner according incoming values"""
        try:
            self.fill_field(xpath=incident_type_owner_xpath, value=owner)
            # self.click(xpath=self.const.SUPPORT_GROUP_INPUT_XPATH)
            value = self.get_element_value(xpath=incident_type_owner_xpath)
            if value == owner:
                self.move_mouse_on_element(xpath=self.const.UPDATE_BUTTON_XPATH)
                self.click(xpath=self.const.UPDATE_BUTTON_XPATH)
            else:
                write_file(f"try to insert {value} as owner")
        except (BaseException, Exception) as ex:
            write_file("assign_to() Exception = ", ex)

    def search_incident(self, incident):
        """Using search bar to open view with the new active ticket"""
        try:
            self.click(xpath=self.const.SEARCH_BUTTON_XPATH)
            self.fill_field_with_submit(xpath=self.const.SEARCH_FIELD_XPATH,
                                        value=incident[self.incident_const.INCIDENT_NUMBER])
        except (Exception, BaseExceptionGroup) as ex:
            write_file("search_incident() Exception = ", ex)

    def alert_handling(self, iframe, incident):
        """Handling possible alert window"""
        try:
            self.switch_to_alert(alert_accept_dismiss=False)
            self.driver.switch_to.frame(iframe)
            self.move_mouse_on_element(xpath=self.const.UPDATE_BUTTON_XPATH)
            self.click(xpath=self.const.UPDATE_BUTTON_XPATH)
            write_file(f'switch_to_alert, time = {str(datetime.now())}')
            time.sleep(2)
            self.driver.switch_to.default_content()
            self.search_incident(incident)
        except (BaseException, Exception):
            pass
