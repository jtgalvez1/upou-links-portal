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

# Function to get count of links
def get_count(sql):
  sql = 'SELECT COUNT(*) FROM ({})'.format(sql)
  count = db_execute(sql)[0][0]
  return count

# Function to list all links
def list_links(privacy='guest',category=None,column=None,value=None):
  sql = "SELECT url, title, description, id, image FROM link a"
  if category is not None and category.get('id') is not None:
    sql = sql + """
                JOIN link_category d
                ON a.id = d.link_id
                """
  if privacy != 'admin':
    sql = sql + """
                  JOIN privacy_settings b
                  ON a.id = b.link_id
                  WHERE a.{} LIKE '%{}%'
                  AND b.user_type_id IN (
                  SELECT id FROM user_type c
                  WHERE c.name = '{}'
                  )
                """.format(
                  column or 'title',
                  value or '',
                  privacy
                )
  if category is not None:
    if privacy != 'admin':
      sql = sql + ' AND '
    else:
      sql = sql + ' WHERE '
    if category.get('id') is not None:
      sql = sql + """
                  d.category_id = '{}'
                  """.format(category['id'])
    elif category.get('name') == 'Others':
      sql = sql + """
                  a.id NOT IN (SELECT e.link_id FROM link_category e)
                  """
  rows = db_execute(sql)

  links = []
  if rows is not None:
    for row in rows:
      link = {
        'url'         : row[0],
        'title'       : row[1],
        'description' : row[2] or 'None',
        'id'          : row[3],
        'image'       : row[4] or 'None',
      }
      links.append(link)

    for link in links:
      sql = "SELECT a.id, a.name FROM user_type a JOIN privacy_settings b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links


# Function to insert link
def upsert_link(link):
  sql = f"""
INSERT INTO link (url, title, description, image)
VALUES 
('{link['url']}',
CASE WHEN '{link['title']}' <> '' THEN '{link['title']}' 
ELSE (SELECT title FROM link WHERE url = '{link['url']}') END,
CASE WHEN '{link['description']}' <> '' THEN '{link['description']}' 
ELSE (SELECT description FROM link WHERE url = '{link['url']}') END,
CASE WHEN '{link['image']}' <> '' THEN '{link['image']}' 
ELSE (SELECT image FROM link WHERE url = '{link['url']}') END)
ON CONFLICT (url) DO UPDATE SET
title = CASE WHEN '{link['title']}' <> '' THEN '{link['title']}' 
ELSE (SELECT title FROM link WHERE url = '{link['url']}') END,
description = CASE WHEN '{link['description']}' <> '' THEN '{link['description']}' 
ELSE (SELECT description FROM link WHERE url = '{link['url']}') END,
image = CASE WHEN '{link['image']}' <> '' THEN '{link['image']}' 
ELSE (SELECT image FROM link WHERE url = '{link['url']}') END
WHERE url = '{link['url']}'
"""
  db_execute(sql)
  update_link_privacy(link['privacy'], link['url'])
  categories = []
  if link['category'] != '':
    categories = link['category'].split(',')
  if link['new_category'] is not None and link['new_category'] != '':
    for new_category in link['new_category'].split(','):
      categories.append(upsert_category(new_category.strip(' ')))
  update_link_category(categories, link['url'])

  return get_link('url',link['url'])

# Function to check if link exists
def does_link_exists(url):
  sql = f'SELECT COUNT(*) FROM link WHERE url = {url}'
  count = db_execute(sql)[0][0]
  if count == 1:
    return True
  return False

# Function to change column in link
def set_link_value(url,column,value):
  sql = f"UPDATE link SET {column} = '{value}' WHERE url = '{url}'"
  db_execute(sql)
  return

# Function to update the privacy level of a link
def update_link_privacy(privacy, url):
  sql = 'DELETE FROM privacy_settings WHERE link_id IN (SELECT id FROM link WHERE url = "{}")'.format(url)
  db_execute(sql)
  sql = 'INSERT INTO privacy_settings (user_type_id, link_id) VALUES( ((SELECT id FROM user_type WHERE name = "admin"), (SELECT id FROM link WHERE url = "{}")))'.format(url)
  for user_type in privacy.split(','):
    sql = "INSERT INTO privacy_settings (user_type_id, link_id) VALUES ('{}', (SELECT id FROM link WHERE url = '{}'))".format(user_type, url)
    db_execute(sql)
  return

# Function to change category of a link
def update_link_category(categories, url):
  sql = 'DELETE FROM link_category WHERE link_id IN (SELECT id FROM link WHERE url = "{}")'.format(url)
  db_execute(sql)
  for category in categories:
    sql = 'INSERT INTO link_category (link_id, category_id) VALUES((SELECT id FROM link WHERE url = "{}"), "{}")'.format(url, category)
    db_execute(sql)
  return

# Function to get a Link
def get_link(column,value):
  sql = 'SELECT url, title, description FROM link WHERE {} = "{}"'.format(column, value)
  row = db_execute(sql)[0]

  link = {
    'url'         : row[0],
    'title'       : row[1],
    'description' : row[2]
  }

  return link


# Function to get id of a category
def get_category_id(category):
  sql = 'SELECT id FROM category WHERE name = "{}"'.format(category)
  data = db_execute(sql)
  if len(data) == 1:
    return data[0][0]
  return None
  
