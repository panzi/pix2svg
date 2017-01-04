#!/usr/bin/env python3

from PIL import Image

def pix2svg(pixfile, svgfile):
	im = Image.open(pixfile, 'r')
	pix = im.load()
	width, height = im.size

	svgfile.write('''\
<?xml version="1.0" encoding="UTF-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
  width="{width}" height="{height}" viewBox="0 0 {width} {height}">
'''.format(width=width, height=height))

	for y in range(height):
		for x in range(width):
			r, g, b, a = pix[x, y]
			if a > 0:
				svgfile.write('''\
  <rect style="fill:{color};fill-opacity:{alpha};" width="1" height="1" x="{x}" y="{y}" />
'''.format(color='#%02x%02x%02x' % (r, g, b), alpha=255.0 / a, x=x, y=y))

	svgfile.write('''\
</svg>
''')

def main(args):
	if len(args) > 0:
		pixfile = open(args[0], 'rb')
	else:
		pixfile = sys.stdin

	if len(args) > 1:
		svgfile = open(args[1], 'w')
	else:
		svgfile = sys.stdout
	
	with pixfile, svgfile:
		pix2svg(pixfile, svgfile)

if __name__ == '__main__':
	import sys
	main(sys.argv[1:])
