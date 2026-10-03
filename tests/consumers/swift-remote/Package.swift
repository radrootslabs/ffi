// swift-tools-version: 6.3
import PackageDescription

let package = Package(
  name: "Consumer",
  platforms: [.macOS("11.0")],
  dependencies: [
    .package(url: "https://github.com/radrootslabs/ffi.git", exact: "0.0.0")
  ],
  targets: [
    .executableTarget(
      name: "Consumer", dependencies: [.product(name: "Radroots", package: "ffi")])
  ]
)
