package models

import (
	"encoding/json"
	"testing"
	"time"
)

func TestPayloadMarshalJSON(t *testing.T) {
	p := Payload{
		Hostname:    "LOJA-042",
		CollectedAt: time.Date(2026, 3, 10, 14, 0, 0, 0, time.UTC),
		Events: []Event{
			{
				Source:    "System",
				EventID:   7034,
				Level:     "Error",
				Message:   "Service terminated unexpectedly",
				Timestamp: time.Date(2026, 3, 10, 13, 42, 11, 0, time.UTC),
			},
		},
		Metrics: Metrics{
			CPUPercent:       45.2,
			RAMAvailableMB:   1024,
			DiskFreePercent:  12.5,
			UptimeHours:      168.3,
			ReliabilityIndex: 7.2,
		},
		BSODDetected: false,
	}

	data, err := json.Marshal(p)
	if err != nil {
		t.Fatalf("marshal error: %v", err)
	}

	var decoded map[string]interface{}
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal error: %v", err)
	}

	if decoded["hostname"] != "LOJA-042" {
		t.Fatalf("hostname = %v, want LOJA-042", decoded["hostname"])
	}

	events := decoded["events"].([]interface{})
	if len(events) != 1 {
		t.Fatalf("events count = %d, want 1", len(events))
	}
}
