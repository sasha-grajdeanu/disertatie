import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from venus import run_venus, run_test_generator


def main() -> None:
    parser = argparse.ArgumentParser(description="Venus Language CLI")
    parser.add_argument("file", help="Path to the .venus file to run")
    parser.add_argument(
        "-s",
        "--scenarios",
        action="store_true",
        help="Run in scenario generation mode (using cAutoTest)",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=3,
        help="Loop unrolling depth for symbolic test generation (default: 3)",
    )
    parser.add_argument(
        "-p",
        "--post",
        type=str,
        default=None,
        help=(
            "Postcondition to verify on all safe symbolic paths, "
            "in Python syntax (e.g. \"result >= 0\"). "
            "Use variable names as they appear in the Venus source."
        ),
    )

    args = parser.parse_args()

    if args.scenarios:
        run_test_generator(args.file, args.depth, args.post)
    else:
        run_venus(args.file)


if __name__ == "__main__":
    main()
