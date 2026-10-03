import Foundation
import Radroots
import XCTest

@MainActor
final class RadrootsTests: XCTestCase {
  func testIdentity() {
    XCTAssertEqual(Radroots.name, "Radroots")
    XCTAssertEqual(Radroots.projectName(), "Radroots")
  }

  func testRepeatedCalls() {
    for _ in 0..<1000 {
      XCTAssertEqual(Radroots.projectName(), "Radroots")
    }
  }

  func testConcurrentCalls() async {
    await withTaskGroup(of: Bool.self) { group in
      for _ in 0..<8 {
        group.addTask {
          (0..<128).allSatisfy { _ in Radroots.projectName() == "Radroots" }
        }
      }
      for await valid in group {
        XCTAssertTrue(valid)
      }
    }
  }

  #if os(macOS)
    func testPrintName() throws {
      let process = Process()
      process.executableURL = Bundle(for: RadrootsTests.self).bundleURL.deletingLastPathComponent()
        .appendingPathComponent("PrintName")
      let output = Pipe()
      process.standardOutput = output
      try process.run()
      process.waitUntilExit()
      XCTAssertEqual(process.terminationStatus, 0)
      XCTAssertEqual(
        String(decoding: output.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self),
        "Radroots\n")
    }
  #endif
}
