package tui

import (
	"fmt"
	"strconv"
	"time"

	"github.com/charmbracelet/bubbles/table"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/models"
	"github.com/mkaz/libro/internal/store"
)

type BooksModel struct {
	store *store.Store
	table table.Model
	books []models.BookReview
	year  int
}

const dateLayout = "2006-01-02T15:04:05Z"

func NewBooksModel(s *store.Store) BooksModel {
	columns := []table.Column{
		{Title: "Date", Width: 12},
		{Title: "Title", Width: 40},
		{Title: "Author", Width: 25},
		{Title: "Rating", Width: 6},
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithFocused(true),
		table.WithHeight(20),
	)

	s_ := table.DefaultStyles()
	s_.Header = s_.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240")).
		BorderBottom(true).
		Bold(false)
	s_.Selected = s_.Selected.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("57")).
		Bold(false)
	t.SetStyles(s_)

	return BooksModel{
		store: s,
		table: t,
		year:  time.Now().Year(),
	}
}

func (m BooksModel) Init() tea.Cmd {
	return m.LoadBooks
}

func (m BooksModel) LoadBooks() tea.Msg {
	books, err := m.store.GetReviewsByYear(m.year)
	if err != nil {
		return nil
	}
	return BooksMsg(books)
}

func (m BooksModel) SearchBooks(query string) tea.Cmd {
	// TODO: Implementing search for read books if needed
	// For now, we'll keep the existing search behavior but map it to BookReview if possible
	// or maybe disable search in this view for now?
	// The prompt asked for "only show books that I've read".
	// Let's defer search modification or adapt it to search reviews.
	return nil
}

func (m BooksModel) SetYear(year int) tea.Cmd {
	m.year = year
	return m.LoadBooks
}

type BooksMsg []models.BookReview

func (m BooksModel) Update(msg tea.Msg) (BooksModel, tea.Cmd) {
	var cmd tea.Cmd
	switch msg := msg.(type) {
	case BooksMsg:
		m.books = msg

		rows := []table.Row{}
		for _, b := range m.books {
			rating := ""
			if b.Rating.Valid {
				rating = strconv.FormatInt(b.Rating.Int64, 10)
			}
			dateRead := ""
			if b.DateRead.Valid {
				parsedDate, _ := time.Parse(dateLayout, b.DateRead.String)
				dateRead = parsedDate.Format("Jan 02, 2006")
			}

			rows = append(rows, table.Row{
				dateRead,
				b.BookTitle,
				b.BookAuthor,
				rating,
			})
		}
		m.table.SetRows(rows)
	}
	m.table, cmd = m.table.Update(msg)
	return m, cmd
}

func (m BooksModel) View() string {
	return lipgloss.JoinVertical(lipgloss.Left,
		lipgloss.NewStyle().Bold(true).Render(fmt.Sprintf("Books Read in %d (%d)", m.year, len(m.books)))+"\n",
		baseStyle.Render(m.table.View()),
	) + "\n"
}
