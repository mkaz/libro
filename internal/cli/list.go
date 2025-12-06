package cli

import (
	"database/sql"
	"fmt"
	"os"
	"strconv"
	"text/tabwriter"

	"github.com/mkaz/libro/internal/models"
	"github.com/spf13/cobra"
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "Manage reading lists",
}

var listShowCmd = &cobra.Command{
	Use:   "show [id]",
	Short: "Show reading lists or specific list",
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
		fmt.Fprintln(w, "ID\tName\tDescription\tCreated")
		for _, l := range lists {
			desc := ""
			if l.Description.Valid {
				desc = l.Description.String
			}
			created := ""
			if l.CreatedDate.Valid {
				created = l.CreatedDate.String
			}
			fmt.Fprintf(w, "%d\t%s\t%s\t%s\n", l.ID, l.Name, desc, created)
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
	listCmd.AddCommand(listShowCmd)
	listCmd.AddCommand(listCreateCmd)
	listCmd.AddCommand(listAddCmd)

	listCreateCmd.Flags().String("description", "", "List description")
}
