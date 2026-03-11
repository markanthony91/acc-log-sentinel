package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/aiknow/acc_log_sentinel/internal/buffer"
	"github.com/aiknow/acc_log_sentinel/internal/collector"
	"github.com/aiknow/acc_log_sentinel/internal/models"
	"github.com/aiknow/acc_log_sentinel/internal/sender"
	"github.com/kardianos/service"
)

const (
	defaultEndpoint        = "http://127.0.0.1:16100/api/v1/events"
	defaultIntervalMinutes = 60
	sendTimeout            = 30 * time.Second
)

type Program struct {
	exit     chan struct{}
	sender   *sender.HTTPSender
	buffer   *buffer.SQLiteBuffer
	interval time.Duration
}

func newProgram() (*Program, error) {
	bufferPath := resolveBufferPath()
	buf, err := buffer.NewSQLiteBuffer(bufferPath)
	if err != nil {
		return nil, err
	}

	return &Program{
		exit:     make(chan struct{}),
		sender:   sender.NewHTTPSender(resolveEndpoint(), sendTimeout),
		buffer:   buf,
		interval: resolveCollectInterval(),
	}, nil
}

func (p *Program) Start(_ service.Service) error {
	go p.run()
	return nil
}

func (p *Program) Stop(_ service.Service) error {
	close(p.exit)
	if p.buffer != nil {
		return p.buffer.Close()
	}
	return nil
}

func (p *Program) run() {
	hostname, _ := os.Hostname()
	log.Printf("[LogSentinel] Service started on %s interval=%s", hostname, p.interval)

	p.collectAndSend(hostname)

	ticker := time.NewTicker(p.interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			p.collectAndSend(hostname)
		case <-p.exit:
			log.Printf("[LogSentinel] Service stopping on %s", hostname)
			return
		}
	}
}

func (p *Program) collectAndSend(hostname string) {
	payload := buildPayload(hostname, p.interval)
	if payload == nil {
		return
	}

	if err := p.flushBuffer(); err != nil {
		log.Printf("[LogSentinel] Buffer flush error: %v", err)
	}

	if err := p.sender.Send(*payload); err != nil {
		log.Printf("[LogSentinel] Send failed, storing locally: %v", err)
		if storeErr := p.buffer.Store(*payload); storeErr != nil {
			log.Printf("[LogSentinel] Buffer store error: %v", storeErr)
		}
		return
	}

	log.Printf("[LogSentinel] Sent payload successfully for %s events=%d bsod=%v", hostname, len(payload.Events), payload.BSODDetected)
}

func (p *Program) flushBuffer() error {
	pending, err := p.buffer.Pending()
	if err != nil {
		return err
	}
	if len(pending) == 0 {
		return nil
	}

	log.Printf("[LogSentinel] Flushing %d buffered payloads", len(pending))
	for _, payload := range pending {
		if err := p.sender.Send(payload); err != nil {
			return err
		}
		if err := p.buffer.MarkSent(payload.Hostname, payload.CollectedAt); err != nil {
			return err
		}
	}
	return nil
}

func runOnce() error {
	hostname, _ := os.Hostname()
	payload := buildPayload(hostname, resolveCollectInterval())
	if payload == nil {
		return nil
	}

	if os.Getenv("LOG_SENTINEL_STDOUT") == "1" || os.Getenv("SENTINEL_DRY_RUN") == "1" {
		data, err := json.MarshalIndent(payload, "", "  ")
		if err != nil {
			return err
		}
		_, _ = os.Stdout.Write(data)
		_, _ = os.Stdout.Write([]byte("\n"))
		return nil
	}

	program, err := newProgram()
	if err != nil {
		return err
	}
	defer program.buffer.Close()

	program.collectAndSend(hostname)
	return nil
}

func buildPayload(hostname string, interval time.Duration) *models.Payload {
	events, err := collector.CollectAllEventLogs(time.Now().Add(-interval))
	if err != nil {
		log.Printf("[LogSentinel] Event collection error: %v", err)
	}

	metrics, err := collector.CollectMetrics()
	if err != nil {
		log.Printf("[LogSentinel] Metrics collection error: %v", err)
	}
	metrics.ReliabilityIndex = collector.CollectReliabilityIndex()

	return &models.Payload{
		Hostname:     hostname,
		CollectedAt:  time.Now().UTC(),
		Events:       events,
		Metrics:      metrics,
		BSODDetected: collector.DetectBSOD(events),
	}
}

func resolveEndpoint() string {
	if endpoint := os.Getenv("SENTINEL_ENDPOINT"); endpoint != "" {
		return endpoint
	}
	return defaultEndpoint
}

func resolveBufferPath() string {
	if path := os.Getenv("SENTINEL_BUFFER_PATH"); path != "" {
		return path
	}
	exePath, err := os.Executable()
	if err != nil {
		return filepath.Join("data", "buffer.db")
	}
	return filepath.Join(filepath.Dir(exePath), "data", "buffer.db")
}

func resolveCollectInterval() time.Duration {
	if raw := os.Getenv("SENTINEL_INTERVAL_MINUTES"); raw != "" {
		minutes, err := strconv.Atoi(raw)
		if err == nil && minutes > 0 {
			return time.Duration(minutes) * time.Minute
		}
		log.Printf("[LogSentinel] Invalid SENTINEL_INTERVAL_MINUTES=%q, using default", raw)
	}
	return defaultIntervalMinutes * time.Minute
}

func intervalDescription() string {
	return fmt.Sprintf("%d minutes", int(resolveCollectInterval()/time.Minute))
}
