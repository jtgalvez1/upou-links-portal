import sqlite3
import math
import datetime

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

# Function to add announcements
def add_announcement(announcement):
    sql = f"INSERT into announcements (name, description, image, ends_at, link) VALUES ('{announcement['name']}', '{announcement['description']}', '{announcement['image']}','{announcement['datetime']}','{announcement['link']}')"
    result = db_execute(sql)
    return result

# Function to get all announcements
def get_announcements():
    sql = "SELECT name, description, created_at, ends_at, image, is_visible, id, link from announcements"
    rows = db_execute(sql)

    announcement_list = []

    if rows != None:
        for row in rows:
            ann = {
                'name'          : row[0],
                'description'   : row[1],
                'create_date'   : datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y'),
                'end_date'      : row[3],
                'image'         : row[4],
                'visibility'    : row[5],
                'id'            : row[6],
                'link'          : row[7],
            }
            announcement_list.append(ann)

    return announcement_list

# Function to get announcements to be displayed
def get_valid_announcements():
    announcements = get_announcements()
    
    result = []
    for annon in announcements:
      if(annon["visibility"]==1 and comparedate(annon["end_date"])):
        result.append(annon)
    return result

# Function to compare date from database
def comparedate(db):
    now = datetime.date.today()
    enddate = db.split("-")
    end = datetime.date(int(enddate[0]),int(enddate[1]),int(enddate[2]))
    result = end>=now
    return result

# Function to change visibility
def change_visibility(name, visibility):
    sql = f"UPDATE announcements set is_visible = {visibility} where name = '{name}'"
    result = db_execute(sql)
    return result

# Function to change date of ending of announcement
def change_enddate(name, date):
  sql = f"UPDATE announcements set ends_at = '{date}' where name = '{name}'"
  result = db_execute(sql)
  return result

# Function to change any column in table
def change_announcement_column_value(id,column,value):
  sql = f"UPDATE announcements SET {column} = '{value}' WHERE id = '{id}'"
  db_execute(sql)

  return

# Function to delete announcements
def delete_announcement(id):
  sql = f"DELETE FROM announcements WHERE id = '{id}'"
  db_execute(sql)
  return

def get_tutorial():

  data = []
  fp = open("app/api/announcements/tutorial.txt", "r")
  for i in range(int(fp.readline())):
    slide = {}
    slide["title"] = fp.readline()
    slide["description"] = fp.readline()
    slide["picture"] = fp.readline()
    data.append(slide)
  fp.close()

  return data