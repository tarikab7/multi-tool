import sys

def main():
    try:
        with open('tools/duplicate_finder.py', 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                print(f"{i+1}: {line}", end="")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
