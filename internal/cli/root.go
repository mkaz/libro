package cli

import (
	"fmt"
	"os"

	"github.com/mkaz/libro/internal/config"
	"github.com/mkaz/libro/internal/db"
	"github.com/mkaz/libro/internal/store"
	"github.com/mkaz/libro/internal/tui"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "libro",
	Short: "Track your reading history",
	Run: func(cmd *cobra.Command, args []string) {
		s := getStore(cmd)
		tui.Start(s)
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func init() {
	rootCmd.PersistentFlags().String("db", "", "SQLite file")
}

func getStore(cmd *cobra.Command) *store.Store {
	dbPath, _ := cmd.Flags().GetString("db")
	if dbPath == "" {
		dbPath = config.GetDBLoc()
	}
	database, err := db.InitDB(dbPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error initializing database: %v\n", err)
		os.Exit(1)
	}
	return store.New(database)
}
