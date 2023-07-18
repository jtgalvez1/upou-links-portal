import sqlite3
import math

from app import app

def db_execute(sql):
  try:
    data = []

    with sqlite3.connect(app.config['DB_PATH'] + 'main.db') as conn:
      conn.create_function('LOG', 1, math.log)
      cursor = conn.execute(sql)
      for row in cursor:
        data.append(row)

    conn.commit()
    return data
  except sqlite3.Error as e:
    conn.rollback()
    print(e)
    pass
  finally:
    conn.close()

def list_user_data():
    sql = "SELECT email, given_name, family_name, user_type FROM user"
    rows = db_execute(sql)
    # print(rows)

    users = []

    if rows != None:
        for row in rows:
            user = {
                'email'             : row[0],
                'given_name'        : row[1],
                'family_name'       : row[2],
                'user_type'         : row[3]
            }
            users.append(user)

    print(users)
    return users


def change_user_type(email, user_type):
    sql = f"UPDATE user set user_type = '{user_type}' where email = '{email}'"
    result = db_execute(sql)
    print("Result!")
    print(result)
    return result

def retrieve_user_types():
    sql = "SELECT * from user_types"
    result = db_execute(sql)
    return result
