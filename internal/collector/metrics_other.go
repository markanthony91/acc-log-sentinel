//go:build !windows

package collector

func defaultDiskPath() string {
	return "/"
}
