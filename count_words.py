import argparse

def count_words_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            words = content.split()
            return len(words)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Count the number of words in a text file.')
    parser.add_argument('file', type=str, help='Path to the text file')
    args = parser.parse_args()

    word_count = count_words_in_file(args.file)
    if word_count is not None:
        print(f"Word count: {word_count}")

if __name__ == '__main__':
    main()