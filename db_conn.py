import os
import psycopg2
import sqlite3
import logging
from config import DB_DIR
from config import DB_NAME
from config import DB_TABLE
from config import DB_TYPE
from config import DB_USER
from config import DB_PASSWORD
from config import DB_HOST
from config import DB_PORT

#----------------------------------------------------------------------------------------

# Get information about this script including name, launch path, etc.
# This allows script to be renamed or relocated to another directory
mypath = os.path.abspath(__file__)  # Find the full path of this python script
# get the path location only (excluding script name)
baseDir = mypath[0 : mypath.rfind("/") + 1]
# Do a quick check to see if the sqlite database directory path exists
DB_DIR_PATH = os.path.join(baseDir, DB_DIR)
if not os.path.exists(DB_DIR_PATH):  # Check if database directory exists
    os.makedirs(DB_DIR_PATH)  # make directory if Not Found

DB_CONN = {}
if DB_TYPE == "sqlite3":
    DB_CONN['path'] = os.path.join(DB_DIR_PATH, DB_NAME)  # Create path to db file

elif DB_TYPE == 'postgres':
    DB_CONN = {
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'port': DB_PORT,
            'host': DB_HOST
        }

else:
    print(f'Invalid DB_TYPE {DB_TYPE}')
    raise NameError

def db_connect(db_conn_dict):
    if DB_TYPE == "sqlite3":
        db_file = db_conn_dict.get('path')
        conn = sqlite3.connect(db_file, timeout=1)

    elif DB_TYPE == "postgres":
        conn = psycopg2.connect(**db_conn_dict)
        conn.autocommit = True

    else:
        logging.error("Failed: invalid DB_TYPE %s", DB_TYPE)
        return None

    return conn

# ------------------------------------------------------------------------------
def db_exists(db_conn_dict):
    """
    Determines if DB exists, creates it otherwise
    """

    # Determine if filename is in sqlite3 format
    if DB_TYPE == 'sqlite3':
        filename = db_conn_dict.get('path')

        if os.path.isfile(filename):
            if os.path.getsize(filename) < 100:  # SQLite database file header is 100 bytes
                size = os.path.getsize(filename)
                logging.error("%s %d is Less than 100 bytes", filename, size)
                return False
            with open(filename, "rb") as fd:
                header = fd.read(100)
                if header.startswith(b"SQLite format 3"):
                    logging.info("Success: File is sqlite3 Format %s", filename)
                    return True
                else:
                    logging.error("Failed: File NOT sqlite3 Header Format %s", filename)
                    return False
        else:
            logging.warning("File Not Found %s", filename)
            logging.info("Create sqlite3 database File %s", filename)
            try:
                conn = sqlite3.connect(filename)
            except sqlite3.Error as e:
                logging.error("Failed: Create Database %s.", filename)
                logging.error("Error Msg: %s", e)
                return False
            conn.commit()
            conn.close()
            logging.info(f"Success: Created sqlite3 Database %s", filename)
            return True

        # Determine if the database exists on postgres server, create it if not
    elif DB_TYPE == 'postgres':

        # Connect to the database
        dbname = db_conn_dict['dbname']
        server_conn = {k: v for k, v in db_conn_dict.items() if k != 'dbname'}
        conn = psycopg2.connect(**server_conn)
        conn.autocommit = True

        # Check if the database exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = '{dbname}')")

        # Get the result
        exists = cursor.fetchone()[0]

        if exists:
            conn.close()
            return True
        else:
            # Create the database
            cursor.execute(f"CREATE DATABASE {dbname}")
            conn.close()
            return True

# ------------------------------------------------------------------------------
def db_check(db_conn_dict):
    """
    Check if db_file is a sqlite3 file and connect if possible
    """
    if db_exists(db_conn_dict):
        try:
            conn = db_connect(db_conn_dict)

        except (sqlite3.Error, psycopg2.Error) as e:
            logging.error("Failed: %s Connect to DB", DB_TYPE)
            logging.error("Error Msg: %s", e)
            return None

    else:
        logging.error("Failed: Could not connect to DB")
        return None

    conn.commit()
    logging.info("Success: Connected to DB %s", DB_TYPE)
    return conn


