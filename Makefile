.PHONY: build build-windows package-windows-release test lint

build:
	go build -o bin/sentinel ./cmd/sentinel

build-windows:
	GOOS=windows GOARCH=amd64 go build -o bin/sentinel.exe ./cmd/sentinel

package-windows-release:
	./scripts/package_windows_release.sh

test:
	go test ./... -v -count=1

lint:
	go fmt ./...
	go vet ./...
