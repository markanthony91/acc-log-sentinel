package collector

import "testing"

func TestParseReliabilityJSON(t *testing.T) {
	index, err := parseReliabilityJSON([]byte(`{"SystemStabilityIndex":7.2}`))
	if err != nil {
		t.Fatalf("parse error: %v", err)
	}
	if index != 7.2 {
		t.Fatalf("index = %v, want 7.2", index)
	}
}
