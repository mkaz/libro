package cli

import (
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"
)

var (
	headerStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("229")).
			Background(lipgloss.Color("57")).
			Padding(0, 1)

	rowStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("252")).
			Padding(0, 1)
)

var reportCmd = &cobra.Command{
	Use:   "report",
	Short: "Show reports",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)
		// TODO: handle flags
		reviews, err := s.GetRecentReviews(50)
		if err != nil {
			fmt.Println(err)
			return
		}

		w := tabwriter.NewWriter(os.Stdout, 0, 0, 1, ' ', 0)
		fmt.Fprintln(w,
			headerStyle.Render("ID")+"\t"+
				headerStyle.Render("Title")+"\t"+
				headerStyle.Render("Author")+"\t"+
				headerStyle.Render("Rating")+"\t"+
				headerStyle.Render("Date Read"))

		for _, r := range reviews {
			rating := "-"
			if r.Rating.Valid {
				rating = fmt.Sprintf("%d", r.Rating.Int64)
			}
			dateRead := "-"
			if r.DateRead.Valid {
				dateRead = r.DateRead.String
			}
			id := r.ReviewID.Int64

			fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\n",
				rowStyle.Render(fmt.Sprintf("%d", id)),
				rowStyle.Render(r.BookTitle),
				rowStyle.Render(r.BookAuthor),
				rowStyle.Render(rating),
				rowStyle.Render(dateRead),
			)
		}
		w.Flush()
	},
}

func init() {
	rootCmd.AddCommand(reportCmd)
}
