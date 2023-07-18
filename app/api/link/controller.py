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

def get_count(sql):
  sql = 'SELECT COUNT(*) FROM ({})'.format(sql)
  count = db_execute(sql)[0][0]
  return count

def list_links(privacy='open',category=None,column=None,value=None):
  sql = "SELECT url, title, description, id FROM link a"
  if category is not None and category.get('id') is not None:
    sql = sql + """
                JOIN link_has_category d
                ON a.id = d.link_id
                """
  if privacy != 'admin':
    sql = sql + """
                  JOIN user_type_can_view_link b
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
                  a.id NOT IN (SELECT e.link_id FROM link_has_category e)
                  """
  rows = db_execute(sql)

  links = []
  if rows is not None:
    for row in rows:
      link = {
        'url'         : row[0],
        'title'       : row[1],
        'description' : row[2] or 'None',
        'id'          : row[3]
      }
      links.append(link)

    for link in links:
      sql = "SELECT a.id, a.name FROM user_type a JOIN user_type_can_view_link b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_has_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links



def upsert_link(link):

  # TODO: empty image submit should not clear database

  # for key, value in link.items():
  #   # change_link_value(key, value)

  sql = """
          INSERT INTO link (url, title, description, image)
          VALUES ('{url}','{title}','{description}', '{image}')
          ON CONFLICT (url) DO UPDATE SET
          title = excluded.title,
          description = excluded.description,
          image = excluded.image
          WHERE url = '{url}'
        """.format(
          url = link['url'],
          title = link['title'],
          description = link['description'] or 'NULL',
          image = link.get('image', 'NULL')
        )
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

def update_link_privacy(privacy, url):
  sql = 'DELETE FROM user_type_can_view_link WHERE link_id IN (SELECT id FROM link WHERE url = "{}")'.format(url)
  db_execute(sql)
  sql = 'INSERT INTO user_type_can_view_link (user_type_id, link_id) VALUES( (4, (SELECT id FROM link WHERE url = "{}")))'.format(url)
  for user_type in privacy.split(','):
    sql = "INSERT INTO user_type_can_view_link (user_type_id, link_id) VALUES ('{}', (SELECT id FROM link WHERE url = '{}'))".format(user_type, url)
    db_execute(sql)
  return

def update_link_category(categories, url):
  sql = 'DELETE FROM link_has_category WHERE link_id IN (SELECT id FROM link WHERE url = "{}")'.format(url)
  db_execute(sql)
  for category in categories:
    sql = 'INSERT INTO link_has_category (link_id, category_id) VALUES((SELECT id FROM link WHERE url = "{}"), "{}")'.format(url, category)
    db_execute(sql)
  return

def get_link(column,value):
  sql = 'SELECT url, title, description FROM link WHERE {} = "{}"'.format(column, value)
  row = db_execute(sql)[0]

  link = {
    'url'         : row[0],
    'title'       : row[1],
    'description' : row[2]
  }

  return link



def get_category_id(category):
  sql = 'SELECT id FROM category WHERE name = "{}"'.format(category)
  data = db_execute(sql)
  if len(data) == 1:
    return data[0][0]
  return None
  
def upsert_category(category):
  sql = 'INSERT OR IGNORE INTO category (name) VALUES ("{}")'.format(category)
  db_execute(sql)
  return get_category_id(category)

def list_categories(privacy='open'):
  sql = """
        SELECT DISTINCT category.id, category.name
        FROM category
        INNER JOIN link_has_category ON category.id = link_has_category.category_id
        INNER JOIN link ON link_has_category.link_id = link.id
        INNER JOIN user_type_can_view_link ON link.id = user_type_can_view_link.link_id
        INNER JOIN user_type ON user_type_can_view_link.user_type_id = user_type.id
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



def links_by_category(category,privacy='open'):
  sql = """
SELECT url, title, description, a.id, image
FROM link a
JOIN user_type_can_view_link b
ON a.id = b.link_id
JOIN user_type c
ON b.user_type_id = c.id
WHERE 
c.name = '{}'
AND
a.id
{} IN (
  SELECT link_id
  FROM link_has_category d
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
      sql = "SELECT a.id, a.name FROM user_type a JOIN user_type_can_view_link b ON a.id = b.user_type_id WHERE b.link_id = '{}'".format(link['id'])
      rows = db_execute(sql)

      link['privacy'] = []
      for row in rows:
        link['privacy'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

      sql = 'SELECT a.id, a.name FROM category a JOIN link_has_category b ON a.id = b.category_id WHERE b.link_id = "{}"'.format(link['id'])
      rows = db_execute(sql)

      link['category'] = []
      for row in rows:
        link['category'].append({
          'id'      : row[0],
          'name'    : row[1]
        })

  return links