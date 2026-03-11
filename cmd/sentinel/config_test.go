package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestParseEnvLine(t *testing.T) {
	key, value, ok, err := parseEnvLine(`SENTINEL_ENDPOINT="https://example.com/api/v1/events"`)
	if err != nil {
		t.Fatalf("parseEnvLine error: %v", err)
	}
	if !ok {
		t.Fatal("expected parsed line")
	}
	if key != "SENTINEL_ENDPOINT" {
		t.Fatalf("key = %s", key)
	}
	if value != "https://example.com/api/v1/events" {
		t.Fatalf("value = %s", value)
	}
}

func TestParseEnvLineComment(t *testing.T) {
	_, _, ok, err := parseEnvLine("# comment")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if ok {
		t.Fatal("comment line should be ignored")
	}
}

func TestParseEnvLineInvalid(t *testing.T) {
	_, _, _, err := parseEnvLine("INVALID_LINE")
	if err == nil {
		t.Fatal("expected invalid line error")
	}
}

func TestLoadEnvFileSetsUnsetVariablesOnly(t *testing.T) {
	path := filepath.Join(t.TempDir(), "sentinel.env")
	content := "SENTINEL_ENDPOINT=https://example.com/api/v1/events\nSENTINEL_INTERVAL_MINUTES=10\n"
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatalf("write env file: %v", err)
	}

	t.Setenv("SENTINEL_ENDPOINT", "https://override.local/api")
	_ = os.Unsetenv("SENTINEL_INTERVAL_MINUTES")

	if err := loadEnvFile(path); err != nil {
		t.Fatalf("loadEnvFile error: %v", err)
	}

	if got := os.Getenv("SENTINEL_ENDPOINT"); got != "https://override.local/api" {
		t.Fatalf("endpoint = %s", got)
	}
	if got := os.Getenv("SENTINEL_INTERVAL_MINUTES"); got != "10" {
		t.Fatalf("interval = %s", got)
	}
}
