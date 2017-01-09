pix2svg
=======

Convert pixle art to SVG.

The difference to other such convertors is that this joins all
the pixels of the same color in one path and removes all the
superfluous vertices.

![](http://i.imgur.com/VHPuQvc.png)

As you can see the glasses are one single path with only two
vertices making the top edge.

Usage
-----

	usage: pix2svg.py [-h] [--no-optimize] [input] [output]
	
	Convert pixle art to SVG.
	
	positional arguments:
	  input
	  output
	
	optional arguments:
	  -h, --help     show this help message and exit
	  --no-optimize  Don't optimize generated paths.
