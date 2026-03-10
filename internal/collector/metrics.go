package collector

import (
	"fmt"

	"github.com/aiknow/acc_log_sentinel/internal/models"
	"github.com/shirou/gopsutil/v4/cpu"
	"github.com/shirou/gopsutil/v4/disk"
	"github.com/shirou/gopsutil/v4/mem"
	"github.com/shirou/gopsutil/v4/host"
)

func CollectMetrics() (models.Metrics, error) {
	var result models.Metrics

	cpuPercent, err := cpu.Percent(0, false)
	if err != nil {
		return result, fmt.Errorf("cpu percent: %w", err)
	}
	if len(cpuPercent) > 0 {
		result.CPUPercent = cpuPercent[0]
	}

	vmem, err := mem.VirtualMemory()
	if err != nil {
		return result, fmt.Errorf("virtual memory: %w", err)
	}
	result.RAMAvailableMB = float64(vmem.Available) / (1024 * 1024)

	usage, err := disk.Usage(defaultDiskPath())
	if err != nil {
		return result, fmt.Errorf("disk usage: %w", err)
	}
	result.DiskFreePercent = 100 - usage.UsedPercent

	uptimeSeconds, err := host.Uptime()
	if err != nil {
		return result, fmt.Errorf("host uptime: %w", err)
	}
	result.UptimeHours = float64(uptimeSeconds) / 3600

	return result, nil
}
