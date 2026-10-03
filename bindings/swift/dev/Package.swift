// swift-tools-version: 6.3
import PackageDescription

let package = Package(
  name: "Radroots",
  platforms: [.macOS("11.0"), .iOS("13.0")],
  products: [
    .library(name: "Radroots", targets: ["Radroots"])
  ],
  targets: [
    .binaryTarget(name: "RadrootsNative", path: "Radroots.xcframework"),
    .executableTarget(
      name: "PrintName", dependencies: ["Radroots"], path: "Tests/Fixtures/PrintName"),
    .testTarget(
      name: "RadrootsTests", dependencies: ["Radroots", "PrintName"], path: "Tests/RadrootsTests"
    ),
    .target(
      name: "RadrootsBindings", dependencies: ["RadrootsNative"],
      path: "Sources/RadrootsBindings", sources: ["RadrootsBindings.swift"]),
    .target(name: "Radroots", dependencies: ["RadrootsBindings"], path: "Sources/Radroots"),
  ]
)
