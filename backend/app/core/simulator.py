import time
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The task prompt", default="Unknown Task")
    args = parser.parse_args()

    steps = [
        f"[START] Processing: {args.prompt[:30]}...",
        "[THINKING] Analyzing context...",
        "[THINKING] Identifying resources...",
        "[ACTION] creating file...",
        "[ACTION] writing code...",
        "[SUCCESS] Task execution finished."
    ]

    for step in steps:
        print(step)
        sys.stdout.flush()
        time.sleep(1)

if __name__ == "__main__":
    main()
