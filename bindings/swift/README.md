# Radroots Swift SDK

Swift SDK for Radroots. Version 0.0.0 is not published.

From the repository root, run `make build-swift` to build the local XCFramework
and staged development package. Run `make test-swift` for the Swift API tests or
`make test-swift-consumer` for an isolated consumer of the local ZIP.

The root `Package.swift` consumes `build/swift/Radroots.xcframework`. A local
consumer can use the staged package:

```swift
.package(path: "/path/to/ffi/build/swift-dev")
```
