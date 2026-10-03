# Radroots Go FFI library

Version 0.0.0 is unpublished. From the repository root, use `make setup-go` followed by `make test-go`
for local verification. Registry installation examples describe intended distributions.

Go FFI library for Radroots.

```bash
go get github.com/radrootslabs/ffi/bindings/go@v0.0.0
```

```go
package main

import "github.com/radrootslabs/ffi/bindings/go"

func main() {
    radroots.PrintName()
}
```
