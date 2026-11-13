<?php
declare(strict_types=1);

function addNumbers(int $left, int $right): int
{
    return $left + $right;
}

if (addNumbers(20, 22) !== 42) {
    fwrite(STDERR, "PHP smoke test failed\n");
    exit(1);
}

echo "PHP smoke test passed\n";