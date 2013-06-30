curlib
======

This is a small Python library for creating static and animated Windows cursors. I wrote 
it back in 2005 to generate animated cursors while working in Linux.

The actual heavy lifting is done in curlib, while anicursor is a front-end to generate 
animated cursors based off of a config file. The config file uses YAML to describe the
format:

  hotspot: [6,3]	# Default location of the cursor hotspot; not actually used (yet).
  author: J. Random User
  name: Name of animated icon
  defaultjif: 10	# Default time between frames; no way to specify for individual frames yet.
  frames:
    - hotspot: [6,3]
      bitrate: 24
      src: /path/to/frame/1.png
    - hotspot: [6,3]
      bitrate: 24
      src: /path/to/frame/2.png
    # And so on

