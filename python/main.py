#!/usr/bin/env python3
import argparse
from runner import run_venus
from test_generator import run_test_generator

def main():
    parser = argparse.ArgumentParser(description="Venus Language CLI")
    parser.add_argument("file", help="Path to the .venus file to run")
    parser.add_argument("-s", "--scenarios", action="store_true", help="Run in scenario generation mode (using cAutoTest)")
    
    args = parser.parse_args()
    
    if args.scenarios:
        run_test_generator(args.file)
    else:
        run_venus(args.file)

if __name__ == "__main__":
    main()
