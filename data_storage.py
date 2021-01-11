import sqlite3
from sqlite3 import Error

def create_connection(db_filename):
    """
    Connect to database file.

    Parameters
    ----------
    db_filename : str
        name of database file if it in currently directory.
        Otherwise, enter path to file

    Returns
    -------
    conn : sqlite3 connection
        connection to db file

    """
    conn = None
    try:
        conn = sqlite3.connect(db_filename)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, query):
    """
    Create table in database.
    
    Parameters
    ----------
    conn : sqlit3 connection
        connection to SQL database
    query : str
        SQL statement to create table
    """
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)


def create_santorini_tables():
    """Create two SQL tables that will game information."""
    database = r"santorini.db"

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS games (
                                        id integer PRIMARY KEY,
                                        gray_player text NOT NULL,
                                        white_player text NOT NULL
                                    ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS turns (
                                    id integer PRIMARY KEY,
                                    game_id INTEGER NOT NULL,
                                    color text NOT NULL,
                                    turn integer NOT NULL,
                                    task text NOT NULL,
                                    x_coordinate integer NOT NULL,
                                    y_coordinate integer NOT NULL,
                                    level integer,
                                    FOREIGN KEY (game_id) REFERENCES games (id)
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)

        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")


def get_next_id(table):
    """
    Get next primary key id from table.
    
    Parameters
    ----------
    table : str
        table name to pull id from

    Returns
    -------
    int
        1 more than current max id. In other words,
        next id value that will get entered into table

    """
    conn = create_connection('santorini.db')
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM {}".format(table))
    try:
        return cur.fetchall()[0][0] + 1
    except TypeError:
        return 1    

def insert_row(table, values):
    """
    Insert row of data into table.

    Parameters
    ----------
    table : str
        table to insert values into
    values : tuple
        values to insert into table
    """
    conn = create_connection('santorini.db')
    cur = conn.cursor()
    sql = 'INSERT INTO {0} VALUES (?,?,?)'.format(table)
    cur.execute(sql, values)
    conn.commit()

def run_query(query_text, commit = False):
    """
    Get results by running a query.

    Parameters
    ----------
    query_test : str
        query to run

    Returns
    -------
    list of tuples
        results of query
    """
    conn = create_connection('santorini.db')
    cur = conn.cursor()
    cur.execute(query_text)
    if commit:
        conn.commit()
        return None
    else:
        return cur.fetchall()

def main():
    create_santorini_tables()
    insert_row('games', (get_next_id('games'),'test1','test2'))
    #run_query("DELETE FROM games;", True)
    data = run_query("SELECT gray_player FROM games")
    print(data)

main()