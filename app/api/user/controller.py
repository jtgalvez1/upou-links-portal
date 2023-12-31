import sqlite3
import math

from app import app

def db_execute(sql):
  data = []
  try:
    with sqlite3.connect(app.config['DB_PATH'] + 'main.db') as conn:
      conn.create_function('LOG', 1, math.log)
      cursor = conn.execute(sql)
      for row in cursor:
        data.append(row)

    conn.commit()
  except sqlite3.Error as e:
    conn.rollback()
    print(e)
  finally:
    conn.close()
  return data

# Function to list all users
def list_users(column,value):
  sql = "SELECT email, given_name, family_name, b.name as user_type, a.id as id FROM user a INNER JOIN user_type b ON a.user_type = b.id  WHERE {} = '{}'".format(column,value)
  rows = db_execute(sql)

  users = []
  if rows != None:
    for row in rows:
      user = {
        'email'             : row[0],
        'given_name'        : row[1],
        'family_name'       : row[2],
        'user_type'         : row[3],
        'id'                : row[4]
      }
      users.append(user)

  return users

# Function to list all user types
def list_user_types():
  sql = 'SELECT id, name FROM user_type ORDER BY name'
  rows = db_execute(sql)

  user_types = []
  for row in rows:
    user_types.append({
      'id'    : row[0],
      'name'  : row[1],
    })

  return user_types

# Function to get user data
def get_user_value(email,column):
  sql = 'SELECT {} FROM user WHERE email = "{}"'.format(column,email)
  data = db_execute(sql)
  if len(data) == 1:
    return data[0][0]
  return None

# Function to get users of a specific type
def get_user_type_id(user_type):
  sql = 'SELECT id FROM user_type WHERE name = "{}"'.format(user_type)
  data = db_execute(sql)
  if len(data) == 1:
    return data[0][0]
  return None

# Function to insert user into database
def upsert_user(user):
  user_type = get_user_type_id('guest')
  if user['email'].endswith('@up.edu.ph'):
    user_type = get_user_type_id('student')
  if user['email'].endswith('@upou.edu.ph'):
    user_type = get_user_type_id('employee')
  sql = """
INSERT INTO user (email,given_name,family_name,user_type)
VALUES ('{email}','{given_name}','{family_name}','{user_type}')
ON CONFLICT (email) DO UPDATE SET
given_name = excluded.given_name,
family_name = excluded.family_name,
user_type = excluded.user_type
WHERE email = '{email}'
        """.format(
          email = user['email'],
          given_name = user['given_name'],
          family_name = user['family_name'],
          user_type = user.get('user_type', user_type)
        )
  db_execute(sql)
  return list_users('email',user['email'])[0]

# Function to bookmark a link
def bookmark_link(userid,link_id):
  sql = f"""
SELECT COUNT(*) FROM user_bookmarks_link
WHERE
userid = '{userid}' AND
link_id = '{link_id}'
"""
  count = db_execute(sql)[0][0]

  action = 'fail'
  if count == 1:
    sql = f"""
DELETE FROM user_bookmarks_link
WHERE
userid = '{userid}' AND
link_id = '{link_id}'
          """
    action = 'remove'
  else:
    sql = f"""
INSERT INTO user_bookmarks_link (userid, link_id)
VALUES ('{userid}', '{link_id}')
          """
    action = 'add'
  db_execute(sql)

  return action

# Function to get bookmarks
def get_user_bookmarks(userid):
  sql = f"SELECT link_id FROM user_bookmarks_link WHERE userid = '{userid}'"
  rows = db_execute(sql)

  bookmarks = []
  for row in rows:
    bookmarks.append(row[0])


  return bookmarks

# Function to add new usertype
def add_user_type(usertypename):

  sql = f"INSERT INTO user_type (name) VALUES ('{usertypename}')"

  result = db_execute(sql)
  return result

#Function to log user movements
def log_activity(userid, action, link_id):
  ACTIONS = [
    'ADD',
    'EDIT',
    'REMOVE',
    'VISIT',
    'BOOKMARK',
  ]

  if action not in ACTIONS:
    # raise ValueError('action must be one of the following: "ADD", "EDIT", "REMOVE", "VISIT", "BOOKMARK"')
    return

  sql = f"INSERT INTO logs (userid, description, link_id) VALUES ('{userid}','{action}','{link_id}')"
  db_execute(sql)

  return

def delete_user(userid):
  sql = f"DELETE FROM user where email = '{userid}'"
  result = db_execute(sql)
  return result