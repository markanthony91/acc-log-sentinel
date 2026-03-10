package buffer

import (
	"path/filepath"
	"testing"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/models"
)

func TestSQLiteBufferStoreAndPending(t *testing.T) {
	path := filepath.Join(t.TempDir(), "buffer.db")
	buf, err := NewSQLiteBuffer(path)
	if err != nil {
		t.Fatalf("new buffer error: %v", err)
	}
	defer buf.Close()

	payload := models.Payload{
		Hostname:    "LOJA-001",
		CollectedAt: time.Date(2026, 3, 10, 14, 0, 0, 0, time.UTC),
	}
	if err := buf.Store(payload); err != nil {
		t.Fatalf("store error: %v", err)
	}

	pending, err := buf.Pending()
	if err != nil {
		t.Fatalf("pending error: %v", err)
	}
	if len(pending) != 1 {
		t.Fatalf("pending len = %d, want 1", len(pending))
	}

	if err := buf.MarkSent(payload.Hostname, payload.CollectedAt); err != nil {
		t.Fatalf("mark sent error: %v", err)
	}

	pending, err = buf.Pending()
	if err != nil {
		t.Fatalf("pending after mark sent error: %v", err)
	}
	if len(pending) != 0 {
		t.Fatalf("pending len after mark sent = %d, want 0", len(pending))
	}
}
