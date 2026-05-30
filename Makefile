.PHONY: proto build test clean help

help:
	@echo "Available targets:"
	@echo "  proto     - Generate gRPC code from .proto files"
	@echo "  build     - Build all Go binaries"
	@echo "  test      - Run all tests"
	@echo "  clean     - Remove build artifacts"

proto:
	@echo "Generating gRPC code..."
	protoc --go_out=. --go-grpc_out=. --python_out=. --pyi_out=. shared/proto/*.proto

build:
	@echo "Building Go binaries..."
	go build -o bin/queue-service ./queue/cmd/main.go
	go build -o bin/observability-service ./observability/cmd/main.go

test:
	@echo "Running tests..."
	pytest -v --cov=. --cov-report=html

clean:
	rm -rf bin/ dist/ __pycache__ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
