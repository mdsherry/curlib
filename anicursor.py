#!/usr/bin/python
import Image
import sys
import curlib
import yaml

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Create an animated cursor")
	parser.add_argument( "configfile", type=argparse.FileType("rt") )
	parser.add_argument("destination", type=argparse.FileType("wb"))

	args = parser.parse_args()
	config = yaml.load( args.configfile )
	hotspot = config['hotspot']
	author = config['author']
	name = config['name']
	defaultjif = config['defaultjif']

	cursors = []
	for frame in config['frames']:
		fn = frame['src']
		im = Image.open( fn )
		cursor = curlib.CursorFile()
		cursorImage = cursor.CursorImage(im.size[0], im.size[1], bitrate=frame['bitrate'])

		cursorImage.Image = im.transpose(Image.FLIP_TOP_BOTTOM).getdata()
		cursorImage.Mask = [0] * (len(cursorImage.Image) / 8)
		for i in xrange(len(cursorImage.Image)):
			if cursorImage.Image[i][3] < 128:
				cursorImage.Mask[i >> 3] |= (128 >> (i & 0x07))
		
		cursor.cdEntries = [ cursor.CursorDirectoryEntry(im.size[0], im.size[1], hotspot, cursorImage) ]
		cursors.append(cursor)

	
	a = curlib.AnimatedCursorFile(author, name, cursors, JifRate = defaultjif)
	a.PrintFile(args.destination)
