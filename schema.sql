DROP TABLE IF EXISTS activity_logs;

CREATE TABLE activity_logs (
  action CHAR(6) NOT NULL DEFAULT 'update',
  item_type VARCHAR,
  item_id INTEGER NOT NULL,
  act_action TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

DROP TABLE IF EXISTS setter_types;

CREATE TABLE setter_types (
  --id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  name CHAR(32) NOT NULL DEFAULT 'Setter type',
  description TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

DROP TABLE IF EXISTS crossword_setters;

CREATE TABLE crossword_setters (
  --id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  name CHAR(32) NOT NULL DEFAULT 'Setter type',
  setter_type_id INTEGER,
  created_at DATETIME,
  updated_at DATETIME
);

DROP TABLE IF EXISTS solution_types;

CREATE TABLE solution_types (
  --id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  name CHAR(32) NOT NULL DEFAULT 'Solution type',
  description TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

DROP TABLE IF EXISTS crossword_solutions;

CREATE TABLE crossword_solutions (
  --id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  setter_id INTEGER NOT NULL DEFAULT '1',
  clue VARCHAR(256) NOT NULL,
  solution VARCHAR(64) NOT NULL,
  solution_hint VARCHAR(64),
  solution_type_id INTEGER NOT NULL,
  created_at DATETIME,
  updated_at DATETIME
)
