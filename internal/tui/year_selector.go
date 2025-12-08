package tui

import (
	"fmt"
	"strconv"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/store"
)

type yearItem struct {
	year  int
	count int
}

func (i yearItem) FilterValue() string { return strconv.Itoa(i.year) }
func (i yearItem) Title() string {
	if i.count == 1 {
		return fmt.Sprintf("%d - 1 book", i.year)
	}
	return fmt.Sprintf("%d - %d books", i.year, i.count)
}
func (i yearItem) Description() string { return "" }

type YearSelectorModel struct {
	list  list.Model
	store *store.Store
}

type YearSelectedMsg int

func NewYearSelector(s *store.Store) YearSelectorModel {
	delegate := list.NewDefaultDelegate()
	delegate.ShowDescription = false
	delegate.Styles.SelectedTitle = delegate.Styles.SelectedTitle.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("57")).
		Bold(true)

	l := list.New([]list.Item{}, delegate, 30, 14)
	l.Title = "Select Year"
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.Styles.Title = lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("229")).
		Padding(0, 0, 1, 0)

	return YearSelectorModel{
		list:  l,
		store: s,
	}
}

func (m YearSelectorModel) Init() tea.Cmd {
	return m.loadYears
}

func (m YearSelectorModel) loadYears() tea.Msg {
	years, err := m.store.GetAvailableYears()
	if err != nil {
		return nil
	}

	items := make([]list.Item, len(years))
	for i, year := range years {
		// Get count for this year
		reviews, err := m.store.GetReviewsByYear(year)
		count := 0
		if err == nil {
			count = len(reviews)
		}
		items[i] = yearItem{year: year, count: count}
	}
	return yearsLoadedMsg(items)
}

type yearsLoadedMsg []list.Item

func (m YearSelectorModel) Update(msg tea.Msg) (YearSelectorModel, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case yearsLoadedMsg:
		m.list.SetItems(msg)
		return m, nil

	case tea.KeyMsg:
		switch msg.String() {
		case "enter":
			if selected, ok := m.list.SelectedItem().(yearItem); ok {
				return m, func() tea.Msg { return YearSelectedMsg(selected.year) }
			}
		}
	}

	m.list, cmd = m.list.Update(msg)
	return m, cmd
}

func (m YearSelectorModel) View() string {
	return lipgloss.NewStyle().
		Padding(1, 2).
		Render(m.list.View())
}
