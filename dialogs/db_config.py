import sqlite3
from sqlite3 import Error


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    db_file = r"help_me_find.db"
    try:
        return sqlite3.connect(db_file)
    except Error as e:
        raise e


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        c.close()
    except Error as e:
        raise e


def main():
    sql_create_facility_table = """ CREATE TABLE IF NOT EXISTS facility_data (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        department text NOT NULL,
                                        section text,
                                        location text NOT NULL,
                                        details text NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection()

    # create tables
    with conn:
        # create projects table
        create_table(conn, sql_create_facility_table)
    conn.close()


main()
