import fileinput
import pickle
import sys


ID = {"dummy": __file__}


def main():
    stdin = pickle.load(sys.stdin.buffer)
    print("Received:", stdin)


if __name__ == "__main__":
    main()
