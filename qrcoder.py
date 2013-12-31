import logging
import sys
from argparse import ArgumentParser
from os import mkdir, listdir
from os.path import (exists as path_exists, join as join_paths,
    isdir as path_is_dir)

from PIL import ImageFont, ImageDraw, ImageOps, Image
from qrcode import QRCode, constants
from qrcode.exceptions import DataOverflowError


log = logging.getLogger('qrcoder')


PACKAGE_URL = 'http://app.seedtabs.com/packages/{code}?type={type}'


QR_FILE_FORMAT = '{code}.png'



FONT = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/verdana.ttf", 12) #Will's Computer
#FONT = ImageFont.truetype("/usr/share/fonts/corefonts/cour.ttf", 12) #Ian's Computer



# This is a completely made up estimate of the height of text
# rendered with the prior `FONT` variable's font.
# Pillow's text size method does not return a correct height.
FONT_HEIGHT = 14


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
        box_size = 3
        border = 4
        qr = QRCode(
            version=expected_version,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(package_url)
        qr.make(fit=True)
        if qr.version != expected_version:
            log.warn(errors['overflow'].format(code=code))
        qr_image = qr.make_image()

        width, height = qr_image.size
        text_to_draw = '# {0}'.format(code)

        # Margin on the left and right of the qr code.
        qr_margin = border * box_size

        # Paste image onto a larger canvas to with room for text.
        img = Image.new("RGB",
            (width, height + FONT_HEIGHT), "white")
        img.paste(qr_image, (0, 0, width, height))

        # Start a drawing, draw on text.
        draw = ImageDraw.Draw(img)
        draw.text((qr_margin, height), text_to_draw, 0, font=FONT)

        # Save the image to a file as a PNG, JPG ruins quality.
        img_path = join_paths(output_dir, QR_FILE_FORMAT.format(code=code))
        img.save(img_path, 'PNG')
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
