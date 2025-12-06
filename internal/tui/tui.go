package tui

import (
	"fmt"
	"os"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/huh"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/mkaz/libro/internal/store"
)

type sessionState int

const (
	viewList sessionState = iota
	viewAdd
	viewSearch
)

func Start(s *store.Store) {
	p := tea.NewProgram(initialModel(s), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, there's been an error: %v", err)
		os.Exit(1)
	}
}

type model struct {
	store       *store.Store
	state       sessionState
	booksModel  BooksModel
	form        *huh.Form
	formData    *BookForm
	searchInput textinput.Model
}

func initialModel(s *store.Store) model {
	ti := textinput.New()
	ti.Placeholder = "Search books..."
	ti.CharLimit = 156
	ti.Width = 30
	ti.Prompt = "🔎 "

	return model{
		store:       s,
		state:       viewList,
		booksModel:  NewBooksModel(s),
		searchInput: ti,
	}
}

func (m model) Init() tea.Cmd {
	return m.booksModel.Init()
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

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
			case "left":
				m.booksModel.year--
				return m, m.booksModel.LoadBooks
			case "right":
				if m.booksModel.year < time.Now().Year() {
					m.booksModel.year++
					return m, m.booksModel.LoadBooks
				}
			}
		}
		m.booksModel, cmd = m.booksModel.Update(msg)
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
	}

	return m, nil
}

func (m model) View() string {
	switch m.state {
	case viewList:
		return m.booksModel.View() + "\n  [←/→] Change Year  [a] Add Book  [q] Quit\n"
	case viewAdd:
		return baseStyle.Render(m.form.View())
	case viewSearch:
		return fmt.Sprintf("\n%s\n\n%s", m.searchInput.View(), m.booksModel.View())
	}
	return ""
}
