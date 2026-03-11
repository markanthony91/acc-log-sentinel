package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
)

const localConfigName = "sentinel.env"

func loadLocalConfig() error {
	for _, path := range configCandidates() {
		if err := loadEnvFile(path); err != nil {
			return err
		}
	}
	return nil
}

func configCandidates() []string {
	paths := make([]string, 0, 2)

	if wd, err := os.Getwd(); err == nil {
		paths = append(paths, filepath.Join(wd, localConfigName))
	}

	if exePath, err := os.Executable(); err == nil {
		exeConfig := filepath.Join(filepath.Dir(exePath), localConfigName)
		duplicate := false
		for _, existing := range paths {
			if existing == exeConfig {
				duplicate = true
				break
			}
		}
		if !duplicate {
			paths = append(paths, exeConfig)
		}
	}

	return paths
}

func loadEnvFile(path string) error {
	file, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return fmt.Errorf("open config %s: %w", path, err)
	}
	defer file.Close()

	loaded := 0
	scanner := bufio.NewScanner(file)
	for lineNumber := 1; scanner.Scan(); lineNumber++ {
		key, value, ok, err := parseEnvLine(scanner.Text())
		if err != nil {
			return fmt.Errorf("parse config %s line %d: %w", path, lineNumber, err)
		}
		if !ok {
			continue
		}
		if _, exists := os.LookupEnv(key); exists {
			continue
		}
		if err := os.Setenv(key, value); err != nil {
			return fmt.Errorf("set env %s from %s: %w", key, path, err)
		}
		loaded++
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("scan config %s: %w", path, err)
	}

	if loaded > 0 {
		log.Printf("[LogSentinel] Loaded %d settings from %s", loaded, path)
	}

	return nil
}

func parseEnvLine(line string) (string, string, bool, error) {
	trimmed := strings.TrimSpace(line)
	if trimmed == "" || strings.HasPrefix(trimmed, "#") || strings.HasPrefix(trimmed, ";") {
		return "", "", false, nil
	}

	parts := strings.SplitN(trimmed, "=", 2)
	if len(parts) != 2 {
		return "", "", false, fmt.Errorf("invalid format")
	}

	key := strings.TrimSpace(parts[0])
	if key == "" {
		return "", "", false, fmt.Errorf("missing key")
	}

	value := strings.TrimSpace(parts[1])
	value = strings.Trim(value, "\"")
	return key, value, true, nil
}
