package buffer

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/models"
	_ "modernc.org/sqlite"
)

type SQLiteBuffer struct {
	db *sql.DB
}

func NewSQLiteBuffer(path string) (*SQLiteBuffer, error) {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return nil, fmt.Errorf("mkdir buffer dir: %w", err)
	}

	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, fmt.Errorf("open sqlite: %w", err)
	}

	if _, err := db.Exec(`PRAGMA journal_mode=WAL;`); err != nil {
		db.Close()
		return nil, fmt.Errorf("enable WAL: %w", err)
	}

	schema := `
	CREATE TABLE IF NOT EXISTS payload_buffer (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		hostname TEXT NOT NULL,
		collected_at TEXT NOT NULL,
		payload_json TEXT NOT NULL,
		sent INTEGER NOT NULL DEFAULT 0,
		created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
	);`
	if _, err := db.Exec(schema); err != nil {
		db.Close()
		return nil, fmt.Errorf("create schema: %w", err)
	}

	return &SQLiteBuffer{db: db}, nil
}

func (b *SQLiteBuffer) Store(payload models.Payload) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	_, err = b.db.Exec(
		`INSERT INTO payload_buffer (hostname, collected_at, payload_json, sent) VALUES (?, ?, ?, 0)`,
		payload.Hostname,
		payload.CollectedAt.UTC().Format(time.RFC3339),
		string(body),
	)
	if err != nil {
		return fmt.Errorf("insert payload: %w", err)
	}
	return nil
}

func (b *SQLiteBuffer) Pending() ([]models.Payload, error) {
	rows, err := b.db.Query(`SELECT payload_json FROM payload_buffer WHERE sent = 0 ORDER BY id ASC`)
	if err != nil {
		return nil, fmt.Errorf("query pending: %w", err)
	}
	defer rows.Close()

	payloads := []models.Payload{}
	for rows.Next() {
		var raw string
		if err := rows.Scan(&raw); err != nil {
			return nil, fmt.Errorf("scan payload: %w", err)
		}
		var payload models.Payload
		if err := json.Unmarshal([]byte(raw), &payload); err != nil {
			return nil, fmt.Errorf("unmarshal payload: %w", err)
		}
		payloads = append(payloads, payload)
	}

	return payloads, rows.Err()
}

func (b *SQLiteBuffer) MarkSent(hostname string, collectedAt time.Time) error {
	_, err := b.db.Exec(
		`UPDATE payload_buffer SET sent = 1 WHERE hostname = ? AND collected_at = ?`,
		hostname,
		collectedAt.UTC().Format(time.RFC3339),
	)
	if err != nil {
		return fmt.Errorf("mark sent: %w", err)
	}
	return nil
}

func (b *SQLiteBuffer) Close() error {
	return b.db.Close()
}
