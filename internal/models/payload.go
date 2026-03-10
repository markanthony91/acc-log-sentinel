package models

import "time"

type Payload struct {
	Hostname     string    `json:"hostname"`
	CollectedAt  time.Time `json:"collected_at"`
	Events       []Event   `json:"events"`
	Metrics      Metrics   `json:"metrics"`
	BSODDetected bool      `json:"bsod_detected"`
}

type Event struct {
	Source    string    `json:"source"`
	EventID   int       `json:"event_id"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}

type Metrics struct {
	CPUPercent       float64 `json:"cpu_percent"`
	RAMAvailableMB   float64 `json:"ram_available_mb"`
	DiskFreePercent  float64 `json:"disk_free_percent"`
	UptimeHours      float64 `json:"uptime_hours"`
	ReliabilityIndex float64 `json:"reliability_index"`
}
