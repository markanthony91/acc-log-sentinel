package collector

import "testing"

func TestParseEventLogJSON(t *testing.T) {
	raw := []byte(`[
	  {
	    "LogName": "System",
	    "Id": 41,
	    "LevelDisplayName": "Critical",
	    "Message": "Kernel power issue",
	    "TimeCreated": "2026-03-10T13:42:11Z"
	  }
	]`)

	events, err := parseEventLogJSON(raw)
	if err != nil {
		t.Fatalf("parse error: %v", err)
	}

	if len(events) != 1 {
		t.Fatalf("len(events) = %d, want 1", len(events))
	}
	if events[0].EventID != 41 {
		t.Fatalf("event id = %d, want 41", events[0].EventID)
	}
}
