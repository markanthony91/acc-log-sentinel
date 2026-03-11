package main

import (
	"os"
	"testing"
	"time"
)

func TestResolveCollectIntervalDefault(t *testing.T) {
	t.Setenv("SENTINEL_INTERVAL_MINUTES", "")
	if got := resolveCollectInterval(); got != 60*time.Minute {
		t.Fatalf("interval = %v, want 60m", got)
	}
}

func TestResolveCollectIntervalEnv(t *testing.T) {
	t.Setenv("SENTINEL_INTERVAL_MINUTES", "15")
	if got := resolveCollectInterval(); got != 15*time.Minute {
		t.Fatalf("interval = %v, want 15m", got)
	}
}

func TestResolveBufferPathOverride(t *testing.T) {
	t.Setenv("SENTINEL_BUFFER_PATH", "/tmp/custom-buffer.db")
	if got := resolveBufferPath(); got != "/tmp/custom-buffer.db" {
		t.Fatalf("buffer path = %s, want override", got)
	}
}

func TestHandleServiceCommandUnknown(t *testing.T) {
	err := handleServiceCommand(nil, "unknown")
	if err == nil {
		t.Fatal("expected error for unknown command")
	}
}

func TestResolveEndpointDefault(t *testing.T) {
	_ = os.Unsetenv("SENTINEL_ENDPOINT")
	if got := resolveEndpoint(); got != defaultEndpoint {
		t.Fatalf("endpoint = %s, want %s", got, defaultEndpoint)
	}
}
