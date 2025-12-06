package cli

import (
	"encoding/csv"
	"fmt"
	"os"

	"github.com/mkaz/libro/internal/models"
	"github.com/spf13/cobra"
)

var importCmd = &cobra.Command{
	Use:   "import [file]",
	Short: "Import books from CSV",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		filename := args[0]
		f, err := os.Open(filename)
		if err != nil {
			fmt.Println(err)
			return
		}
		defer f.Close()

		reader := csv.NewReader(f)
		records, err := reader.ReadAll()
		if err != nil {
			fmt.Println(err)
			return
		}

		s := getStore(cmd)
		count := 0
		for i, record := range records {
			if i == 0 {
				continue
			} // Header
			if len(record) < 2 {
				continue
			}
			title := record[0]
			author := record[1]

			b := &models.Book{Title: title, Author: author}
			_, err := s.AddBook(b)
			if err == nil {
				count++
			}
		}
		fmt.Printf("Imported %d books\n", count)
	},
}

func init() {
	rootCmd.AddCommand(importCmd)
}