# Function to insert category
def upsert_category(category):
  sql = 'INSERT OR IGNORE INTO category (name) VALUES ("{}")'.format(category)
  db_execute(sql)
  return get_category_id(category)

# Function to list all categories
def list_categories(privacy='guest'):
  sql = """
        SELECT DISTINCT category.id, category.name
        FROM category
        INNER JOIN link_category ON category.id = link_category.category_id
        INNER JOIN link ON link_category.link_id = link.id
        INNER JOIN privacy_settings ON link.id = privacy_settings.link_id
        INNER JOIN user_type ON privacy_settings.user_type_id = user_type.id
        WHERE user_type.name = '{}'
        ORDER BY category.name;
        """.format(privacy)

  rows = db_execute(sql)
  categories = []

  if(rows != None):
    for row in rows:
      categories.append({
        'id'      : row[0],
        'name'    : row[1]
      })
    categories.append({
      'name'      : 'Others'
    })

  return categories


# Function to get links by category
def links_by_category(category,privacy='guest'):
  sql = """
SELECT url, title, description, a.id, image
FROM link a
JOIN privacy_settings b
ON a.id = b.link_id
JOIN user_type c
ON b.user_type_id = c.id
WHERE 
c.name = '{}'
AND
a.id
{} IN (
  SELECT link_id
  FROM link_category d
        """.format(privacy, 'NOT' if category['name'] == 'Others' else '')
  if category['name'] != 'Others':
    sql = sql + " WHERE d.category_id == '{}'".format(category['id'])
  sql = sql + ")"
    
  rows = db_execute(sql)

  links = []
  if rows is not None:
    for row in rows:
      link = {
        'url'         : row[0],
        'title'       : row[1],
        'description' : row[2] or 'None',
        'id'          : row[3],
        'image'       : row[4] or 'None',
      }
      links.append(link)

    for link in links:
      sql = "SELECT a.id, a.name FROM user_type a JOIN privacy_settings b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links

# Function to remove/delete a link
def remove_link_from_db(link_id):
  sql = f"DELETE FROM link_category WHERE link_id = '{link_id}'"
  db_execute(sql)

  sql = f"DELETE FROM privacy_settings WHERE link_id = '{link_id}'"
  db_execute(sql)

  sql = f"DELETE FROM link WHERE id = '{link_id}'"
  db_execute(sql)

  return

# Function to return bookmarked links
def list_bookmark_links(userid):
  sql = f"""
SELECT link.id, link.url, link.title, link.description, link.image
FROM link
INNER JOIN user_bookmarks_link ON link.id = user_bookmarks_link.link_id
INNER JOIN user ON user_bookmarks_link.userid = user.id
INNER JOIN privacy_settings ON user.user_type = privacy_settings.user_type_id AND link.id = privacy_settings.link_id
WHERE user.id = '{userid}';
"""
  rows = db_execute(sql)

  links = []
  for row in rows:
    links.append({
      'id'          : row[0],
      'url'         : row[1],
      'title'       : row[2],
      'description' : row[3] or 'None',
      'image'       : row[4] or 'None',
    })

    for link in links:
      sql = "SELECT a.id, a.name FROM user_type a JOIN privacy_settings b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links

# Function to get recently visited links
def list_recently_visited_links(userid):
  sql = f"""
SELECT id, url, title, description, image
FROM link a
WHERE a.id IN (
  SELECT link_id 
  FROM logs b
  WHERE userid = '{userid}'
  AND description = 'VISIT'
  ORDER BY b.created_at
  DESC LIMIT 6
) AND a.id IN (
  SELECT c.link_id
  FROM privacy_settings c
  JOIN user d
  ON c.user_type_id = d.user_type
  WHERE d.id = '{userid}'
)
        """
  rows = db_execute(sql)

  links = []
  if rows and len(rows) > 0:
    for row in rows:
      links.append({
        'id'          : row[0],
        'url'         : row[1],
        'title'       : row[2],
        'description' : row[3] or 'None',
        'image'       : row[4] or 'None',
      })

    for link in links:
      sql = "SELECT a.id, a.name FROM user_type a JOIN privacy_settings b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links

# Function to list trending links
def list_trending_links(privacy):
  sql = f"""
SELECT id, url, title, description, image
FROM link a
WHERE a.id IN (
  SELECT link_id 
  FROM logs b
  WHERE description = 'VISIT'
  ORDER BY b.created_at
  DESC LIMIT 6
) AND a.id IN (
  SELECT link_id
  FROM privacy_settings c
  JOIN user_type d
  ON c.user_type_id = d.id
  WHERE d.name = '{privacy}'
)
        """
  rows = db_execute(sql)

  links = []
  if rows and len(rows) > 0:
    for row in rows:
      links.append({
        'id'          : row[0],
        'url'         : row[1],
        'title'       : row[2],
        'description' : row[3] or 'None',
        'image'       : row[4] or 'None',
      })

    for link in links:
      sql = "SELECT a.id, a.name FROM user_type a JOIN privacy_settings b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links

# Function to list all categories
def list_all_categories():
  sql = "SELECT id, name FROM category"
  rows = db_execute(sql)

  categories = []
  for row in rows:
     categories.append({
        'id'      : row[0],
        'name'    : row[1],
     })

  return categories