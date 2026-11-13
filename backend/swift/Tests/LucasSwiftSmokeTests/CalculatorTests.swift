import XCTest
@testable import LucasSwiftSmoke

final class CalculatorTests: XCTestCase {
    func testAddsTwoNumbers() {
        XCTAssertEqual(Calculator.add(20, 22), 42)
    }
}