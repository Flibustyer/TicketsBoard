from operator import itemgetter


from constants.incident import Incident
from constants.service_now import ServiceNowConstants
from pages.utils import incident_sr_view, write_file


def incidents_search(driver):
    """Checking "Incidents" and "Service request" views for active tickets"""
    incidents = []
    const = ServiceNowConstants

    try:
        incidents_form = incident_sr_view(driver, const.INCIDENTS_URL, const.INCIDENT_TABLE_XPATH, 'INC')
        s_request_from = incident_sr_view(driver, const.SERVICE_REQUEST_URL, const.SERVICE_REQUEST_TABLE_XPATH, 'RITM')
        incidents = incidents_form + s_request_from
        incidents_sorted = sorted(incidents, key=itemgetter(Incident.INCIDENT_TIME))
        return incidents_sorted
    except (Exception, BaseExceptionGroup) as ex:
        write_file("DataBase hasn't been created", ex)
    finally:
        return incidents
