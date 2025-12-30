package cli

import (
	"database/sql"
	"fmt"
	"os"
	"strconv"
	"text/tabwriter"
	"time"

	"github.com/mkaz/libro/internal/models"
	"github.com/spf13/cobra"
)

var listCmd = &cobra.Command{
	Use:   "list [id]",
	Short: "Manage reading lists",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)
		if len(args) > 0 {
			// Show specific list
			id, _ := strconv.ParseInt(args[0], 10, 64)
			list, err := s.GetListBooks(id)
			if err != nil {
				fmt.Println(err)
				return
			}
			w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
			fmt.Fprintln(w, "ID\tTitle\tAuthor\tStatus")
			for _, b := range list {
				status := "To Read"
				if b.IsRead {
					status = "Read"
				}
				fmt.Fprintf(w, "%d\t%s\t%s\t%s\n", b.BookID, b.Title, b.Author, status)
			}
			w.Flush()
			return
		}

		// Show all lists
		lists, err := s.GetLists()
		if err != nil {
			fmt.Println(err)
			return
		}
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		fmt.Fprintln(w, "ID\tName                      \tStats          \tCreated")
		for _, l := range lists {
			// Get stats for this list
			books, _ := s.GetListBooks(l.ID)
			total := len(books)
			read := 0
			for _, b := range books {
				if b.IsRead {
					read++
				}
			}
			pct := 0
			if total > 0 {
				pct = read * 100 / total
			}
			stats := fmt.Sprintf("%d/%d (%d%%)", read, total, pct)

			created := ""
			if l.CreatedDate.Valid {
				if t, err := time.Parse(time.RFC3339, l.CreatedDate.String); err == nil {
					created = t.Format("Jan 02, 2006")
				}
			}
			fmt.Fprintf(w, "%d\t%-26s\t%-15s\t%s\n", l.ID, l.Name, stats, created)
		}
		w.Flush()
	},
}

var listCreateCmd = &cobra.Command{
	Use:   "create [name]",
	Short: "Create a reading list",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		name := args[0]
		desc, _ := cmd.Flags().GetString("description")

		s := getStore(cmd)
		l := &models.ReadingList{
			Name:        name,
			Description: sql.NullString{String: desc, Valid: desc != ""},
			// CreatedDate default handled by DB
		}
		id, err := s.CreateList(l)
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Printf("Created list %d: %s\n", id, name)
	},
}

var listAddCmd = &cobra.Command{
	Use:   "add [list_id] [book_id]",
	Short: "Add book to list",
	Args:  cobra.ExactArgs(2),
	Run: func(cmd *cobra.Command, args []string) {
		listID, _ := strconv.ParseInt(args[0], 10, 64)
		bookID, _ := strconv.ParseInt(args[1], 10, 64)

		s := getStore(cmd)
		err := s.AddBookToList(listID, bookID)
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Println("Added book to list")
	},
}

func init() {
	rootCmd.AddCommand(listCmd)
	listCmd.AddCommand(listCreateCmd)
	listCmd.AddCommand(listAddCmd)

	listCreateCmd.Flags().String("description", "", "List description")
}
