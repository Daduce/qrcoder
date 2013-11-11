import logging
import sys
from argparse import ArgumentParser
from os import mkdir, listdir
from os.path import (exists as path_exists, join as join_paths,
    isdir as path_is_dir)

from qrcode import QRCode, constants
from qrcode.exceptions import DataOverflowError


log = logging.getLogger('qrcoder')


PACKAGE_URL = 'http://www.seed.io/packages/{code}?type={type}'


QR_FILE_FORMAT = '{code}.jpg'


def create_parser():
    parser = ArgumentParser(description='Generate qrcode images')
    parser.add_argument('--type', choices=['sample', 'normal'], required=True)
    parser.add_argument('--count', type=int, required=True,
        help='Generate this many identifiers.')
    parser.add_argument('--start', type=int, required=True,
        help='Start at this id.')
    parser.add_argument('--dir', required=True,
        help='Place images in this directory.')
    parser.add_argument('--debug', action='store_true',
        help='Display debugging messages.')
    return parser


def script_error(msg):
    log.error(msg)
    sys.exit(-1)


errors = {
    'overflow': """There was too much data for code {code}.
Therefore a larger qr code will be created."""
}


def generate_qr_codes(package_type, starting_code, count, output_dir):
    for code in range(starting_code, starting_code + count):
        package_url = PACKAGE_URL.format(code=code, type=package_type)
        expected_version = 3
        qr = QRCode(
            version=expected_version,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=3,
            border=4,
        )
        qr.add_data(package_url)
        qr.make(fit=True)
        if qr.version != expected_version:
            log.warn(errors['overflow'].format(code=code))
        img = qr.make_image()
        img_path = join_paths(output_dir, QR_FILE_FORMAT.format(code=code))
        img.save(img_path, 'JPEG')
        log.debug('Writing qr code with')
        log.debug('\t code {}\n\t dimensions {}\n\t url {}\n\t path {}.'.format(
            code, img.size, package_url, img_path))
    log.info('Generated {count} qr codes'.format(count=count))


def main():
    parser = create_parser()
    parse_result = parser.parse_args()
    if parse_result.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(stream=sys.stdout, level=level)
    if not path_exists(parse_result.dir):
        log.info('Creating directory {dir}'.format(dir=parse_result.dir))
        mkdir(parse_result.dir)
    if path_exists(parse_result.dir) and listdir(parse_result.dir):
        script_error('Path exists and is not empty: {}'.format(
            parse_result.dir))
    elif not path_is_dir(parse_result.dir):
        script_error('Path is not a directory: {}'.format(parse_result.dir))
    generate_qr_codes(parse_result.type, parse_result.start,
        parse_result.count, parse_result.dir)


if __name__ == '__main__':
    main()
