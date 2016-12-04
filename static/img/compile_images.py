# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import subprocess
from os import path

from PIL import Image


DIRNAME = path.abspath(path.dirname(__file__))


def make_white(filename, output_dir):
	shaders = [
		lambda i: 255,
		lambda i: 255,
		lambda i: 255,
		lambda i: i,
	]
	process_image(filename, shaders, output_dir)


def process_image(filename, shaders, output_dir):
	output_filename = path.join(output_dir, path.basename(filename))
	im = Image.open(filename)
	im = im.convert("RGBA")
	sources = im.split()
	result = []
	for shader, source in zip(shaders, sources):
		result.append(source.point(shader))
	result_image = Image.merge(im.mode, result)
	result_image.save(output_filename)
	subprocess.call(['pngout-static', '-k0', output_filename])
	subprocess.call(['advpng', '-z', '-4', output_filename])
	subprocess.call(['optipng', '-o7', output_filename])


def main():
	input_files = glob.glob(path.join(DIRNAME, 'black', '*.png'))
	white_dir = path.join(DIRNAME, 'white')
	for filename in input_files:
		make_white(filename, white_dir)


if __name__ == "__main__":
	main()
