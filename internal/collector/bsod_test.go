package collector

import (
	"testing"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/models"
)

func TestDetectBSOD(t *testing.T) {
	events := []models.Event{
		{Source: "System", EventID: 41, Level: "Critical", Timestamp: time.Now()},
	}

	if !DetectBSOD(events) {
		t.Fatal("expected BSOD detection")
	}
}
