# External Merge Sort

This project implements external merge sort for large text files containing integers.

The program:
- splits the file into smaller chunks
- sorts each chunk separately
- stores sorted chunks in temporary files
- merges all sorted chunks into one final sorted file

Multiprocessing is used to utilize all available CPU cores.

## Files

- external_sort.py — main program
- check_sorted.py — checks if the output file is sorted

## Run

```bash
python external_sort.py random_numbers.txt 5000000
```