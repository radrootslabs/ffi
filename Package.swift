// swift-tools-version: 6.3
import PackageDescription

let releaseTag = "v0.0.0"
let releaseChecksum = "7c53506222541666e84040f2ce6e4370e77f8d2be0a8a9152802deb5fff0b9ed"

let package = Package(
  name: "Radroots",
  platforms: [.macOS("11.0"), .iOS("13.0")],
  products: [
    .library(name: "Radroots", targets: ["Radroots"])
  ],
  targets: [
    .binaryTarget(
      name: "RadrootsNative",
      url:
        "https://github.com/radrootslabs/ffi/releases/download/\(releaseTag)/Radroots.xcframework.zip",
      checksum: releaseChecksum),
    .executableTarget(
      name: "PrintName", dependencies: ["Radroots"],
      path: "bindings/swift/Tests/Fixtures/PrintName"),
    .testTarget(
      name: "RadrootsTests", dependencies: ["Radroots", "PrintName"],
      path: "bindings/swift/Tests/RadrootsTests"),
    .target(
      name: "RadrootsBindings", dependencies: ["RadrootsNative"],
      path: "bindings/swift/Sources/RadrootsBindings", sources: ["RadrootsBindings.swift"]),
    .target(
      name: "Radroots", dependencies: ["RadrootsBindings"],
      path: "bindings/swift/Sources/Radroots"),
  ]
)
