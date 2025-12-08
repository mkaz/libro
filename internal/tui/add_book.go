package tui

import (
	"database/sql"
	"errors"
	"strconv"
	"time"

	"github.com/charmbracelet/huh"
	"github.com/mkaz/libro/internal/models"
	"github.com/mkaz/libro/internal/store"
)

type BookForm struct {
	Title    string
	Author   string
	PubYear  string
	Pages    string
	Genre    string
	DateRead string
	Rating   string
	Review   string
}

func (f *BookForm) ToBook() *models.Book {
	b := &models.Book{
		Title:  f.Title,
		Author: f.Author,
	}

	if f.PubYear != "" {
		if y, err := strconv.ParseInt(f.PubYear, 10, 64); err == nil {
			b.PubYear = sql.NullInt64{Int64: y, Valid: true}
		}
	}

	if f.Pages != "" {
		if p, err := strconv.ParseInt(f.Pages, 10, 64); err == nil {
			b.Pages = sql.NullInt64{Int64: p, Valid: true}
		}
	}

	if f.Genre != "" {
		b.Genre = sql.NullString{String: f.Genre, Valid: true}
	}

	return b
}

func (f *BookForm) ToReview(bookID int64) *models.Review {
	r := &models.Review{
		BookID: bookID,
	}

	if f.DateRead != "" {
		r.DateRead = sql.NullString{String: f.DateRead, Valid: true}
	}

	if f.Rating != "" {
		if rating, err := strconv.ParseInt(f.Rating, 10, 64); err == nil {
			r.Rating = sql.NullInt64{Int64: rating, Valid: true}
		}
	}

	if f.Review != "" {
		r.Review = sql.NullString{String: f.Review, Valid: true}
	}

	return r
}

func (f *BookForm) HasReview() bool {
	return f.DateRead != "" || f.Rating != "" || f.Review != ""
}

func NewAddBookForm(form *BookForm, s *store.Store) *huh.Form {
	// Get autocomplete suggestions
	authors, _ := s.GetUniqueAuthors()
	genres, _ := s.GetUniqueGenres()

	return huh.NewForm(
		huh.NewGroup(
			huh.NewInput().
				Title("Title").
				Value(&form.Title).
				Validate(func(str string) error {
					if str == "" {
						return errors.New("title is required")
					}
					return nil
				}),

			huh.NewInput().
				Title("Author").
				Value(&form.Author).
				Suggestions(authors).
				Validate(func(str string) error {
					if str == "" {
						return errors.New("author is required")
					}
					return nil
				}),

			huh.NewInput().
				Title("Publication Year").
				Value(&form.PubYear).
				Validate(func(str string) error {
					if str == "" {
						return nil
					}
					year, err := strconv.Atoi(str)
					if err != nil {
						return errors.New("must be a number")
					}
					if year < 0 || year > time.Now().Year()+1 {
						return errors.New("invalid year")
					}
					return nil
				}),

			huh.NewInput().
				Title("Pages").
				Value(&form.Pages).
				Validate(func(str string) error {
					if str == "" {
						return nil
					}
					if _, err := strconv.Atoi(str); err != nil {
						return errors.New("must be a number")
					}
					return nil
				}),

			huh.NewInput().
				Title("Genre").
				Value(&form.Genre).
				Suggestions(genres),
		),
		huh.NewGroup(
			huh.NewNote().
				Title("Review (optional)").
				Description("Leave blank to add just the book"),

			huh.NewInput().
				Title("Date Read (YYYY-MM-DD)").
				Value(&form.DateRead).
				Placeholder(time.Now().Format("2006-01-02")).
				Validate(func(str string) error {
					if str == "" {
						return nil
					}
					_, err := time.Parse("2006-01-02", str)
					if err != nil {
						return errors.New("must be YYYY-MM-DD format")
					}
					return nil
				}),

			huh.NewInput().
				Title("Rating (0-5)").
				Value(&form.Rating).
				Validate(func(str string) error {
					if str == "" {
						return nil
					}
					rating, err := strconv.Atoi(str)
					if err != nil {
						return errors.New("must be a number")
					}
					if rating < 0 || rating > 5 {
						return errors.New("must be between 0 and 5")
					}
					return nil
				}),

			huh.NewText().
				Title("Review").
				Value(&form.Review).
				CharLimit(1000),
		),
	)
}
