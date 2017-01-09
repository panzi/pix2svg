#!/usr/bin/env python3

import sys
from PIL import Image
from array import array
import argparse

TOP_LEFT     = 1
TOP_RIGHT    = 2
BOTTOM_RIGHT = 4
BOTTOM_LEFT  = 8

CORNERS = [TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT]

STATE = {         # next corner, delta x/y, neighbours
	TOP_LEFT:     (TOP_RIGHT,    (0, 0),    [(( 0, -1), BOTTOM_LEFT),  ((-1, -1), BOTTOM_RIGHT), ((-1,  0), TOP_RIGHT)]),
	TOP_RIGHT:    (BOTTOM_RIGHT, (1, 0),    [(( 1,  0), TOP_LEFT),     (( 1, -1), BOTTOM_LEFT),  (( 0, -1), BOTTOM_RIGHT)]),
	BOTTOM_RIGHT: (BOTTOM_LEFT,  (1, 1),    [(( 0,  1), TOP_RIGHT),    (( 1,  1), TOP_LEFT),     (( 1,  0), BOTTOM_LEFT)]),
	BOTTOM_LEFT:  (TOP_LEFT,     (0, 1),    [((-1,  0), BOTTOM_RIGHT), ((-1,  1), TOP_RIGHT),    (( 0,  1), TOP_LEFT)]),
}

class CornerSet(object):
	__slots__ = '_array', 'width', 'height'

	def __init__(self, width, height):
		self.width  = width
		self.height = height
		self._array = array('b', (0 for _ in range(width * height)))

	def visit(self, x, y, corner):
		self._array[self.width * y + x] |= corner

	def visited(self, x, y, corner):
		return bool(self._array[self.width * y + x] & corner)

def isline(p1, p2, p3):
	x1, y1 = p1
	x2, y2 = p2
	x3, y3 = p3

	if x1 == x2 and x2 == x3:
		return True

	if y1 == y2 and y2 == y3:
		return True

	return False

def optimize_subpath(subpath):
	if len(subpath) < 3:
		return subpath

	it = iter(subpath)
	p1 = start = next(it)
	p2 = next(it)

	optpath = [p1]

	for p3 in it:
		if not isline(p1, p2, p3):
			optpath.append(p2)

		p1 = p2
		p2 = p3

	if not isline(p1, p2, start):
		optpath.append(p2)

	return optpath

def pix2svg(pixfile, svgfile, optimize=True):
	im = Image.open(pixfile, 'r')
	pix = im.load()
	width, height = im.size

	def get_col(x, y):
		if x < 0 or y < 0 or x >= width or y >= height:
			return None
		return pix[x, y]

	cset = CornerSet(width, height)
	paths_by_color = {}

	def build_subpath(color, x, y, corner):
		subpath = []

		while not cset.visited(x, y, corner):
			cset.visit(x, y, corner)
			next_corn, (dx, dy), neighbours = STATE[corner]
			((dx1, dy1), corn1), ((dx2, dy2), corn2), ((dx3, dy3), corn3) = neighbours

			x1, y1 = x + dx1, y + dy1
			x2, y2 = x + dx2, y + dy2
			x3, y3 = x + dx3, y + dy3

			c1 = get_col(x1, y1)
			c2 = get_col(x2, y2)
			c3 = get_col(x3, y3)

			# 21
			# 3X
			if color == c1:
				if color == c2:
					if color == c3:
						# ##
						# #X
						break
					else:
						# ##
						# .X
						x = x2
						y = y2
						corner = corn2
				else:
					# .#
					# ?X
					x = x1
					y = y1
					corner = corn1
			else:
				# ?. 
				# ?X
				subpath.append((x + dx, y + dy))
				corner = next_corn

		return subpath

	for y in range(height):
		for x in range(width):
			color = pix[x, y]
			if color[3] > 0:
				if color in paths_by_color:
					path = paths_by_color[color]
				else:
					path = paths_by_color[color] = []

				for corner in CORNERS:
					subpath = build_subpath(color, x, y, corner)
					if subpath:
						path.append(subpath)

	if optimize:
		paths = [(color, [optimize_subpath(subpath) for subpath in path])
			for color, path in paths_by_color.items()]
	else:
		paths = list(paths_by_color.items())

	svgfile.write('''\
<?xml version="1.0" encoding="UTF-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
  width="{width}px" height="{height}px" viewBox="0 0 {width} {height}">
  <defs />
  <g style="fill-rule:evenodd;">
'''.format(width=width, height=height))

	for color, path in paths:
		alpha = color[3]
		strcolor = '#%02x%02x%02x' % color[:3]
		strpath = ' '.join(
			'M%d %d %sZ' % (
				subpath[0][0], subpath[0][1], ''.join(
					'L%d %d ' % point for point in subpath[1:]))
			for subpath in path)

		if alpha < 1.0:
			svgfile.write('''\
    <path fill="{color}" d="{path}" opacity="{alpha}" />
'''.format(color=strcolor, path=strpath, alpha=255.0 / alpha))
		else:
			svgfile.write('''\
    <path fill="{color}" d="{path}" />
'''.format(color=strcolor, path=strpath))

	svgfile.write('''\
  </g>
</svg>
''')

def main(args):
	parser = argparse.ArgumentParser(description='Convert pixle art to SVG.')
	parser.add_argument('--no-optimize', dest='optimize', action='store_false',
		help="Don't optimize generated paths.")
	parser.set_defaults(optimize=True)

	parser.add_argument('input', type=argparse.FileType('rb'), default=sys.stdin, nargs='?')
	parser.add_argument('output', type=argparse.FileType('w'), default=sys.stdout, nargs='?')

	opts = parser.parse_args(args)

	with opts.input, opts.output:
		pix2svg(opts.input, opts.output, opts.optimize)

if __name__ == '__main__':
	main(sys.argv[1:])
