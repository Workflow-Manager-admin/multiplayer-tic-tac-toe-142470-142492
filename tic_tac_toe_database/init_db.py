#!/usr/bin/env python3
"""Initialize SQLite database for tic_tac_toe_database: Users, Games, Moves, Sessions."""

import sqlite3
import os

DB_NAME = "myapp.db"

print("Starting Tic Tac Toe SQLite database setup...")

db_exists = os.path.exists(DB_NAME)
if db_exists:
    print(f"SQLite database already exists at {DB_NAME}")
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("SELECT 1")
        conn.close()
        print("Database is accessible and working.")
    except Exception as e:
        print(f"Warning: Database exists but may be corrupted: {e}")
else:
    print("Creating new SQLite database...")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Ensure foreign key support
cursor.execute("PRAGMA foreign_keys = ON;")

# ---- USERS TABLE ----
# Holds unique user accounts
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---- GAMES TABLE ----
# Each game can have two players. player_x_id and player_o_id reference users.
cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_x_id INTEGER NOT NULL,
    player_o_id INTEGER,
    current_turn TEXT NOT NULL CHECK(current_turn IN ('X', 'O')),
    state TEXT NOT NULL CHECK(state IN ('waiting', 'in_progress', 'finished')),
    winner TEXT CHECK(winner IN ('X', 'O', 'draw', NULL)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    FOREIGN KEY(player_x_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(player_o_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# ---- MOVES TABLE ----
# Each row represents a board move
cursor.execute("""
CREATE TABLE IF NOT EXISTS moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    move_number INTEGER NOT NULL,
    x INTEGER NOT NULL CHECK(x >= 0 AND x < 3),
    y INTEGER NOT NULL CHECK(y >= 0 AND y < 3),
    mark TEXT NOT NULL CHECK(mark IN ('X', 'O')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY(player_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(game_id, x, y)      -- Only one move per cell per game
)
""")

# ---- SESSIONS TABLE ----
# Links active user sessions to user IDs (for authentication)
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# ---- Indexes for Fast Lookups ----
cursor.execute("""CREATE INDEX IF NOT EXISTS idx_moves_game_id ON moves(game_id);""")
cursor.execute("""CREATE INDEX IF NOT EXISTS idx_games_state ON games(state);""")
cursor.execute("""CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);""")

# ---- App Info Table ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS app_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---- Initial Data ----
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("project_name", "tic_tac_toe_database"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("version", "1.0.0"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("author", "Kavia Generated"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("description", "Schema for Tic Tac Toe game with users, games, moves, and sessions tables."))

conn.commit()

# Summary statistics
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
table_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM app_info")
record_count = cursor.fetchone()[0]
conn.close()

# Save connection info to a file
current_dir = os.getcwd()
connection_string = f"sqlite:///{current_dir}/{DB_NAME}"
try:
    with open("db_connection.txt", "w") as f:
        f.write(f"# SQLite connection methods:\n")
        f.write(f"# Python: sqlite3.connect('{DB_NAME}')\n")
        f.write(f"# Connection string: {connection_string}\n")
        f.write(f"# File path: {current_dir}/{DB_NAME}\n")
    print("Connection information saved to db_connection.txt")
except Exception as e:
    print(f"Warning: Could not save connection info: {e}")

# Create environment variable file for Node.js viewer
db_path = os.path.abspath(DB_NAME)
if not os.path.exists("db_visualizer"):
    os.makedirs("db_visualizer", exist_ok=True)
    print("Created db_visualizer directory")
try:
    with open("db_visualizer/sqlite.env", "w") as f:
        f.write(f"export SQLITE_DB=\"{db_path}\"\n")
    print(f"Environment variables saved to db_visualizer/sqlite.env")
except Exception as e:
    print(f"Warning: Could not save environment variables: {e}")

print("\nSQLite setup complete!")
print(f"Database: {DB_NAME}")
print(f"Location: {current_dir}/{DB_NAME}\n")
print("To use with Node.js viewer, run: source db_visualizer/sqlite.env")

print("\nTo connect to the database, use one of the following methods:")
print(f"1. Python: sqlite3.connect('{DB_NAME}')")
print(f"2. Connection string: {connection_string}")
print(f"3. Direct file access: {current_dir}/{DB_NAME}\n")
print("Database statistics:")
print(f"  Tables: {table_count}")
print(f"  App info records: {record_count}")

# Check for sqlite3 CLI
try:
    import subprocess
    result = subprocess.run(['which', 'sqlite3'], capture_output=True, text=True)
    if result.returncode == 0:
        print("")
        print("SQLite CLI is available. You can also use:")
        print(f"  sqlite3 {DB_NAME}")
except Exception:
    pass

print("\nScript completed successfully.")
