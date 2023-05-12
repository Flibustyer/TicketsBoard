import datetime
import time

from tests import input_data


class TestAssign:

    def test_assign(self, service_now_page):
        """Starting the assignment process
            Created loop is running the process every 20 seconds
            Limit values for the loop are the start and end times of work"""
        end_of_work = True
        while end_of_work:
            service_now_page.set_assign_to()
            time.sleep(10)
            if datetime.datetime.now() >= input_data.end_time:
                end_of_work = False
