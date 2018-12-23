import os
import hashlib


def get_files_recursively(root_dir):
    print('root dir is: ', root_dir)
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            yield os.path.join(root, file)


def get_md5(fn):
    m = hashlib.md5()
    m.update(open(fn, 'rb').read())
    return m.hexdigest()


def yield_md5_in_folder(root_dir):
    for fn in get_files_recursively(root_dir):
        yield fn, get_md5(fn)


if __name__ == '__main__':
    root_dir = r''
    result_file = r''

    with open(result_file, 'w', encoding='utf-8') as f:
        for r in yield_md5_in_folder(root_dir):
            print(r)
            f.write(str(r) + '\n')
