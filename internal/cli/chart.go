package cli

import (
	"fmt"

	"github.com/charmbracelet/lipgloss"
	"github.com/mkaz/libro/internal/store"
	"github.com/spf13/cobra"
)

var chartCmd = &cobra.Command{
	Use:   "chart",
	Short: "Show reading charts",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)
		year, _ := cmd.Flags().GetInt("year")

		if year > 0 {
			showMonthlyChart(s, year)
		} else {
			showYearlyChart(s)
		}
	},
}

func showYearlyChart(s *store.Store) {
	counts, err := s.GetYearlyCounts()
	if err != nil {
		fmt.Println(err)
		return
	}

	if len(counts) == 0 {
		fmt.Println("No data available")
		return
	}

	// Find max count for scaling
	maxCount := 0
	for _, c := range counts {
		if c.Count > maxCount {
			maxCount = c.Count
		}
	}

	// Calculate bar width (scale to fit ~50 characters)
	maxBarWidth := 50
	scale := float64(maxBarWidth) / float64(maxCount)

	// Title
	titleStyle := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("229"))
	fmt.Println()
	fmt.Println(titleStyle.Render("                         Books Read by Year"))
	fmt.Println()

	// Header
	fmt.Println("  Year   Count   Bar")
	fmt.Println(" ───────────────────────────────────────────────────────────────────")

	// Data rows
	for _, c := range counts {
		barLength := int(float64(c.Count) * scale)
		if barLength < 1 && c.Count > 0 {
			barLength = 1
		}
		bar := ""
		for i := 0; i < barLength; i++ {
			bar += "▄"
		}

		fmt.Printf("  %d   %-7d %s\n", c.Year, c.Count, bar)
	}

	fmt.Println()
}

func showMonthlyChart(s *store.Store, year int) {
	counts, err := s.GetMonthlyCounts(year)
	if err != nil {
		fmt.Println(err)
		return
	}

	if len(counts) == 0 {
		fmt.Printf("No data available for %d\n", year)
		return
	}

	// Find max count for scaling
	maxCount := 0
	for _, c := range counts {
		if c.Count > maxCount {
			maxCount = c.Count
		}
	}

	// Calculate bar width (scale to fit ~50 characters)
	maxBarWidth := 50
	scale := float64(maxBarWidth) / float64(maxCount)

	// Title
	titleStyle := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("229"))
	fmt.Println()
	fmt.Println(titleStyle.Render(fmt.Sprintf("                    Books Read by Month in %d", year)))
	fmt.Println()

	// Header
	fmt.Println("  Month        Count   Bar")
	fmt.Println(" ───────────────────────────────────────────────────────────────────")

	// Month names
	monthNames := []string{
		"January", "February", "March", "April", "May", "June",
		"July", "August", "September", "October", "November", "December",
	}

	// Data rows
	for _, c := range counts {
		barLength := int(float64(c.Count) * scale)
		if barLength < 1 && c.Count > 0 {
			barLength = 1
		}
		bar := ""
		for i := 0; i < barLength; i++ {
			bar += "▄"
		}

		monthName := monthNames[c.Month-1]
		fmt.Printf("  %-12s %-7d %s\n", monthName, c.Count, bar)
	}

	fmt.Println()
}

func init() {
	rootCmd.AddCommand(chartCmd)
	chartCmd.Flags().Int("year", 0, "Show monthly chart for specific year")
}
