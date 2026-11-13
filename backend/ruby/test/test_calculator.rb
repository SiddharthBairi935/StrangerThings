require "minitest/autorun"
require_relative "../lib/calculator"

class CalculatorTest < Minitest::Test
  def test_adds_two_numbers
    assert_equal 42, add_numbers(20, 22)
  end
end