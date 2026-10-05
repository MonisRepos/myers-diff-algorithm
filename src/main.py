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
# Myers Diff
# ============================================================

def myers_diff(a, b):
    """
    Find the shortest edit script that transforms sequence a
    into sequence b.

    Returns operations of the form:

        ("equal", item)
        ("delete", item)
        ("insert", item)

    Myers uses:
        k = x - y

    where:
        x = position in sequence a
        y = position in sequence b
    """

    n = len(a)
    m = len(b)

    # --------------------------------------------------------
    # Fast cases
    # --------------------------------------------------------

    if n == 0:
        return [("insert", item) for item in b]

    if m == 0:
        return [("delete", item) for item in a]

    if a == b:
        return [("equal", item) for item in a]

    # --------------------------------------------------------
    # V[k] stores the furthest x-coordinate reached on
    # diagonal k.
    #
    # k = x - y
    #
    # Dictionary is used because k can be negative.
    # --------------------------------------------------------

    v = {1: 0}

    # We save V after every D layer.
    # This is needed later for backtracking.
    trace = []

    max_d = n + m

    # --------------------------------------------------------
    # D = number of edits made so far.
    #
    # For every D, we examine the possible diagonals:
    #
    # -D, -D+2, ..., D-2, D
    # --------------------------------------------------------

    for d in range(max_d + 1):

        for k in range(-d, d + 1, 2):

            # ------------------------------------------------
            # Choose whether to come from:
            #
            # k + 1 -> insertion
            # k - 1 -> deletion
            #
            # We choose the path that reaches farther in x.
            # ------------------------------------------------

            if k == -d:
                # Cannot come from k - 1.
                x = v.get(k + 1, 0)

            elif k == d:
                # Cannot come from k + 1.
                x = v.get(k - 1, 0) + 1

            elif v.get(k - 1, -1) < v.get(k + 1, -1):
                # Coming from k + 1 reaches farther.
                x = v.get(k + 1, 0)

            else:
                # Coming from k - 1 reaches farther.
                x = v.get(k - 1, 0) + 1

            # Since k = x - y:
            y = x - k

            # ------------------------------------------------
            # Snake:
            #
            # Once we make an insertion/deletion, continue
            # diagonally while the elements are equal.
            # ------------------------------------------------

            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            # Store the furthest x for this diagonal.
            v[k] = x

            # ------------------------------------------------
            # If we reached the end of both sequences, we
            # found the shortest edit script.
            # ------------------------------------------------

            if x >= n and y >= m:

                # Save the completed D layer.
                trace.append(v.copy())

                return backtrack(a, b, trace, d)

        # Save V after this complete D layer.
        trace.append(v.copy())

    return []


def backtrack(a, b, trace, final_d):
    """
    Reconstruct the edit script by walking backwards through
    the V arrays saved by Myers' algorithm.
    """

    x = len(a)
    y = len(b)

    operations = []

    # --------------------------------------------------------
    # Start at the bottom-right corner (N, M) and move
    # backwards until we reach (0, 0).
    # --------------------------------------------------------

    for d in range(final_d, 0, -1):

        v = trace[d]

        # Current diagonal.
        k = x - y

        # ----------------------------------------------------
        # Find the previous diagonal.
        # ----------------------------------------------------

        if k == -d:
            previous_k = k + 1

        elif k == d:
            previous_k = k - 1

        elif v.get(k - 1, -1) < v.get(k + 1, -1):
            previous_k = k + 1

        else:
            previous_k = k - 1

        # ----------------------------------------------------
        # Get the previous position.
        # ----------------------------------------------------

        previous_x = trace[d - 1].get(previous_k, 0)
        previous_y = previous_x - previous_k

        # ----------------------------------------------------
        # Walk backwards through the snake.
        #
        # These are equal elements.
        # ----------------------------------------------------

        while x > previous_x and y > previous_y:
            x -= 1
            y -= 1

            operations.append(("equal", a[x]))

        # ----------------------------------------------------
        # One edit remains.
        #
        # If x did not change:
        #     insertion
        #
        # Otherwise:
        #     deletion
        # ----------------------------------------------------

        if x == previous_x:

            y -= 1

            operations.append(("insert", b[y]))

        else:

            x -= 1

            operations.append(("delete", a[x]))

    # --------------------------------------------------------
    # Any remaining elements before the first edit are equal.
    # --------------------------------------------------------

    while x > 0 and y > 0:

        x -= 1
        y -= 1

        operations.append(("equal", a[x]))

    # Remaining elements in a are deletions.
    while x > 0:

        x -= 1

        operations.append(("delete", a[x]))

    # Remaining elements in b are insertions.
    while y > 0:

        y -= 1

        operations.append(("insert", b[y]))

    # We constructed the operations backwards.
    operations.reverse()

    return operations


# ============================================================
# Main
# ============================================================

def main():

    if len(sys.argv) != 4:
        return 2

    path_a = sys.argv[2]
    path_b = sys.argv[3]

    old_lines = read_bytes_lines(path_a)
    new_lines = read_bytes_lines(path_b)

    if old_lines is None or new_lines is None:
        return 2

    operations = myers_diff(old_lines, new_lines)

    for operation, value in operations:
        print(operation, value)

    return 0


if __name__ == "__main__":
    sys.exit(main())