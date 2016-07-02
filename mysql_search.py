#!/usr/bin/env python3

# On Kali Linux get the pymysql library by installing python-pymysql
import pymysql

# User editable variables. Define the tables of interest (toi), the columns of
# interest (coi), the database connection time out, and the filename holding
# the mysql credentials in the format of host|user|pass|port.
#
# When editing the toi and coi tables keep in mind that auth will match all
# of the following:
# auth, authentication, authorization, user_auth, user_authentication
toi = ['auth', 'user', 'session']
coi = ['pass', 'ssn', 'usr', 'session', 'hash']
connect_timeout = 10
cred_file = 'mysql_creds.txt'


# Should not need to edit anything below this line.
def query(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    except pymysql.OperationalError as e:
        print('[-] {0}'.format(e[1]))
        return None

    except Exception as e:
        print('[-] {0}'.format(e))
        return None


def connect(host, user, pwd, db=None, port=3306):
    try:
        return pymysql.connect(host=host, user=user, password=pwd,
                               database=db, port=port,
                               connect_timeout=connect_timeout)

    except pymysql.OperationalError as e:
        print('[-] {0}'.format(e[1]))
        return None

    except Exception as e:
        print('[-] {0}'.format(str(e)))
        return None


def get_dbs(conn):
    if conn is not None:
        results = query(conn, 'show databases')

        if results is None:
            return []
        else:
            return [r[0] for r in results]

        conn.close()

    else:
        return []


def get_tables(conn):
    if conn is not None:
        results = query(conn, 'show tables')

        if results is None:
           return []
        else:
            return [r[0] for r in results]

    else:
        return []


def get_columns(conn, table):
    if conn is not None:
        sql = 'show columns from {0}'.format(table)
        results = query(conn, sql)

        if results is None:
            return []
        else:
            return [r[0] for r in results]

    else:
        return []


def get_creds(filename):
    for line in open(filename):
        line = line.strip('\r\n')
        host, user, pwd, port = line.split('|')
        yield host, user, pwd, int(port)


def interesting_table(db, table):
    for t in toi:
        if t in table:
            return (db, table)
        else:
            return None


def interesting_col(db, table, col):
    for c in coi:
        if c in col:
            return (db, table, col)
        else:
            return None


def search_db(host, user, pwd, port):
    conn = connect(host, user, pwd, port=port)
    dbs = get_dbs(conn)

    for db in dbs:
        print('[*] Searching database {0}'.format(db))
        of_interest = []
        conn = connect(host, user, pwd, port=port, db=db)
        tables = get_tables(conn)

        for table in tables:
            of_interest.append(interesting_table(db, table))

            cols = get_columns(conn, table)
            for col in cols:
                of_interest.append(interesting_col(db, table, col))

        conn.close()
        print_interesting(of_interest)


def print_interesting(of_interest):
    for i in of_interest:
        if i is not None:
            print('[+] {0}'.format('->'.join(i)))


#-----------------------------------------------------------------------------
# Begin Main Program
#-----------------------------------------------------------------------------
for creds in get_creds(cred_file):
    host, user, pwd, port = creds
    print('[*] Searching {0} on port {1}'.format(host, port))
    search_db(host, user, pwd, port)
