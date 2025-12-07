package cli

import (
	"fmt"
	"os"
	"strconv"
	"text/tabwriter"

	"github.com/mkaz/libro/internal/models"
	"github.com/spf13/cobra"
)

var bookCmd = &cobra.Command{
	Use:   "book",
	Short: "Manage books",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)
		books, err := s.GetRecentBooks(20)
		if err != nil {
			fmt.Println(err)
			return
		}
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 1, ' ', 0)
		fmt.Fprintln(w,
			headerStyle.Render("ID")+"\t"+
				headerStyle.Render("Title")+"\t"+
				headerStyle.Render("Author")+"\t"+
				headerStyle.Render("Year"))

		for _, b := range books {
			year := ""
			if b.PubYear.Valid {
				year = strconv.FormatInt(b.PubYear.Int64, 10)
			}
			fmt.Fprintf(w, "%s\t%s\t%s\t%s\n",
				rowStyle.Render(fmt.Sprintf("%d", b.ID)),
				rowStyle.Render(b.Title),
				rowStyle.Render(b.Author),
				rowStyle.Render(year))
		}
		w.Flush()
	},
}

var bookAddCmd = &cobra.Command{
	Use:   "add",
	Short: "Add a book",
	Run: func(cmd *cobra.Command, args []string) {
		title, _ := cmd.Flags().GetString("title")
		author, _ := cmd.Flags().GetString("author")

		if title == "" || author == "" {
			fmt.Println("Error: --title and --author are required")
			return
		}

		s := getStore(cmd)
		b := &models.Book{
			Title:  title,
			Author: author,
		}
		id, err := s.AddBook(b)
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Printf("Added book ID: %d\n", id)
	},
}

func init() {
	rootCmd.AddCommand(bookCmd)
	bookCmd.AddCommand(bookAddCmd)

	bookAddCmd.Flags().String("title", "", "Book Title")
	bookAddCmd.Flags().String("author", "", "Book Author")
}
