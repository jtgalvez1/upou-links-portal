import sqlite3
import csv
import json

def db_execute(sql):
  try:
    data = []

    with sqlite3.connect('main.db') as conn:
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

sql = 'SELECT id, name FROM user_type'
rows = db_execute(sql)
privacy_list = {}
for row in rows:
  privacy_list[row[1]] = row[0]

links = []
with open('./links.csv', 'r') as file:
  reader = csv.DictReader(file)
  for line in reader:
    if line.get('Do Not Add') == 'TRUE':
      continue
    # privacy = 'admin'
    # if line.get('For Faculty and Employees') == 'TRUE':
    #   privacy = 'employee'
    # if line.get('For Students') == 'TRUE':
    #   if privacy == 'employee':
    #     privacy = 'upou'
    #   else:
    #     privacy = 'student'
    # if line.get('Open for all') == 'TRUE':
    #   privacy = 'guest'
    privacy = []
    if line['For Admin'] == 'TRUE':
      privacy.append(privacy_list['admin'])
    if line['For Faculty and Employees'] == 'TRUE':
      privacy.append(privacy_list['employee'])
    if line['For Students'] == 'TRUE':
      privacy.append(privacy_list['student'])
    if line['Open for all'] == 'TRUE':
      privacy.append(privacy_list['guest'])
    link = {
      'url'     : line.get('URL'),
      'title'   : line.get('Title'),
      'privacy' : json.dumps(privacy)
    }
    links.append(link)

for link in links:
  conn = sqlite3.connect('main.db')
  cursor = conn.execute('INSERT INTO link (url, title) VALUES (?, ?)', (link['url'], link['title']))
  link_id = cursor.lastrowid
  conn.commit()
  conn.close()
  for privacy in link['privacy'].strip('][').split(', '):
    conn = sqlite3.connect('main.db')
    cursor = conn.execute('INSERT INTO privacy_settings (user_type_id, link_id) VALUES (?,?)', (privacy, link_id))
    conn.commit()
    conn.close()
  # sql = 'INSERT INTO link (url, title) VALUES ("{}","{}")'.format(link['url'], link['title'])
  # rows = db_execute(sql)
  
  # print(rows.lastrowid)