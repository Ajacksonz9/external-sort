import argparse
import heapq
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


def read_part(file, limit):
    nums = []

    for _ in range(limit):
        line = file.readline()

        if not line:
            break

        line = line.strip()

        if line:
            nums.append(int(line))

    return nums


def save_numbers(filename, nums):
    with open(filename, "w", encoding="utf-8") as f:
        for x in nums:
            f.write(str(x) + "\n")


def sort_file(filename):
    nums = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                nums.append(int(line))

    nums.sort()
    save_numbers(filename, nums)

    return filename


def make_chunks(input_file, max_numbers, temp_dir):
    cpu_count = os.cpu_count() or 1
    part_size = max(1, max_numbers // cpu_count)

    temp_files = []
    tasks = []

    with open(input_file, "r", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=cpu_count) as executor:
            index = 0

            while True:
                nums = read_part(f, part_size)

                if not nums:
                    break

                chunk_name = temp_dir / f"chunk_{index}.txt"
                save_numbers(chunk_name, nums)

                temp_files.append(chunk_name)
                tasks.append(executor.submit(sort_file, str(chunk_name)))

                index += 1

            for task in tasks:
                task.result()

    return temp_files


def read_number(file):
    while True:
        line = file.readline()

        if not line:
            return None

        line = line.strip()

        if line:
            return int(line)


def merge_group(files, output_file):
    opened = []
    heap = []

    try:
        for i, filename in enumerate(files):
            f = open(filename, "r", encoding="utf-8")
            opened.append(f)

            value = read_number(f)

            if value is not None:
                heapq.heappush(heap, (value, i))

        with open(output_file, "w", encoding="utf-8") as out:
            while heap:
                value, file_index = heapq.heappop(heap)
                out.write(str(value) + "\n")

                next_value = read_number(opened[file_index])

                if next_value is not None:
                    heapq.heappush(heap, (next_value, file_index))

    finally:
        for f in opened:
            f.close()


def merge_all(files, result_file, temp_dir, max_numbers):
    if not files:
        Path(result_file).touch()
        return

    max_open_files = min(max_numbers, 256)
    max_open_files = max(2, max_open_files)

    current_files = files
    step = 0

    while len(current_files) > 1:
        new_files = []

        for i in range(0, len(current_files), max_open_files):
            group = current_files[i:i + max_open_files]
            merged_name = temp_dir / f"merge_{step}_{i}.txt"

            merge_group(group, merged_name)
            new_files.append(merged_name)

            for old_file in group:
                old_file.unlink(missing_ok=True)

        current_files = new_files
        step += 1

    current_files[0].replace(result_file)


def external_sort(filename, max_numbers):
    input_file = Path(filename)

    if not input_file.exists():
        raise FileNotFoundError("Input file not found")

    if max_numbers <= 0:
        raise ValueError("Second argument must be positive")

    result_file = input_file.with_name(input_file.stem + "_sorted" + input_file.suffix)

    with tempfile.TemporaryDirectory(dir=input_file.parent) as temp_name:
        temp_dir = Path(temp_name)

        chunks = make_chunks(input_file, max_numbers, temp_dir)
        merge_all(chunks, result_file, temp_dir, max_numbers)

    return result_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("max_numbers", type=int)

    args = parser.parse_args()

    result = external_sort(args.filename, args.max_numbers)

    print("Sorted file created:", result)


if __name__ == "__main__":
    main()
