import fileinput
import json


ID = {"dummy": __file__}


def main():
    with fileinput.input(encoding="utf-8") as f:
        for line in f:
            stdin = json.loads(line)
            print("Received:", repr(stdin))


if __name__ == "__main__":
    main()
