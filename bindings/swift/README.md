# Radroots Swift FFI library

Swift FFI library for Radroots. Version 0.0.0 is not published.

From the repository root, run `make build-swift` to build the local XCFramework
and staged development package. Run `make test-swift` for the Swift API tests or
`make test-swift-consumer` for an isolated consumer of the local ZIP.

The root `Package.swift` uses the versioned GitHub release XCFramework URL and
its exact checksum. That asset is not published yet. A local consumer uses the
staged development package:

```swift
.package(path: "/path/to/ffi/build/swift-dev")
```

After publication, use `.package(url: "https://github.com/radrootslabs/ffi.git",
exact: "0.0.0")` and the `Radroots` product from package `ffi`, then
`import Radroots`. The remote consumer fixture is under
`tests/consumers/swift-remote`; it is executed only during approved remote acceptance.
