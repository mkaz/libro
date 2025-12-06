package models

import (
	"database/sql"
)

type Book struct {
	ID      int64          `db:"id"`
	Title   string         `db:"title"`
	Author  string         `db:"author"`
	PubYear sql.NullInt64  `db:"pub_year"`
	Pages   sql.NullInt64  `db:"pages"`
	Genre   sql.NullString `db:"genre"`
}

type Review struct {
	ID       int64          `db:"id"`
	BookID   int64          `db:"book_id"`
	DateRead sql.NullString `db:"date_read"` // YYYY-MM-DD
	Rating   sql.NullInt64  `db:"rating"`
	Review   sql.NullString `db:"review"`
}

type BookReview struct {
	// Combined fields
	BookID      int64          `db:"book_id"`
	BookTitle   string         `db:"title"`
	BookAuthor  string         `db:"author"`
	ReviewID    sql.NullInt64  `db:"review_id"`
	DateRead    sql.NullString `db:"date_read"`
	Rating      sql.NullInt64  `db:"rating"`
	ReviewText  sql.NullString `db:"review"`
	BookPubYear sql.NullInt64  `db:"pub_year"`
	BookPages   sql.NullInt64  `db:"pages"`
	BookGenre   sql.NullString `db:"genre"`
}

type ReadingList struct {
	ID          int64          `db:"id"`
	Name        string         `db:"name"`
	Description sql.NullString `db:"description"`
	CreatedDate sql.NullString `db:"created_date"`
}

type ReadingListBook struct {
	ID        int64          `db:"id"`
	ListID    int64          `db:"list_id"`
	BookID    int64          `db:"book_id"`
	AddedDate sql.NullString `db:"added_date"`
	Priority  int64          `db:"priority"`
}

type ReadingListBookDetail struct {
	BookID    int64          `db:"book_id"`
	Title     string         `db:"title"`
	Author    string         `db:"author"`
	Genre     sql.NullString `db:"genre"`
	PubYear   sql.NullInt64  `db:"pub_year"`
	Pages     sql.NullInt64  `db:"pages"`
	AddedDate sql.NullString `db:"added_date"`
	Priority  int64          `db:"priority"`
	IsRead    bool           `db:"is_read"`
	DateRead  sql.NullString `db:"date_read"`
	Rating    sql.NullInt64  `db:"rating"`
}
