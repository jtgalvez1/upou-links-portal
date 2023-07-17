DROP TABLE IF EXISTS user_type;
CREATE TABLE IF NOT EXISTS user_type (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL UNIQUE,
  created_at  datetime DEFAULT current_timestamp     
);

INSERT INTO user_type (name) VALUES ('open'),('student'),('employee'),('admin');

DROP TABLE IF EXISTS user;
CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL UNIQUE,
  given_name  TEXT NOT NULL,
  family_name TEXT NOT NULL,
  user_type   INTEGER,
  joined_at   datetime DEFAULT current_timestamp,
  updated_at  timestamp DEFAULT current_timestamp,
  FOREIGN KEY (user_type) REFERENCES user_type(id)
);

DROP TABLE IF EXISTS category;
CREATE TABLE IF NOT EXISTS category (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL UNIQUE,
  created_at  datetime DEFAULT current_timestamp
);

DROP TABLE IF EXISTS link;
CREATE TABLE IF NOT EXISTS link (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url         TEXT NOT NULL UNIQUE,
  title       TEXT NOT NULL,
  description TEXT,
  image       TEXT,
  added_by    INTEGER,
  created_at  datetime DEFAULT current_timestamp,
  updated_at  timestamp DEFAULT current_timestamp,
  FOREIGN KEY (added_by) REFERENCES user(id)
);

DROP TABLE IF EXISTS user_type_can_view_link;
CREATE TABLE IF NOT EXISTS user_type_can_view_link (
  user_type_id    INTEGER,
  link_id         INTEGER,
  created_at      datetime DEFAULT current_timestamp,
  FOREIGN KEY (user_type_id) REFERENCES user_type(id),
  FOREIGN KEY (link_id) REFERENCES link(id),
  UNIQUE (user_type_id, link_id)
);

DROP TABLE IF EXISTS link_has_category;
DROP TABLE IF EXISTS link_has_category;
CREATE TABLE IF NOT EXISTS link_has_category (
  link_id         INTEGER,
  category_id     INTEGER,
  created_at      datetime DEFAULT current_timestamp,
  FOREIGN KEY (link_id) REFERENCES link(id),
  FOREIGN KEY (category_id) REFERENCES category(id),
  UNIQUE (link_id, category_id)
);

DROP TABLE IF EXISTS user_bookmarks_link;
CREATE TABLE IF NOT EXISTS user_bookmarks_link (
  userid        TEXT NOT NULL,
  link_id       INTEGER NOT NULL,
  created_at    datetime DEFAULT current_timestamp,
  FOREIGN KEY (userid) REFERENCES user(id),
  FOREIGN KEY (link_id) REFERENCES link(id),
  UNIQUE (userid, link_id)
);

DROP TABLE IF EXISTS logs;
CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  userid        TEXT NOT NULL,
  description   TEXT,
  link_id       INTEGER,
  created_at    datetime DEFAULT current_timestamp,
  FOREIGN KEY (userid) REFERENCES user(id),
  FOREIGN KEY (link_id) REFERENCES link(id)
);