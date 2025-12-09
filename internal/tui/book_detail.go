package tui

import (
	"fmt"
	"strconv"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/models"
)

type BookDetailModel struct {
	book models.BookReview
}

func NewBookDetail(book models.BookReview) BookDetailModel {
	return BookDetailModel{
		book: book,
	}
}

func (m BookDetailModel) View() string {
	var s string

	titleStyle := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("229"))
	labelStyle := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("246"))
	valueStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("255"))

	// Title and Author
	s += titleStyle.Render(m.book.BookTitle) + "\n"
	s += labelStyle.Render("by ") + valueStyle.Render(m.book.BookAuthor) + "\n\n"

	// Book Details
	if m.book.BookGenre.Valid && m.book.BookGenre.String != "" {
		s += labelStyle.Render("Genre: ") + valueStyle.Render(m.book.BookGenre.String) + "\n"
	}

	if m.book.BookPubYear.Valid {
		s += labelStyle.Render("Published: ") + valueStyle.Render(strconv.FormatInt(m.book.BookPubYear.Int64, 10)) + "\n"
	}

	if m.book.BookPages.Valid {
		s += labelStyle.Render("Pages: ") + valueStyle.Render(strconv.FormatInt(m.book.BookPages.Int64, 10)) + "\n"
	}

	// Review Details
	if m.book.ReviewID.Valid {
		s += "\n" + labelStyle.Render("Review") + "\n"
		s += lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Render("────────────────────────────────────────") + "\n"

		if m.book.DateRead.Valid {
			dateRead := m.book.DateRead.String
			// Try to parse and format nicely
			if parsed, err := time.Parse("2006-01-02T15:04:05Z07:00", dateRead); err == nil {
				dateRead = parsed.Format("January 2, 2006")
			}
			s += labelStyle.Render("Date Read: ") + valueStyle.Render(dateRead) + "\n"
		}

		if m.book.Rating.Valid {
			rating := m.book.Rating.Int64
			stars := ""
			for i := int64(0); i < rating; i++ {
				stars += "★"
			}
			for i := rating; i < 5; i++ {
				stars += "☆"
			}
			s += labelStyle.Render("Rating: ") + valueStyle.Render(fmt.Sprintf("%s (%d/5)", stars, rating)) + "\n"
		}

		if m.book.ReviewText.Valid && m.book.ReviewText.String != "" {
			s += "\n" + labelStyle.Render("Notes:") + "\n"
			// Wrap review text
			reviewStyle := lipgloss.NewStyle().Width(60).Foreground(lipgloss.Color("255"))
			s += reviewStyle.Render(m.book.ReviewText.String) + "\n"
		}
	} else {
		s += "\n" + lipgloss.NewStyle().Italic(true).Foreground(lipgloss.Color("240")).Render("(No review yet)") + "\n"
	}

	// Wrap everything in a box
	boxStyle := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("240")).
		Padding(1, 2).
		Width(70)

	return boxStyle.Render(s)
}

func (m BookDetailModel) Update(msg tea.Msg) (BookDetailModel, tea.Cmd) {
	return m, nil
}
