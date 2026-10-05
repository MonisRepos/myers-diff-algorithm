import sys


# ============================================================
# File handling
# ============================================================

def read_bytes_lines(path):
    """
    Read a file as raw bytes and split it into lines using
    the newline byte b'\\n'.

    Important:
    - We do NOT use text mode.
    - \\r is kept as part of the line.
    - A final empty piece caused by a trailing \\n is removed.
    """

    try:
        with open(path, "rb") as f:
            data = f.read()
    except (OSError, IOError):
        return None

    lines = data.split(b"\n")

    # A final newline does not create an extra empty line.
    if lines and lines[-1] == b"":
        lines.pop()

    return lines


# ============================================================
# Main
# ============================================================

def main():
    """
    Temporary test for file handling.
    """

    if len(sys.argv) != 4:
        print(
            "Usage: python src/main.py "
            "<lines|highlight> A B",
            file=sys.stderr
        )
        return 2

    path_a = sys.argv[2]
    path_b = sys.argv[3]

    old_lines = read_bytes_lines(path_a)
    new_lines = read_bytes_lines(path_b)

    if old_lines is None or new_lines is None:
        print(
            "Error: could not read input file",
            file=sys.stderr
        )
        return 2

    print("Old file:")
    for line in old_lines:
        print(line)

    print("New file:")
    for line in new_lines:
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())