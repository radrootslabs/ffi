// swift-tools-version: 6.3
import PackageDescription

let package = Package(
  name: "RadrootsConsumerTests",
  platforms: [.macOS("11.0"), .iOS("13.0")],
  dependencies: [.package(name: "radroots_ffi", path: "../package")],
  targets: [
    .executableTarget(
      name: "PrintName", dependencies: [.product(name: "Radroots", package: "radroots_ffi")]),
    .testTarget(
      name: "RadrootsTests", dependencies: [.product(name: "Radroots", package: "radroots_ffi")]),
  ]
)
