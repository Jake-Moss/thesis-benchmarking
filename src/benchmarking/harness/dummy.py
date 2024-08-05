import pickle
import sys


ID = {"dummy": {"file": __file__, "env": {}}}


def main():
    stdin = pickle.load(sys.stdin.buffer)
    print("Received:", stdin)


if __name__ == "__main__":
    main()
