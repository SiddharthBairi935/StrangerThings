using Xunit;

public class CalculatorTests
{
    [Fact]
    public void AddsTwoNumbers()
    {
        Assert.Equal(42, 20 + 22);
    }
}