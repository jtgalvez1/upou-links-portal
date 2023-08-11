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

# Function to return all user data
def list_user_data():
    sql = "SELECT email, given_name, family_name, user_type FROM user"
    rows = db_execute(sql)

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

    return users

# Function to change user type
def change_user_type(email, user_type):
    sql = f"UPDATE user set user_type = '{user_type}' where email = '{email}'"
    result = db_execute(sql)
    return result

# Function to retrieve all user types
def retrieve_user_types():
    sql = "SELECT * from user_type"
    result = db_execute(sql)
    return result



def remove_link_category(categoryName):
  sql = f"DELETE FROM link_category WHERE category_id IN (SELECT id FROM category WHERE name = '{categoryName}')"
  db_execute(sql)

  sql = f"DELETE FROM category WHERE name = '{categoryName}'"
  db_execute(sql)

  return

def remove_user_type(userType):
  # sql = f"DELETE FROM link_category WHERE category_id IN (SELECT id FROM category WHERE name = '{userType}')"
  # db_execute(sql)

  sql = f"UPDATE user SET user_type = (SELECT id FROM user_type WHERE name = 'guest') WHERE user_type = (SELECT id FROM user_type WHERE name = '{userType}')"
  db_execute(sql)

  sql = f"DELETE FROM user_type WHERE name = '{userType}'"
  db_execute(sql)

  return