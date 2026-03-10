package collector

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"os/exec"
	"runtime"
	"strings"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/models"
)

type powerShellEvent struct {
	LogName      string `json:"LogName"`
	ID           int    `json:"Id"`
	LevelDisplay string `json:"LevelDisplayName"`
	Message      string `json:"Message"`
	TimeCreated  string `json:"TimeCreated"`
}

func CollectAllEventLogs(since time.Time) ([]models.Event, error) {
	if runtime.GOOS != "windows" {
		return []models.Event{}, nil
	}

	script := fmt.Sprintf(`$logs = "System","Application"; Get-WinEvent -FilterHashtable @{LogName=$logs; StartTime=[datetime]"%s"; Level=1,2,3} | Select-Object LogName, Id, LevelDisplayName, Message, TimeCreated | ConvertTo-Json -Depth 3`, since.UTC().Format(time.RFC3339))

	cmd := exec.Command("powershell", "-NoProfile", "-Command", script)
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("powershell Get-WinEvent failed: %w (%s)", err, strings.TrimSpace(stderr.String()))
	}

	events, err := parseEventLogJSON(stdout.Bytes())
	if err != nil {
		return nil, err
	}

	log.Printf("[LogSentinel] Collected %d Windows event log entries", len(events))
	return events, nil
}

func parseEventLogJSON(data []byte) ([]models.Event, error) {
	trimmed := bytes.TrimSpace(data)
	if len(trimmed) == 0 || bytes.Equal(trimmed, []byte("null")) {
		return []models.Event{}, nil
	}

	var list []powerShellEvent
	if err := json.Unmarshal(trimmed, &list); err != nil {
		var single powerShellEvent
		if errSingle := json.Unmarshal(trimmed, &single); errSingle != nil {
			return nil, fmt.Errorf("unmarshal event log JSON: %w", err)
		}
		list = []powerShellEvent{single}
	}

	events := make([]models.Event, 0, len(list))
	for _, item := range list {
		ts, err := time.Parse(time.RFC3339, item.TimeCreated)
		if err != nil {
			ts = time.Time{}
		}
		events = append(events, models.Event{
			Source:    item.LogName,
			EventID:   item.ID,
			Level:     normalizeLevel(item.LevelDisplay),
			Message:   strings.TrimSpace(item.Message),
			Timestamp: ts.UTC(),
		})
	}

	return events, nil
}

func normalizeLevel(value string) string {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "critical":
		return "Critical"
	case "error":
		return "Error"
	case "warning":
		return "Warning"
	default:
		if value == "" {
			return "Unknown"
		}
		return strings.TrimSpace(value)
	}
}
