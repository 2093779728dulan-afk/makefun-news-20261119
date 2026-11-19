#!/usr/bin/env python3
import os
import shutil

def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(output_dir, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, "assets", "entry.png")
    dst = os.path.join(output_dir, "entry.png")

    with open(src, "rb") as fsrc:
        data = fsrc.read()

    with open(dst, "wb") as fdst:
        fdst.write(data)

    print(f"Copied {len(data)} bytes to {dst}")

if __name__ == "__main__":
    main()