package tui

import (
	"fmt"
	"strconv"

	"github.com/charmbracelet/bubbles/table"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/models"
	"github.com/mkaz/libro/internal/store"
)

type ReadingListBooksModel struct {
	store    *store.Store
	table    table.Model
	books    []models.ReadingListBookDetail
	listID   int64
	listName string
}

type ReadingListBooksMsg []models.ReadingListBookDetail

func NewReadingListBooksModel(s *store.Store, listID int64, listName string) ReadingListBooksModel {
	columns := []table.Column{
		{Title: "Title", Width: 40},
		{Title: "Author", Width: 25},
		{Title: "Status", Width: 10},
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

	return ReadingListBooksModel{
		store:    s,
		table:    t,
		listID:   listID,
		listName: listName,
	}
}

func (m ReadingListBooksModel) Init() tea.Cmd {
	return m.LoadBooks
}

func (m ReadingListBooksModel) LoadBooks() tea.Msg {
	books, err := m.store.GetListBooks(m.listID)
	if err != nil {
		return nil
	}
	return ReadingListBooksMsg(books)
}

func (m *ReadingListBooksModel) Update(msg tea.Msg) tea.Cmd {
	var cmd tea.Cmd
	switch msg := msg.(type) {
	case ReadingListBooksMsg:
		m.books = msg

		rows := []table.Row{}
		for _, b := range m.books {
			status := "To Read"
			if b.IsRead {
				status = "Read"
			}
			rating := ""
			if b.Rating.Valid {
				rating = strconv.FormatInt(b.Rating.Int64, 10)
			}

			rows = append(rows, table.Row{
				b.Title,
				b.Author,
				status,
				rating,
			})
		}
		m.table.SetRows(rows)
	}
	m.table, cmd = m.table.Update(msg)
	return cmd
}

func (m ReadingListBooksModel) View() string {
	header := lipgloss.NewStyle().Bold(true).Render(m.listName)

	// Calculate stats
	total := len(m.books)
	read := 0
	for _, b := range m.books {
		if b.IsRead {
			read++
		}
	}
	pct := 0
	if total > 0 {
		pct = (read * 100) / total
	}
	stats := fmt.Sprintf("%d/%d read (%d%%)", read, total, pct)

	return lipgloss.JoinVertical(lipgloss.Left,
		header,
		stats+"\n",
		baseStyle.Render(m.table.View()),
	) + "\n"
}
