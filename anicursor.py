#!/usr/bin/python
import Image
import sys
import curlib
from xml.dom.minidom import parse

if len(sys.argv) < 2:
	sys.exit("Usage: anicursor <config file>")
dom = parse(sys.argv[1])
el = dom.getElementsByTagName('hotspot').item(0)
hotspot = (int(el.attributes['x'].nodeValue), int(el.attributes['y'].nodeValue))
author = dom.getElementsByTagName('author').item(0).firstChild.nodeValue
name = dom.getElementsByTagName('name').item(0).firstChild.nodeValue
defaultjif = int(dom.getElementsByTagName('defaultjif').item(0).firstChild.nodeValue)
out_filename = dom.getElementsByTagName('cursor').item(0).attributes['dest'].nodeValue
cl = []
for (fn, bitrate, hotspot) in [(el.attributes['src'].nodeValue, int(el.attributes['bitrate'].nodeValue), (int(el.attributes['hotspotx'].nodeValue), int(el.attributes['hotspoty'].nodeValue))) for el in dom.getElementsByTagName('frame')]:
	im = Image.open(fn)
	c = curlib.CursorFile()
	ci = c.CursorImage(im.size[0], im.size[1], bitrate=bitrate)
	#ci.Image = im.getdata()

	ci.Image = im.transpose(Image.FLIP_TOP_BOTTOM).getdata()
	ci.Mask = [0] * (len(ci.Image) / 8)
	for i in xrange(len(ci.Image)):
		if ci.Image[i][3] < 128:
			ci.Mask[i >> 3] |= (128 >> (i & 0x07))
	
	c.cdEntries = [ c.CursorDirectoryEntry(im.size[0], im.size[1], hotspot, ci) ]
	cl.append(c)

f = open(out_filename, 'wb')
a = curlib.AnimatedCursorFile(author, name, cl, JifRate = defaultjif)
a.PrintFile(f)
