# Radroots Go FFI library

Go FFI library for Radroots.

The module path is `github.com/radrootslabs/ffi/bindings/go`.
Version tags use `bindings/go/v<version>`; distribution snapshots include the
native libraries required by cgo. The `master` branch contains source only.
See the repository's release notes for available versions.

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
