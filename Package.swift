// swift-tools-version: 6.3
import PackageDescription

let package = Package(
  name: "Radroots",
  platforms: [.macOS("11.0"), .iOS("13.0")],
  products: [
    .library(name: "Radroots", targets: ["Radroots"])
  ],
  targets: [
    .binaryTarget(
      name: "RadrootsNative",
      path: "build/swift/Radroots.xcframework"),
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
