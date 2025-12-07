package tui

import (
	"fmt"
	"os"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/huh"
	"github.com/mkaz/libro/internal/store"
)

type sessionState int

const (
	viewList sessionState = iota
	viewAdd
	viewSearch
	viewYearSelector
)

func Start(s *store.Store) {
	p := tea.NewProgram(initialModel(s), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, there's been an error: %v", err)
		os.Exit(1)
	}
}

type model struct {
	store        *store.Store
	state        sessionState
	booksModel   BooksModel
	form         *huh.Form
	formData     *BookForm
	searchInput  textinput.Model
	yearSelector YearSelectorModel
}

func initialModel(s *store.Store) model {
	ti := textinput.New()
	ti.Placeholder = "Search books..."
	ti.CharLimit = 156
	ti.Width = 30
	ti.Prompt = "🔎 "

	return model{
		store:        s,
		state:        viewList,
		booksModel:   NewBooksModel(s),
		searchInput:  ti,
		yearSelector: NewYearSelector(s),
	}
}

func (m model) Init() tea.Cmd {
	return m.booksModel.Init()
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	// Handle year selection message globally
	if yearMsg, ok := msg.(YearSelectedMsg); ok {
		m.booksModel.year = int(yearMsg)
		m.state = viewList
		return m, m.booksModel.LoadBooks
	}

	switch m.state {
	case viewList:
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.String() {
			case "q", "ctrl+c":
				return m, tea.Quit
			case "a":
				m.state = viewAdd
				m.formData = &BookForm{}
				m.form = NewAddBookForm(m.formData)
				return m, m.form.Init()
			case "/":
				m.state = viewSearch
				m.searchInput.Focus()
				return m, textinput.Blink
			case "y":
				m.state = viewYearSelector
				m.yearSelector = NewYearSelector(m.store)
				return m, m.yearSelector.Init()
			}
		}
		cmd = m.booksModel.Update(msg)
		return m, cmd

	case viewAdd:
		var formCmd tea.Cmd

		// Update the form
		formModel, formCmd := m.form.Update(msg)
		if f, ok := formModel.(*huh.Form); ok {
			m.form = f
		}

		if m.form.State == huh.StateAborted {
			m.state = viewList
			return m, nil
		}

		if m.form.State == huh.StateCompleted {
			book := m.formData.ToBook()
			_, err := m.store.AddBook(book)
			if err != nil {
				// TODO: handle error
			}
			m.state = viewList
			// Return a command that reloads the books
			return m, m.booksModel.LoadBooks
		}

		return m, formCmd

	case viewSearch:
		var cmd tea.Cmd
		m.searchInput, cmd = m.searchInput.Update(msg)
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.Type {
			case tea.KeyEnter:
				// query := m.searchInput.Value()
				// m.state = viewList
				// return m, m.booksModel.SearchBooks(query)
				// Search disabled for now in year view
				m.state = viewList
				return m, nil
			case tea.KeyEsc:
				m.state = viewList
				m.searchInput.Blur()
				m.searchInput.Reset()
				return m, m.booksModel.LoadBooks
			}
		}
		return m, cmd

	case viewYearSelector:
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.String() {
			case "esc", "q":
				m.state = viewList
				return m, nil
			}
		}
		m.yearSelector, cmd = m.yearSelector.Update(msg)
		return m, cmd
	}

	return m, nil
}

func (m model) View() string {
	switch m.state {
	case viewList:
		return m.booksModel.View() + "\n  [y] Change Year  [a] Add Book  [q] Quit\n"
	case viewAdd:
		return baseStyle.Render(m.form.View())
	case viewSearch:
		return fmt.Sprintf("\n%s\n\n%s", m.searchInput.View(), m.booksModel.View())
	case viewYearSelector:
		return m.yearSelector.View() + "\n\n  [↑/↓] Navigate  [enter] Select  [esc] Cancel\n"
	}
	return ""
}
