import pickle
import sys


ID = {
    "sympy": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "python"}},
    "sympy-gmpy": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "gmpy"}},
    "sympy-flint": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "flint"}},
}


def main():
    stdin = pickle.load(sys.stdin.buffer)
    print("sympy received:", stdin, file=sys.stderr)


if __name__ == "__main__":
    import sympy  # noqa: F401
    main()
