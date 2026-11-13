import kotlin.test.Test
import kotlin.test.assertEquals

class CalculatorTest {
    @Test
    fun addsTwoNumbers() {
        assertEquals(42, add(20, 22))
    }
}