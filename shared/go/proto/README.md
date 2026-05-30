# Go Protocol Buffer Stubs

This directory would contain the generated Go protobuf files:
- `messages.pb.go` - Generated Go structs for messages
- `messages_grpc.pb.go` - Generated gRPC client and server code
- `services.pb.go` - Generated Go structs for service definitions  
- `services_grpc.pb.go` - Generated gRPC service code

## Generation

To generate these files, Go 1.21+ and the protoc-gen-go/protoc-gen-go-grpc plugins must be installed:

```bash
go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-go-grpc@latest
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest

protoc \
  -I. \
  --go_out=shared/go \
  --go-grpc_out=shared/go \
  shared/proto/*.proto
```

The Go environment was not available at generation time.
