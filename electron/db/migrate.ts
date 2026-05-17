import type Database from 'better-sqlite3'

export function migrateDatabase(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS books (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      author TEXT NOT NULL,
      pub_year INTEGER,
      pages INTEGER,
      genre TEXT
    );

    CREATE TABLE IF NOT EXISTS reviews (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      book_id INTEGER,
      date_read DATE,
      rating INTEGER,
      review TEXT,
      FOREIGN KEY (book_id) REFERENCES books(id)
    );

    CREATE TABLE IF NOT EXISTS reading_lists (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      description TEXT,
      created_date DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS reading_list_books (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      list_id INTEGER NOT NULL,
      book_id INTEGER NOT NULL,
      added_date DATE DEFAULT CURRENT_DATE,
      priority INTEGER DEFAULT 0,
      FOREIGN KEY (list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
      FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
      UNIQUE(list_id, book_id)
    );
  `)
}
