# Radroots Go FFI library

Version 0.0.0 is unpublished. From the repository root, use `make setup-go` followed by `make test-go`
for local verification. Registry installation examples describe intended distributions.

Go FFI library for Radroots.

`make package-go` includes all tracked module files, including tests, and compares
the prepared archive with Go's pinned official module-ZIP implementation. The
local fixture adds only the eight prepared native archive/provenance files to
its source commit and verifies identical member bytes and `h1` checksums. This
check does not claim that a public tag or Go proxy release exists.

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
