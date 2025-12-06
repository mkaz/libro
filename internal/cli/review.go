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

var reviewCmd = &cobra.Command{
	Use:   "review",
	Short: "Manage reviews",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)
		reviews, err := s.GetRecentReviews(20)
		if err != nil {
			fmt.Println(err)
			return
		}
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		fmt.Fprintln(w, "ID\tTitle\tRating\tDate")
		for _, r := range reviews {
			rating := "-"
			if r.Rating.Valid {
				rating = fmt.Sprintf("%d", r.Rating.Int64)
			}
			date := "-"
			if r.DateRead.Valid {
				date = r.DateRead.String
			}
			fmt.Fprintf(w, "%d\t%s\t%s\t%s\n", r.ReviewID.Int64, r.BookTitle, rating, date)
		}
		w.Flush()
	},
}

var reviewAddCmd = &cobra.Command{
	Use:   "add [book_id]",
	Short: "Add a review",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		bookID, _ := strconv.ParseInt(args[0], 10, 64)
		rating, _ := cmd.Flags().GetInt64("rating")
		text, _ := cmd.Flags().GetString("text")

		s := getStore(cmd)
		r := &models.Review{
			BookID:   bookID,
			Rating:   sql.NullInt64{Int64: rating, Valid: rating > 0},
			Review:   sql.NullString{String: text, Valid: text != ""},
			DateRead: sql.NullString{String: time.Now().Format("2006-01-02"), Valid: true},
		}
		id, err := s.AddReview(r)
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Printf("Added review %d\n", id)
	},
}

func init() {
	rootCmd.AddCommand(reviewCmd)
	reviewCmd.AddCommand(reviewAddCmd)
	reviewAddCmd.Flags().Int64("rating", 0, "Rating (1-5)")
	reviewAddCmd.Flags().String("text", "", "Review text")
}
