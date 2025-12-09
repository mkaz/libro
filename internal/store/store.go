package store

import (
	"database/sql"
	"time"

	"github.com/mkaz/libro/internal/models"
)

type Store struct {
	DB *sql.DB
}

func New(db *sql.DB) *Store {
	return &Store{DB: db}
}

// Books

func (s *Store) AddBook(book *models.Book) (int64, error) {
	query := `INSERT INTO books (title, author, pub_year, pages, genre) VALUES (?, ?, ?, ?, ?)`
	res, err := s.DB.Exec(query, book.Title, book.Author, book.PubYear, book.Pages, book.Genre)
	if err != nil {
		return 0, err
	}
	return res.LastInsertId()
}

func (s *Store) GetBook(id int64) (*models.Book, error) {
	query := `SELECT id, title, author, pub_year, pages, genre FROM books WHERE id = ?`
	row := s.DB.QueryRow(query, id)
	var b models.Book
	if err := row.Scan(&b.ID, &b.Title, &b.Author, &b.PubYear, &b.Pages, &b.Genre); err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &b, nil
}

func (s *Store) GetRecentBooks(limit int) ([]models.Book, error) {
	query := `SELECT id, title, author, pub_year, pages, genre FROM books ORDER BY id DESC LIMIT ?`
	rows, err := s.DB.Query(query, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var books []models.Book
	for rows.Next() {
		var b models.Book
		if err := rows.Scan(&b.ID, &b.Title, &b.Author, &b.PubYear, &b.Pages, &b.Genre); err != nil {
			return nil, err
		}
		books = append(books, b)
	}
	return books, nil
}

func (s *Store) SearchBooks(query string) ([]models.Book, error) {
	q := "%" + query + "%"
	sqlQuery := `SELECT id, title, author, pub_year, pages, genre FROM books 
                 WHERE title LIKE ? OR author LIKE ? ORDER BY id DESC LIMIT 50`
	rows, err := s.DB.Query(sqlQuery, q, q)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var books []models.Book
	for rows.Next() {
		var b models.Book
		if err := rows.Scan(&b.ID, &b.Title, &b.Author, &b.PubYear, &b.Pages, &b.Genre); err != nil {
			return nil, err
		}
		books = append(books, b)
	}
	return books, nil
}

func (s *Store) UpdateBook(book *models.Book) error {
	query := `UPDATE books SET title=?, author=?, pub_year=?, pages=?, genre=? WHERE id=?`
	_, err := s.DB.Exec(query, book.Title, book.Author, book.PubYear, book.Pages, book.Genre, book.ID)
	return err
}

// Reviews

func (s *Store) AddReview(review *models.Review) (int64, error) {
	query := `INSERT INTO reviews (book_id, date_read, rating, review) VALUES (?, ?, ?, ?)`
	res, err := s.DB.Exec(query, review.BookID, review.DateRead, review.Rating, review.Review)
	if err != nil {
		return 0, err
	}
	return res.LastInsertId()
}

func (s *Store) GetReview(id int64) (*models.BookReview, error) {
	query := `
        SELECT r.id, r.book_id, r.date_read, NULLIF(r.rating, ''), NULLIF(r.review, ''),
               b.title, b.author, NULLIF(b.pub_year, ''), NULLIF(b.pages, ''), NULLIF(b.genre, '')
        FROM reviews r
        JOIN books b ON r.book_id = b.id
        WHERE r.id = ?
    `
	row := s.DB.QueryRow(query, id)
	var br models.BookReview
	if err := row.Scan(&br.ReviewID, &br.BookID, &br.DateRead, &br.Rating, &br.ReviewText,
		&br.BookTitle, &br.BookAuthor, &br.BookPubYear, &br.BookPages, &br.BookGenre); err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &br, nil
}

func (s *Store) GetRecentReviews(limit int) ([]models.BookReview, error) {
	query := `
        SELECT r.id, r.book_id, r.date_read, NULLIF(r.rating, ''), NULLIF(r.review, ''),
               b.title, b.author, NULLIF(b.pub_year, ''), NULLIF(b.pages, ''), NULLIF(b.genre, '')
        FROM reviews r
        JOIN books b ON r.book_id = b.id
        ORDER BY r.date_read DESC, r.id DESC
        LIMIT ?
    `
	rows, err := s.DB.Query(query, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var reviews []models.BookReview
	for rows.Next() {
		var br models.BookReview
		if err := rows.Scan(&br.ReviewID, &br.BookID, &br.DateRead, &br.Rating, &br.ReviewText,
			&br.BookTitle, &br.BookAuthor, &br.BookPubYear, &br.BookPages, &br.BookGenre); err != nil {
			return nil, err
		}
		reviews = append(reviews, br)
	}
	return reviews, nil
}

func (s *Store) GetReviewsByYear(year int) ([]models.BookReview, error) {
	// Format year as string for LIKE query or use strftime
	// Assuming date_read is YYYY-MM-DD
	start := time.Date(year, 1, 1, 0, 0, 0, 0, time.UTC).Format("2006-01-02")
	end := time.Date(year, 12, 31, 23, 59, 59, 0, time.UTC).Format("2006-01-02")

	query := `
        SELECT r.id, r.book_id, r.date_read, NULLIF(r.rating, ''), NULLIF(r.review, ''),
               b.title, b.author, NULLIF(b.pub_year, ''), NULLIF(b.pages, ''), NULLIF(b.genre, '')
        FROM reviews r
        JOIN books b ON r.book_id = b.id
        WHERE r.date_read BETWEEN ? AND ?
        ORDER BY r.date_read ASC
    `
	rows, err := s.DB.Query(query, start, end)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var reviews []models.BookReview
	for rows.Next() {
		var br models.BookReview
		if err := rows.Scan(&br.ReviewID, &br.BookID, &br.DateRead, &br.Rating, &br.ReviewText,
			&br.BookTitle, &br.BookAuthor, &br.BookPubYear, &br.BookPages, &br.BookGenre); err != nil {
			return nil, err
		}
		reviews = append(reviews, br)
	}
	return reviews, nil
}

func (s *Store) GetAvailableYears() ([]int, error) {
	query := `
		SELECT DISTINCT strftime('%Y', date_read) as year
		FROM reviews
		WHERE date_read IS NOT NULL
		ORDER BY year DESC
	`
	rows, err := s.DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var years []int
	for rows.Next() {
		var yearStr string
		if err := rows.Scan(&yearStr); err != nil {
			return nil, err
		}
		year, _ := time.Parse("2006", yearStr)
		years = append(years, year.Year())
	}
	return years, nil
}

// Reading Lists

func (s *Store) GetLists() ([]models.ReadingList, error) {
	query := `SELECT id, name, description, created_date FROM reading_lists ORDER BY created_date DESC`
	rows, err := s.DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var lists []models.ReadingList
	for rows.Next() {
		var l models.ReadingList
		if err := rows.Scan(&l.ID, &l.Name, &l.Description, &l.CreatedDate); err != nil {
			return nil, err
		}
		lists = append(lists, l)
	}
	return lists, nil
}

func (s *Store) CreateList(list *models.ReadingList) (int64, error) {
	query := `INSERT INTO reading_lists (name, description, created_date) VALUES (?, ?, ?)`
	res, err := s.DB.Exec(query, list.Name, list.Description, list.CreatedDate)
	if err != nil {
		return 0, err
	}
	return res.LastInsertId()
}

func (s *Store) GetListBooks(listID int64) ([]models.ReadingListBookDetail, error) {
	query := `
        SELECT
            b.id as book_id,
            b.title,
            b.author,
            b.genre,
            b.pub_year,
            b.pages,
            rlb.added_date,
            rlb.priority,
            CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END as is_read,
            r.date_read,
            r.rating
        FROM reading_list_books rlb
        JOIN books b ON rlb.book_id = b.id
        LEFT JOIN reviews r ON b.id = r.book_id
        WHERE rlb.list_id = ?
        ORDER BY rlb.priority DESC, rlb.added_date ASC
    `
	rows, err := s.DB.Query(query, listID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var books []models.ReadingListBookDetail
	for rows.Next() {
		var b models.ReadingListBookDetail
		var isRead int
		if err := rows.Scan(&b.BookID, &b.Title, &b.Author, &b.Genre, &b.PubYear, &b.Pages,
			&b.AddedDate, &b.Priority, &isRead, &b.DateRead, &b.Rating); err != nil {
			return nil, err
		}
		b.IsRead = isRead == 1
		books = append(books, b)
	}
	return books, nil
}

func (s *Store) AddBookToList(listID, bookID int64) error {
	query := `INSERT INTO reading_list_books (list_id, book_id, added_date) VALUES (?, ?, date('now'))`
	_, err := s.DB.Exec(query, listID, bookID)
	return err
}

func (s *Store) RemoveBookFromList(listID, bookID int64) error {
	query := `DELETE FROM reading_list_books WHERE list_id = ? AND book_id = ?`
	_, err := s.DB.Exec(query, listID, bookID)
	return err
}

// SearchReviews searches for reviews by title or author, optionally filtered by year
func (s *Store) SearchReviews(query string, year int) ([]models.BookReview, error) {
	searchPattern := "%" + query + "%"

	var rows *sql.Rows
	var err error

	if year > 0 {
		// Search within a specific year
		start := time.Date(year, 1, 1, 0, 0, 0, 0, time.UTC).Format("2006-01-02")
		end := time.Date(year, 12, 31, 23, 59, 59, 0, time.UTC).Format("2006-01-02")

		querySQL := `
			SELECT r.id, r.book_id, r.date_read, NULLIF(r.rating, ''), NULLIF(r.review, ''),
				   b.title, b.author, NULLIF(b.pub_year, ''), NULLIF(b.pages, ''), NULLIF(b.genre, '')
			FROM reviews r
			JOIN books b ON r.book_id = b.id
			WHERE r.date_read BETWEEN ? AND ?
			  AND (b.title LIKE ? OR b.author LIKE ?)
			ORDER BY r.date_read DESC
		`
		rows, err = s.DB.Query(querySQL, start, end, searchPattern, searchPattern)
	} else {
		// Search all years
		querySQL := `
			SELECT r.id, r.book_id, r.date_read, NULLIF(r.rating, ''), NULLIF(r.review, ''),
				   b.title, b.author, NULLIF(b.pub_year, ''), NULLIF(b.pages, ''), NULLIF(b.genre, '')
			FROM reviews r
			JOIN books b ON r.book_id = b.id
			WHERE b.title LIKE ? OR b.author LIKE ?
			ORDER BY r.date_read DESC
		`
		rows, err = s.DB.Query(querySQL, searchPattern, searchPattern)
	}

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var reviews []models.BookReview
	for rows.Next() {
		var br models.BookReview
		if err := rows.Scan(&br.ReviewID, &br.BookID, &br.DateRead, &br.Rating, &br.ReviewText,
			&br.BookTitle, &br.BookAuthor, &br.BookPubYear, &br.BookPages, &br.BookGenre); err != nil {
			return nil, err
		}
		reviews = append(reviews, br)
	}
	return reviews, nil
}

// GetUniqueAuthors returns all unique authors from the books table
func (s *Store) GetUniqueAuthors() ([]string, error) {
	query := `SELECT DISTINCT author FROM books WHERE author IS NOT NULL AND author != '' ORDER BY author ASC`
	rows, err := s.DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var authors []string
	for rows.Next() {
		var author string
		if err := rows.Scan(&author); err != nil {
			return nil, err
		}
		authors = append(authors, author)
	}
	return authors, nil
}

// YearCount represents the count of books read in a year
type YearCount struct {
	Year  int
	Count int
}

// MonthCount represents the count of books read in a month
type MonthCount struct {
	Month int
	Count int
}

// GetYearlyCounts returns the count of books read per year
func (s *Store) GetYearlyCounts() ([]YearCount, error) {
	query := `
		SELECT strftime('%Y', date_read) as year, COUNT(*) as count
		FROM reviews
		WHERE date_read IS NOT NULL
		GROUP BY year
		ORDER BY year ASC
	`
	rows, err := s.DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var counts []YearCount
	for rows.Next() {
		var yearStr string
		var count int
		if err := rows.Scan(&yearStr, &count); err != nil {
			return nil, err
		}
		year, _ := time.Parse("2006", yearStr)
		counts = append(counts, YearCount{Year: year.Year(), Count: count})
	}
	return counts, nil
}

// GetMonthlyCounts returns the count of books read per month for a specific year
func (s *Store) GetMonthlyCounts(year int) ([]MonthCount, error) {
	start := time.Date(year, 1, 1, 0, 0, 0, 0, time.UTC).Format("2006-01-02")
	end := time.Date(year, 12, 31, 23, 59, 59, 0, time.UTC).Format("2006-01-02")

	query := `
		SELECT strftime('%m', date_read) as month, COUNT(*) as count
		FROM reviews
		WHERE date_read BETWEEN ? AND ?
		GROUP BY month
		ORDER BY month ASC
	`
	rows, err := s.DB.Query(query, start, end)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var counts []MonthCount
	for rows.Next() {
		var monthStr string
		var count int
		if err := rows.Scan(&monthStr, &count); err != nil {
			return nil, err
		}
		month, _ := time.Parse("01", monthStr)
		counts = append(counts, MonthCount{Month: int(month.Month()), Count: count})
	}
	return counts, nil
}

// GetUniqueGenres returns all unique genres from the books table
func (s *Store) GetUniqueGenres() ([]string, error) {
	query := `SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL AND genre != '' ORDER BY genre ASC`
	rows, err := s.DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var genres []string
	for rows.Next() {
		var genre string
		if err := rows.Scan(&genre); err != nil {
			return nil, err
		}
		genres = append(genres, genre)
	}
	return genres, nil
}
