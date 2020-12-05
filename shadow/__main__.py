import sys

from shadow.core import fib

if __name__ == "__main__":
    n = int(sys.argv[1])
    print(fib(n))
