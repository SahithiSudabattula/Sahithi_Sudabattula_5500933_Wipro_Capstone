import subprocess
import sys


def main():
    command = ["behave"]
    if len(sys.argv) > 1:
        command.extend(sys.argv[1:])
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()

