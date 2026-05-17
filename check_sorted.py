prev = None

with open("random_numbers_sorted.txt", "r") as f:
    for line in f:
        num = int(line.strip())

        if prev is not None and num < prev:
            print("ERROR")
            break

        prev = num

print("SORTED OK")