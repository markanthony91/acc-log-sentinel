package collector

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
)

func CollectReliabilityIndex() float64 {
	if runtime.GOOS != "windows" {
		return -1
	}

	cmd := exec.Command("powershell", "-NoProfile", "-Command", `Get-CimInstance -ClassName Win32_ReliabilityStabilityMetrics | Select-Object -First 1 TimeGenerated, SystemStabilityIndex | ConvertTo-Json`)
	var stdout bytes.Buffer
	cmd.Stdout = &stdout
	if err := cmd.Run(); err != nil {
		return -1
	}

	index, err := parseReliabilityJSON(stdout.Bytes())
	if err != nil {
		return -1
	}
	return index
}

func parseReliabilityJSON(data []byte) (float64, error) {
	trimmed := bytes.TrimSpace(data)
	if len(trimmed) == 0 || bytes.Equal(trimmed, []byte("null")) {
		return -1, nil
	}

	var raw map[string]interface{}
	if err := json.Unmarshal(trimmed, &raw); err != nil {
		return 0, fmt.Errorf("unmarshal reliability JSON: %w", err)
	}

	value, ok := raw["SystemStabilityIndex"]
	if !ok {
		return -1, nil
	}

	switch typed := value.(type) {
	case float64:
		return typed, nil
	case string:
		parsed, err := strconv.ParseFloat(strings.TrimSpace(typed), 64)
		if err != nil {
			return 0, err
		}
		return parsed, nil
	default:
		return 0, fmt.Errorf("unsupported reliability type %T", value)
	}
}