# ------------------------------------------------------------------------------
def db_open(db_conn_dict):
    """
    Insert speed data into database table
    """
    try:
        db_conn = db_connect(db_conn_dict)
        cursor = db_conn.cursor()

    except (sqlite3.Error, psycopg2.Error) as e:
        logging.error("Failed: Connect to DB %s", DB_TYPE)
        logging.error("Error Msg: %s", e)
        return None

    sql_cmd = """create table if not exists {} (idx text primary key,
                 log_timestamp text,
                 camera text,
                 ave_speed real, speed_units text, image_path text,
                 image_w integer, image_h integer, image_bigger integer,
                 direction text, plugin_name text,
                 cx integer, cy integer,
                 mw integer, mh integer, m_area integer,
                 x_left integer, x_right integer,
                 y_upper integer, y_lower integer,
                 max_speed_over integer,
                 min_area integer, track_counter integer,
                 cal_obj_px integer, cal_obj_mm integer, status text, cam_location text)""".format(
        DB_TABLE
    )
    try:
        if DB_TYPE == 'sqlite3':
            db_conn.execute(sql_cmd)

        elif DB_TYPE == 'postgres':
            cursor.execute(sql_cmd)

        else:
            logging.error("Failed: To Create Table %s on DB_TYPE %s", DB_TABLE, DB_TYPE)
            return None

    except (sqlite3.Error, psycopg2.Error) as e:
        logging.error("Failed: To Create Table %s on %s DB", DB_TABLE, DB_TYPE)
        logging.error("Error Msg: %s", e)
        return None

    else:
        db_conn.commit()
    return db_conn

#----------------------------------------------------------------------------------------
def get_timestamp_substr(total_by):
    '''
    Convert hour, day or month string to required
    values for changing the log_timestamp to
    an appropriate substring value
    '''
    total_by = total_by.upper()
    if total_by == 'HOUR':
        timestamp_subst = '2, 13'
    elif total_by == 'DAY':
        timestamp_subst = '2, 10'
    elif total_by == 'MONTH':
        timestamp_subst = '2, 7'
    else:
        logging.info("total_by variable must be string. Valid values are hour, day, month")
        logging.warning("Defaulting to hour")
        timestamp_subst = '2, 13'
    return timestamp_subst

#----------------------------------------------------------------------------------------
def get_query_str(agg_type, total_by, days_prev, speed_over):
    ''' Create Sqlite3 Query to Get Totals for specified days previous and speeds over
    '''
    timestamp_subst = get_timestamp_substr(total_by)

    aggregation = {
        'count': 'COUNT(*) AS count_totals',
        'ave_speed': 'ROUND(CAST(AVG(ave_speed) AS NUMERIC), 1) AS speed_ave'
    }

    qstring = {
        'postgres': '''
    SELECT
        SUBSTRING(log_timestamp, %s) AS log_date,
        %s
    FROM
        %s
    WHERE
        ave_speed >= %s AND
        TO_DATE(SUBSTRING(log_timestamp FROM 2 FOR 11), 'YYYY-MM-DD') >= CURRENT_DATE - INTERVAL '%i days' AND
        TO_DATE(SUBSTRING(log_timestamp FROM 2 FOR 11), 'YYYY-MM-DD') <= CURRENT_DATE + INTERVAL '1 day'
    GROUP BY
        log_date;
    ''',

    'sqlite3': '''
    select
        substr(log_timestamp, %s) log_date,
        %s
    from %s
    where
        ave_speed >= %s and
        substr(log_timestamp, 2, 11) >= DATE('now', '-%i days')  and
        substr(log_timestamp, 2, 11) <= DATE('now', '+1 day')
    group by
        log_date
    '''
    }

    sql_query_by_count = (qstring[DB_TYPE] % (timestamp_subst, aggregation[agg_type], DB_TABLE, speed_over, int(days_prev)))

    return sql_query_by_count
