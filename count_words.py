#!/usr/bin/env python3
"""
count_words.py - A utility to count words in text files
"""
import sys
import re

def count_words(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            words = re.findall(r'\b\w+\b', content)
            return len(words)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return 0
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python count_words.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    word_count = count_words(filename)
    print(f"Word count: {word_count}")

if __name__ == "__main__":
    main()