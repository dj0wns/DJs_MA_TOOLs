import argparse
import os

from misc import BinaryIO
from mst import MST


def extract(mst_path, out_path, ignore_existing):
    br = BinaryIO(open(mst_path, 'rb'))

    mst = MST()
    mst.read(br)

    try:
        os.makedirs(out_path, exist_ok=True)
    except OSError:
        raise Exception("Couldn't create output path.")

    for file in mst.files:
        file_out_path = os.path.join(out_path, file.name)
        file_out_path = file_out_path.replace('.tga', '.dds')

        if os.path.isfile(file_out_path) and ignore_existing:
            print('Skipping {0.name}'.format(file))
            continue

        print('Writing {0.name} ({0.length} bytes) loader: {0.loader}'.format(file))
        out_handle = open(file_out_path, 'wb')
        file.loader.read(br)
        file.loader.save(out_handle)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mst', help="path to the Metal Arms .MST file")
    parser.add_argument('path', help="directory to put the extracted files in")
    parser.add_argument('--ignore-existing', dest='ignore_existing', action='store_true')
    parser.set_defaults(ignore_existing=False)
    args = parser.parse_args()
    extract(args.mst, args.path, args.ignore_existing)
