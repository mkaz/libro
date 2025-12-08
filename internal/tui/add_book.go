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
	Title   string
	Author  string
	PubYear string
	Pages   string
	Genre   string
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
	)
}
