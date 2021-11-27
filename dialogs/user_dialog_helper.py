from data_models.help_data import HelpData
from dialogs.db_config import create_connection


def db_insert_data(help_data: HelpData):
    record = [help_data.department.value, help_data.section, help_data.location.value, help_data.details]
    sql = ''' INSERT INTO facility_data(department,section,location,details)
                  VALUES(?,?,?,?) '''
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute(sql, record)
        conn.commit()
    conn.close()


def db_get_data(department, section):
    sql = ''' SELECT * FROM facility_data WHERE department=? and section=?'''
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute(sql, [department, section])
        rows = cur.fetchall()
    conn.close()
    return rows
