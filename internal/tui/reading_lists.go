package tui

import (
	"fmt"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/models"
	"github.com/mkaz/libro/internal/store"
)

type readingListItem struct {
	list models.ReadingList
}

func (i readingListItem) FilterValue() string { return i.list.Name }
func (i readingListItem) Title() string       { return i.list.Name }
func (i readingListItem) Description() string {
	if i.list.Description.Valid && i.list.Description.String != "" {
		return i.list.Description.String
	}
	return ""
}

type ReadingListsModel struct {
	list  list.Model
	store *store.Store
	lists []models.ReadingList
}

type ReadingListSelectedMsg struct {
	ListID   int64
	ListName string
}

type readingListsLoadedMsg []models.ReadingList

func NewReadingListsModel(s *store.Store) ReadingListsModel {
	delegate := list.NewDefaultDelegate()
	delegate.ShowDescription = false
	delegate.Styles.SelectedTitle = delegate.Styles.SelectedTitle.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("57")).
		Bold(true)

	l := list.New([]list.Item{}, delegate, 50, 14)
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.SetShowTitle(false)

	return ReadingListsModel{
		list:  l,
		store: s,
	}
}

func (m ReadingListsModel) Init() tea.Cmd {
	return m.loadLists
}

func (m ReadingListsModel) loadLists() tea.Msg {
	lists, err := m.store.GetLists()
	if err != nil {
		return nil
	}
	return readingListsLoadedMsg(lists)
}

func (m ReadingListsModel) GetSelectedList() *models.ReadingList {
	if selected, ok := m.list.SelectedItem().(readingListItem); ok {
		return &selected.list
	}
	return nil
}

func (m *ReadingListsModel) Update(msg tea.Msg) tea.Cmd {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case readingListsLoadedMsg:
		m.lists = msg
		items := make([]list.Item, len(m.lists))
		for i, l := range m.lists {
			items[i] = readingListItem{list: l}
		}
		m.list.SetItems(items)
		return nil

	case tea.KeyMsg:
		switch msg.String() {
		case "enter":
			if selected := m.GetSelectedList(); selected != nil {
				return func() tea.Msg {
					return ReadingListSelectedMsg{
						ListID:   selected.ID,
						ListName: selected.Name,
					}
				}
			}
		}
	}

	m.list, cmd = m.list.Update(msg)
	return cmd
}

func (m ReadingListsModel) View() string {
	header := fmt.Sprintf("Reading Lists (%d)", len(m.lists))
	return lipgloss.JoinVertical(lipgloss.Left,
		lipgloss.NewStyle().Bold(true).Render(header)+"\n",
		m.list.View(),
	)
}
