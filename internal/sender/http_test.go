package sender

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/models"
)

func TestHTTPSenderSend(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Fatalf("method = %s, want POST", r.Method)
		}
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	client := NewHTTPSender(server.URL, 2*time.Second)
	err := client.Send(models.Payload{Hostname: "LOJA-042", CollectedAt: time.Now()})
	if err != nil {
		t.Fatalf("send error: %v", err)
	}
}
