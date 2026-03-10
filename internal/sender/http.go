package sender

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/models"
)

type HTTPSender struct {
	client   *http.Client
	endpoint string
	token    string
}

func NewHTTPSender(endpoint string, timeout time.Duration) *HTTPSender {
	return &HTTPSender{
		client:   &http.Client{Timeout: timeout},
		endpoint: endpoint,
		token:    os.Getenv("SENTINEL_API_TOKEN"),
	}
}

func (s *HTTPSender) Send(payload models.Payload) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, s.endpoint, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	if s.token != "" {
		req.Header.Set("Authorization", "Bearer "+s.token)
	}

	resp, err := s.client.Do(req)
	if err != nil {
		return fmt.Errorf("send payload: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("unexpected status code %d", resp.StatusCode)
	}

	return nil
}
