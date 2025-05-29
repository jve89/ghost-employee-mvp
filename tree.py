# tree.py
import os
import sys

def tree(dir_path: str, prefix: str = ''):
    files = sorted(os.listdir(dir_path))
    for idx, file in enumerate(files):
        path = os.path.join(dir_path, file)
        connector = '└── ' if idx == len(files) - 1 else '├── '
        print(prefix + connector + file)
        if os.path.isdir(path):
            extension = '    ' if idx == len(files) - 1 else '│   '
            tree(path, prefix + extension)

if __name__ == '__main__':
    start_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(start_path)
    tree(start_path)
