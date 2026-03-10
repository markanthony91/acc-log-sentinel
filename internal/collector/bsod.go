package collector

import "github.com/aiknow/acc_log_sentinel/internal/models"

var bsodEventIDs = map[int]struct{}{
	41:   {},
	1001: {},
	6008: {},
}

func DetectBSOD(events []models.Event) bool {
	for _, event := range events {
		if _, ok := bsodEventIDs[event.EventID]; ok {
			return true
		}
	}
	return false
}
