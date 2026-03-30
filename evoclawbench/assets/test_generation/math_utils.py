"""Math utility functions."""


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number (0-indexed).

    fibonacci(0) = 0, fibonacci(1) = 1, fibonacci(2) = 1, fibonacci(3) = 2, ...

    Raises ValueError if n is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def is_prime(n: int) -> bool:
    """Check if n is a prime number.

    Returns False for numbers less than 2.
    """
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def gcd(a: int, b: int) -> int:
    """Compute the greatest common divisor of a and b using Euclid's algorithm.

    Works with negative numbers (returns a non-negative result).
    gcd(0, 0) returns 0.
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
