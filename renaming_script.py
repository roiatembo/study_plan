import os


def plan_renames(basepath, file_type, splitter):
    """
    Work out the zero-padding needed for each module folder so that files
    numbered 1, 2, 3 ... sort correctly next to 10, 11, 100, etc.

    Returns a list of (old_path, new_path) tuples. Files whose name doesn't
    start with a numeric token (before `splitter`) are left untouched.
    """
    if not os.path.isdir(basepath):
        raise FileNotFoundError(f"Directory not found: {basepath}")

    renames = []
    list_dir = sorted(os.listdir(basepath))

    for folder in list_dir:
        full_path = os.path.join(basepath, folder)
        if not os.path.isdir(full_path):
            continue

        matching_files = [
            f for f in sorted(os.listdir(full_path)) if f.endswith(file_type)
        ]

        # Figure out the numeric prefix (if any) for every matching file,
        # and the widest one determines the padding width for the folder.
        parsed = []
        max_width = 0
        for file_name in matching_files:
            token = file_name.split(splitter)[0]
            if token.isdigit():
                parsed.append((file_name, token))
                max_width = max(max_width, len(token))
            else:
                parsed.append((file_name, None))

        if max_width == 0:
            continue  # nothing numeric to pad in this folder

        for file_name, token in parsed:
            if token is None:
                continue
            padded_token = token.zfill(max_width)
            if padded_token == token:
                continue  # already correctly padded
            rest = file_name[len(token):]
            new_name = padded_token + rest
            renames.append((
                os.path.join(full_path, file_name),
                os.path.join(full_path, new_name),
            ))

    return renames


def apply_renames(renames):
    successes, failures = [], []
    for old_path, new_path in renames:
        if os.path.exists(new_path):
            failures.append((old_path, new_path, "target filename already exists"))
            continue
        try:
            os.rename(old_path, new_path)
            successes.append((old_path, new_path))
        except OSError as exc:
            failures.append((old_path, new_path, str(exc)))
    return successes, failures


if __name__ == "__main__":
    file_type = input("Which file extension would you like to rename (e.g. .mp4): ").strip()
    basepath = input("Enter full file path: ").strip()
    splitter = input("What splitting character is used before the number, '.' or '-': ").strip()

    try:
        renames = plan_renames(basepath, file_type, splitter)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    if not renames:
        print("Nothing to rename -- all matching files are already consistently numbered.")
        raise SystemExit(0)

    print(f"\n{len(renames)} file(s) will be renamed:")
    for old_path, new_path in renames:
        print(f"  {os.path.basename(old_path)}  ->  {os.path.basename(new_path)}")

    confirm = input("\nProceed with these renames? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled, no files were changed.")
        raise SystemExit(0)

    successes, failures = apply_renames(renames)

    print(f"\nRenamed {len(successes)} file(s) successfully.")
    if failures:
        print(f"{len(failures)} file(s) could NOT be renamed:")
        for old_path, new_path, reason in failures:
            print(f"  {os.path.basename(old_path)}: {reason}")