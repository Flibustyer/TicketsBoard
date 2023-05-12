import os.path
import sqlite3

from pages.utils import generate_db_id, write_file


def create_db(name_db):
    try:
        with sqlite3.connect(name_db) as db:
            cursor = db.cursor()
            cursor.execute('''CREATE TABLE incidents
                     (ID STRING PRIMARY KEY  NOT NULL,
                     INCIDENT_NUMBER STRING  NOT NULL,
                     INCIDENT_DATE  DATE      NOT NULL,
                     ASSIGN_TO STRING)
                     ''')
    except (Exception, BaseExceptionGroup) as ex:
        write_file("DataBase hasn't been created", ex)


def store_data(incident, timedate, user):
    """Storing the data in SQLite3 DataBase"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "incidents.db")

        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()

            db_id = generate_db_id()

            cursor.execute(f'''
                insert into incidents (id, incident_number, incident_date, assign_to) values (
                "{db_id}", "{incident}", "{timedate}", "{user}")         
            ''')
            db.commit()
    except (Exception, BaseException) as ex:
        write_file("DataBase store error, store_data(), Exception =  ", ex)


def get_bd_data():
    """Getting the data from SQLite3 DataBase"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "incidents.db")
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()

            cursor.execute('''
                select incident_number, incident_date, assign_to from incidents
            ''')

            incidents_list = cursor.fetchall()
            return incidents_list
    except (Exception, BaseException) as ex:
        write_file("DataBase query error, get_bd_data(), Exception = ", ex)


def get_specify_bd_data(incident):
    """Getting the data from SQLite3 DataBase with variable"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "incidents.db")
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()

            cursor.execute("SELECT incident_number, incident_date, assign_to from incidents where incident_number=?",
                           (incident,))

            incidents = cursor.fetchone()
            return incidents
    except (Exception, BaseException) as ex:
        write_file("DataBase query error, get_specify_bd_data(incident), Exception = ", ex)
