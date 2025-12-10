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
	viewBookDetail
	viewReadingLists
	viewReadingListBooks
)

func Start(s *store.Store) {
	p := tea.NewProgram(initialModel(s), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, there's been an error: %v", err)
		os.Exit(1)
	}
}

type model struct {
	store            *store.Store
	state            sessionState
	booksModel       BooksModel
	form             *huh.Form
	formData         *BookForm
	searchInput      textinput.Model
	yearSelector     YearSelectorModel
	bookDetail       BookDetailModel
	readingLists     ReadingListsModel
	readingListBooks ReadingListBooksModel
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
		readingLists: NewReadingListsModel(s),
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

	// Handle reading list selection message globally
	if listMsg, ok := msg.(ReadingListSelectedMsg); ok {
		m.readingListBooks = NewReadingListBooksModel(m.store, listMsg.ListID, listMsg.ListName)
		m.state = viewReadingListBooks
		return m, m.readingListBooks.Init()
	}

	switch m.state {
	case viewList:
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.String() {
			case "q", "ctrl+c":
				return m, tea.Quit
			case "a":
				// Only allow "add book" when not searching
				if m.booksModel.searchQuery == "" {
					m.state = viewAdd
					m.formData = &BookForm{}
					m.form = NewAddBookForm(m.formData, m.store)
					return m, m.form.Init()
				} else {
					// When in search mode, "A" toggles search all years
					m.booksModel.searchAll = !m.booksModel.searchAll
					return m, m.booksModel.LoadBooks
				}
			case "/":
				m.state = viewSearch
				m.searchInput.Focus()
				return m, textinput.Blink
			case "y":
				m.state = viewYearSelector
				m.yearSelector = NewYearSelector(m.store)
				return m, m.yearSelector.Init()
			case "l":
				m.state = viewReadingLists
				m.readingLists = NewReadingListsModel(m.store)
				return m, m.readingLists.Init()
			case "enter":
				// Show book detail
				if book := m.booksModel.GetSelectedBook(); book != nil {
					m.bookDetail = NewBookDetail(*book)
					m.state = viewBookDetail
					return m, nil
				}
			case "esc":
				// Clear search when pressing Esc in list view
				if m.booksModel.searchQuery != "" {
					return m, m.booksModel.ClearSearch()
				}
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
			bookID, err := m.store.AddBook(book)
			if err != nil {
				// TODO: handle error
				m.state = viewList
				return m, m.booksModel.LoadBooks
			}

			// Add review if any review data was provided
			if m.formData.HasReview() {
				review := m.formData.ToReview(bookID)
				_, err := m.store.AddReview(review)
				if err != nil {
					// TODO: handle error
				}
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
			switch msg.String() {
			case "enter":
				query := m.searchInput.Value()
				if query != "" {
					m.state = viewList
					m.searchInput.Blur()
					return m, m.booksModel.SetSearch(query, false)
				}
			case "esc":
				m.state = viewList
				m.searchInput.Blur()
				m.searchInput.Reset()
				return m, m.booksModel.ClearSearch()
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

	case viewBookDetail:
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.String() {
			case "esc", "q", "enter":
				m.state = viewList
				return m, nil
			}
		}
		m.bookDetail, cmd = m.bookDetail.Update(msg)
		return m, cmd

	case viewReadingLists:
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.String() {
			case "esc", "q":
				m.state = viewList
				return m, nil
			}
		}
		cmd = m.readingLists.Update(msg)
		return m, cmd

	case viewReadingListBooks:
		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.String() {
			case "esc":
				m.state = viewReadingLists
				return m, m.readingLists.Init()
			case "q":
				m.state = viewList
				return m, nil
			}
		}
		cmd = m.readingListBooks.Update(msg)
		return m, cmd
	}

	return m, nil
}

func (m model) View() string {
	switch m.state {
	case viewList:
		var footer string
		if m.booksModel.searchQuery != "" {
			if m.booksModel.searchAll {
				footer = "\n  [enter] View Details  [a] Search Current Year  [/] New Search  [esc] Clear Search  [q] Quit\n"
			} else {
				footer = "\n  [enter] View Details  [a] Search All Years  [/] New Search  [esc] Clear Search  [q] Quit\n"
			}
		} else {
			footer = "\n  [enter] View Details  [y] Change Year  [l] Lists  [/] Search  [a] Add Book  [q] Quit\n"
		}
		return m.booksModel.View() + footer
	case viewAdd:
		return baseStyle.Render(m.form.View())
	case viewSearch:
		return fmt.Sprintf("\n%s\n\n  [enter] Search  [esc] Cancel\n", m.searchInput.View())
	case viewYearSelector:
		return m.yearSelector.View() + "\n\n  [↑/↓] Navigate  [enter] Select  [esc] Cancel\n"
	case viewBookDetail:
		return "\n" + m.bookDetail.View() + "\n\n  [enter/esc] Back to List  [q] Quit\n"
	case viewReadingLists:
		return "\n" + m.readingLists.View() + "\n\n  [enter] View List  [esc] Back to Books  [q] Quit\n"
	case viewReadingListBooks:
		return "\n" + m.readingListBooks.View() + "\n  [esc] Back to Lists  [q] Back to Books\n"
	}
	return ""
}
