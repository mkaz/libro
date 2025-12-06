package config

import (
	"os"
	"path/filepath"
	"runtime"
)

func GetDBLoc() string {
	// 1. Check current directory
	cwd, err := os.Getwd()
	if err == nil {
		localDB := filepath.Join(cwd, "libro.db")
		if _, err := os.Stat(localDB); err == nil {
			return localDB
		}
	}

	// 2. Check environment variable
	if env := os.Getenv("LIBRO_DB"); env != "" {
		return env
	}

	// 3. Platform specific data dir
	var dataDir string
	if runtime.GOOS == "windows" {
		dataDir = os.Getenv("APPDATA")
		if dataDir == "" {
			dataDir = filepath.Join(os.Getenv("USERPROFILE"), "AppData", "Roaming")
		}
	} else if runtime.GOOS == "darwin" {
		home, _ := os.UserHomeDir()
		dataDir = filepath.Join(home, "Library", "Application Support")
	} else {
		// Linux/Unix
		dataDir = os.Getenv("XDG_DATA_HOME")
		if dataDir == "" {
			home, _ := os.UserHomeDir()
			dataDir = filepath.Join(home, ".local", "share")
		}
	}

	appDir := filepath.Join(dataDir, "libro")
	if _, err := os.Stat(appDir); os.IsNotExist(err) {
		_ = os.MkdirAll(appDir, 0755)
	}

	return filepath.Join(appDir, "libro.db")
}
