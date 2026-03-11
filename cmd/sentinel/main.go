package main

import (
	"fmt"
	"log"
	"os"

	"github.com/kardianos/service"
)

var svcConfig = &service.Config{
	Name:        "LogSentinelAiknow",
	DisplayName: "Log Sentinel Aiknow",
	Description: "Collects Windows logs and metrics for centralized monitoring.",
}

func main() {
	if err := loadLocalConfig(); err != nil {
		log.Fatalf("[LogSentinel] Config error: %v", err)
	}

	if len(os.Args) > 1 && os.Args[1] == "run-once" {
		if err := runOnce(); err != nil {
			log.Fatalf("[LogSentinel] Run-once error: %v", err)
		}
		return
	}

	program, err := newProgram()
	if err != nil {
		log.Fatalf("[LogSentinel] Init error: %v", err)
	}

	svc, err := service.New(program, svcConfig)
	if err != nil {
		log.Fatalf("[LogSentinel] Service init error: %v", err)
	}

	if len(os.Args) > 1 {
		if err := handleServiceCommand(svc, os.Args[1]); err != nil {
			log.Fatalf("[LogSentinel] Service command error: %v", err)
		}
		return
	}

	if err := svc.Run(); err != nil {
		log.Fatalf("[LogSentinel] Run error: %v", err)
	}
}

func handleServiceCommand(svc service.Service, command string) error {
	switch command {
	case "install":
		return svc.Install()
	case "uninstall":
		return svc.Uninstall()
	case "start":
		return svc.Start()
	case "stop":
		return svc.Stop()
	case "status":
		status, err := svc.Status()
		if err != nil {
			return err
		}
		fmt.Println(formatServiceStatus(status))
		return nil
	default:
		return fmt.Errorf("unknown command %q", command)
	}
}

func formatServiceStatus(current service.Status) string {
	switch current {
	case service.StatusRunning:
		return "running"
	case service.StatusStopped:
		return "stopped"
	case service.StatusUnknown:
		return "unknown"
	default:
		return fmt.Sprintf("status(%d)", current)
	}
}
