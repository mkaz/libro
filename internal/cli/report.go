package cli

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/models"
	"github.com/mkaz/libro/internal/store"
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
	Short: "Show reading report",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)

		author, _ := cmd.Flags().GetString("author")
		author = strings.TrimSpace(author)
		title, _ := cmd.Flags().GetString("title")
		year, _ := cmd.Flags().GetInt("year")

		// Check if --author flag was explicitly provided
		authorFlagSet := cmd.Flags().Changed("author")

		// If --author flag provided with no value, show author counts
		if authorFlagSet && author == "" {
			limit, _ := cmd.Flags().GetInt("limit")
			undated, _ := cmd.Flags().GetBool("undated")
			showAuthorCounts(s, limit, undated)
			return
		}

		var reviews []models.BookReview
		var err error

		if author != "" {
			// Filter by author
			reviews, err = s.SearchReviewsByAuthor(author, year)
		} else if title != "" {
			// Filter by title
			reviews, err = s.SearchReviewsByTitle(title, year)
		} else if year > 0 {
			// Filter by year
			reviews, err = s.GetReviewsByYear(year)
		} else {
			// Default: recent reviews
			reviews, err = s.GetRecentReviews(50)
		}

		if err != nil {
			fmt.Println(err)
			return
		}

		// Print header with fixed widths
		headerLine := fmt.Sprintf("%-3s    %-12s    %-40s  %-20s  %s",
			"ID", "Date", "Title", "Author", "Rating")
		fmt.Println(headerStyle.Render(headerLine))

		for _, r := range reviews {
			reviewID := "-"
			if r.ReviewID.Valid {
				reviewID = fmt.Sprintf("%d", r.ReviewID.Int64)
			}

			rating := "-"
			if r.Rating.Valid {
				rating = fmt.Sprintf("%d", r.Rating.Int64)
			}

			dateRead := "-"
			if r.DateRead.Valid {
				// Parse and format date like TUI (Jan 02, 2006)
				if parsed, err := time.Parse("2006-01-02T15:04:05Z07:00", r.DateRead.String); err == nil {
					dateRead = parsed.Format("Jan 02, 2006")
				}
			}

			// Truncate long titles and authors to fit fixed widths
			title := r.BookTitle
			if len(title) > 40 {
				title = title[:37] + "..."
			}

			author := r.BookAuthor
			if len(author) > 20 {
				author = author[:17] + "..."
			}

			line := fmt.Sprintf("%-3s    %-12s    %-40s  %-20s  %s",
				reviewID, dateRead, title, author, rating)
			fmt.Println(rowStyle.Render(line))
		}
	},
}

func showAuthorCounts(s *store.Store, minCount int, includeUndated bool) {
	counts, err := s.GetAuthorCounts(minCount, includeUndated)
	if err != nil {
		fmt.Println(err)
		return
	}

	// Print header
	headerLine := fmt.Sprintf("%-5s  %-50s", "Count", "Author")
	fmt.Println(headerStyle.Render(headerLine))

	for _, ac := range counts {
		author := ac.Author
		if len(author) > 50 {
			author = author[:47] + "..."
		}
		line := fmt.Sprintf("%-5d  %-50s", ac.Count, author)
		fmt.Println(rowStyle.Render(line))
	}
}

func init() {
	rootCmd.AddCommand(reportCmd)
	reportCmd.Flags().String("author", "", "Show author counts, or filter with --author=NAME")
	reportCmd.Flags().Lookup("author").NoOptDefVal = " "
	reportCmd.Flags().String("title", "", "Filter by title")
	reportCmd.Flags().Int("year", 0, "Filter by year")
	reportCmd.Flags().Int("limit", 3, "Minimum book count for --author")
	reportCmd.Flags().Bool("undated", false, "Include books without read dates in --author counts")
}
