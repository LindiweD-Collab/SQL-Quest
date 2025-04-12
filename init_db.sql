-- Drop existing tables if they exist
DROP TABLE IF EXISTS plants;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS caves;
DROP TABLE IF EXISTS artifacts;
DROP TABLE IF EXISTS villagers;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS actions;
DROP TABLE IF EXISTS levels;
DROP TABLE IF EXISTS players;


-- Plants table
CREATE TABLE plants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  is_edible BOOLEAN
);

INSERT INTO plants (name, is_edible) VALUES
  ('Coconut', 1),
  ('Poison Ivy', 0),
  ('Mango', 1),
  ('Red Mushroom', 0);

-- Inventory table
CREATE TABLE inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item TEXT,
  quantity INTEGER
);

DROP TABLE IF EXISTS players;

CREATE TABLE players (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  level INTEGER DEFAULT 1,
  score INTEGER DEFAULT 0,
  inventory TEXT,          
  actions TEXT,             
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Add an example player
INSERT INTO players (username, level, score, inventory, actions) VALUES
  ('PlayerOne', 1, 10, 'Wood:2,Stone:1', 'Collected Wood,Collected Stone');

-- Caves table
CREATE TABLE caves (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  danger_level INTEGER,
  discovered BOOLEAN
);

INSERT INTO caves (name, danger_level, discovered) VALUES
  ('Dark Hollow', 5, 0),
  ('Crystal Cove', 2, 0),
  ('Serpent''s Lair', 8, 0);


-- Artifacts table
CREATE TABLE artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  power_level INTEGER,
  cave_id INTEGER,
  FOREIGN KEY (cave_id) REFERENCES caves (id)
);

INSERT INTO artifacts (name, power_level, cave_id) VALUES
  ('Ancient Sword', 7, 1),
  ('Glowing Amulet', 5, 2),
  ('Crystal Orb', 9, 3);

-- Villagers table
CREATE TABLE villagers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  role TEXT,
  health INTEGER
);

INSERT INTO villagers (name, role, health) VALUES
  ('Kai', 'Hunter', 100),
  ('Lira', 'Healer', 90),
  ('Boro', 'Blacksmith', 110);

  CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  level INTEGER DEFAULT 1,
  score INTEGER DEFAULT 0
);

CREATE TABLE actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  action TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);



CREATE TABLE levels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  level_number INTEGER,
  description TEXT,
  goal_score INTEGER
);

INSERT INTO levels (level_number, description, goal_score) VALUES
  (1, 'Survive Day 1 on SQL Island', 50),
  (2, 'Explore the Caves', 100),
  (3, 'Defeat the Guardian', 200);


-- Create a trigger to update the health of villagers when they are injured
CREATE TRIGGER update_villager_health
AFTER UPDATE ON villagers
FOR EACH ROW
BEGIN
  UPDATE villagers
  SET health = CASE
    WHEN NEW.health < OLD.health THEN OLD.health - 10
    ELSE OLD.health
  END
  WHERE id = NEW.id;
END;