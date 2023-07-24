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

def add_announcement(announcement):
    sql = f"INSERT into announcements (name, description, image, ends_at) VALUES ('{announcement['name']}', '{announcement['description']}', '{announcement['image']}','{announcement['datetime']}')"
    result = db_execute(sql)
    return result

def get_announcements():
    sql = "SELECT name, description, created_at, ends_at, image, is_visible from announcements"
    rows = db_execute(sql)

    if rows != None:
        for row in rows:
            user = {
                'name'          : row[0],
                'description'   : row[1],
                'create_date'   : row[2],
                'end_date'      : row[3],
                'image'         : row[4],
                'visibility'    : row[5]
            }
            users.append(user)

    return users