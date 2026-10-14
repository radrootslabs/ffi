// swift-tools-version: 6.3
import PackageDescription

let releaseTag = "v0.0.0"
let releaseChecksum = "13f824dc2cf61977e877339bdb59e596b84399e73db85ec004bbbcd549f79898"

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
