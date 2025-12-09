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
	store       *store.Store
	table       table.Model
	books       []models.BookReview
	year        int
	searchQuery string
	searchAll   bool // When true, search across all years
}

func (m BooksModel) GetSelectedBook() *models.BookReview {
	cursor := m.table.Cursor()
	if cursor >= 0 && cursor < len(m.books) {
		return &m.books[cursor]
	}
	return nil
}

const dateLayout = "2006-01-02T15:04:05Z07:00"

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
	var books []models.BookReview
	var err error

	if m.searchQuery != "" {
		// If searching, use search query
		year := m.year
		if m.searchAll {
			year = 0 // 0 means search all years
		}
		books, err = m.store.SearchReviews(m.searchQuery, year)
	} else {
		// Normal year view
		books, err = m.store.GetReviewsByYear(m.year)
	}

	if err != nil {
		// Log error to a file for debugging
		return nil
	}
	return BooksMsg(books)
}

func (m *BooksModel) SetSearch(query string, searchAll bool) tea.Cmd {
	m.searchQuery = query
	m.searchAll = searchAll
	return m.LoadBooks
}

func (m *BooksModel) ClearSearch() tea.Cmd {
	m.searchQuery = ""
	m.searchAll = false
	return m.LoadBooks
}

func (m BooksModel) SetYear(year int) tea.Cmd {
	m.year = year
	return m.LoadBooks
}

type BooksMsg []models.BookReview

func (m *BooksModel) Update(msg tea.Msg) tea.Cmd {
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
				// Try to parse the date - dates are stored as YYYY-MM-DD in SQLite
				parsedDate, err := time.Parse(dateLayout, b.DateRead.String)
				if err != nil {
					// If that fails, just use the raw string
					dateRead = b.DateRead.String
				} else {
					dateRead = parsedDate.Format("Jan 02, 2006")
				}
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
	return cmd
}

func (m BooksModel) View() string {
	var header string
	if m.searchQuery != "" {
		if m.searchAll {
			header = fmt.Sprintf("Search: \"%s\" (All Years) - %d results", m.searchQuery, len(m.books))
		} else {
			header = fmt.Sprintf("Search: \"%s\" (%d) - %d results", m.searchQuery, m.year, len(m.books))
		}
	} else {
		header = fmt.Sprintf("Books Read in %d (%d)", m.year, len(m.books))
	}

	return lipgloss.JoinVertical(lipgloss.Left,
		lipgloss.NewStyle().Bold(true).Render(header)+"\n",
		baseStyle.Render(m.table.View()),
	) + "\n"
}
