import struct
def IntToString(num, size=2):
	""" Takes a word or byte and returns its binary representation as a string """
	return  struct.pack('<%sB' % size, num)

def IntToFile(f, num, size=2):
	""" Takes a word or byte and prints its binary representation to a file """
	f.write(IntToString(num, size))

class AnimatedCursorFile:
	def __init__(self, author, name, icons, rate=None, seq=None, JifRate = 10):
		self.author = author
		self.name = name
		self.icons = icons
		self.rate = rate
		self.seq = seq
		self.JifRate = JifRate

	def GetSize(self):
		# Everything up to anih
		n_length = len(self.name) + 1
		a_length = len(self.author) + 1
		total = 32 + n_length + (n_length & 1) + a_length + (a_length & 1)
		# anih
		total += 44
		if self.rate:
			total += 8 + len(self.rate) * 4
		if self.seq:
			total += 8 + len(self.seq) * 4
		total += 12
		for i in self.icons:
			total += i.Size() + 8 #(i.cdEntries[0].Image.biWidth * i.cdEntries[0].Image.biHeight * (1 + i.cdEntries[0].Image.biBitCount))/ 8 + 70
			
		return total
	
	def PrintFile(self,f):
		f.write("RIFF")
		f.write(struct.pack('<I',self.GetSize())
		f.write("ACON")
		f.write("LIST")
		# Name must be null terminated
		name = self.name + '\x00'
		# Length includes null
		n_length = len(self.name) + 1
		# Must also be word aligned. Length does not include this.
		if n_length & 1:
			name += '\x00'
		# Author must be null terminated
		author = self.author + '\x00'
		# Length includes null
		a_length = len(self.author) + 1
		# Must also be word aligned. Length does not include this.
		if a_length & 1:
			author += '\x00'
		# Size of list goes here
		tot_length = n_length + (n_length & 1) + a_length + (a_length & 1) + 20
		f.write(struct.pack('<I4s4sI%ss4sI%ss' % (n_length, a_length), 
			tot_length, 'INFO', 'INAM', n_length, name, 'IART', a_length, author))
		f.write(struct.pack('<4sIII','anih',36,36,len(self.icons)))
		if self.rate:
			f.write(struct.pack('<I',len(self.rate))
		else:
			f.write(struct.pack('<I',len(self.icons))
			
		f.write(struct.pack('<IIIIII', 0,0,0,1,self.JifRate,1)

		# Rate and sequence, if available
		if self.rate:
			f.write('rate')
			IntToFile(f, len(self.rate) * 4, 4)
			for r in self.rate:
				IntToFile(f, r, 4)
		if self.seq:
			f.write('seq ')
			IntToFile(f, len(self.seq) * 4, 4)
			for s in self.seq:
				IntToFile(f, s, 4)
		# Now for the icons themselves
		f.write('LIST')
		# Size of the icon list
		total = 0
		for i in self.icons:
			# 8 extra because of the 'icon' + icon size
			total += i.Size() + 8 #(i.cdEntries[0].Image.biWidth * i.cdEntries[0].Image.biHeight * (1 + i.cdEntries[0].Image.biBitCount))/ 8 + 70
		IntToFile(f, 4 + total, 4)
		f.write('fram')
		for icon in self.icons:
			f.write('icon')
			IntToFile(f, icon.Size(), 4)
			icon.PrintHeader(f)

		
class CursorFile:
	def __init__(self):
		self.cdReserved = 0
		self.cdType = 2
		self.cdEntries = []

	def Size(self):
		total = 6
		for cd in self.cdEntries:
			total += 16 + cd.Image.NumBytes()
		return total
		
	def PrintHeader(self, f):
		IntToFile(f,self.cdReserved)
		IntToFile(f,self.cdType)
		IntToFile(f,len(self.cdEntries))
		for cd in enumerate(self.cdEntries):
			# Offset is 6 (basic header) plus 16 for each CD entry
			# Since we're indexing from zero here, we add the first 16
			# to the base offset to give us 22.
			cd[1].PrintHeader(f, cd[0] * 16 + 22)
		for cd in self.cdEntries:
			cd.Image.PrintImage(f)

	class CursorDirectoryEntry:
		def __init__(self, width, height, Hotspot, Image):
			self.bWidth = width
			self.bHeight = height
			self.bColorCount = 0
			self.bReserved = 0
			self.wXHotspot = Hotspot[0]
			self.wYHotspot = Hotspot[1]
			self.Image = Image

		def PrintHeader(self, f, ImageOffset):
			IntToFile(f, self.bWidth,1)
			IntToFile(f, self.bHeight,1)
			IntToFile(f, self.bColorCount,1)
			IntToFile(f, self.bReserved,1)
			IntToFile(f, self.wXHotspot)
			IntToFile(f, self.wYHotspot)
			IntToFile(f, self.Image.NumBytes(),4)
			IntToFile(f, ImageOffset,4)
		
	class CursorImage:
		def __init__(self, width, height, bitrate=32):
			self.biSize = 40
			self.biWidth = width
			self.biHeight = height
			self.biPlanes = 1
			self.biBitCount = bitrate
			self.biCompression = 0
			self.biSizeImage = (width*height*(bitrate+1))/8
			self.biXPelsPerMeter = 0
			self.biYPelsPerMeter = 0
			self.biClrUsed = 0
			self.biClrImportant = 0
			self.Image = []
			self.Mask = []

		def NumBytes(self):
			return self.biSizeImage + self.biSize

		def PrintImage(self, f):
			IntToFile(f, self.biSize, 4)
			IntToFile(f, self.biWidth, 4)
			IntToFile(f, self.biHeight*2, 4) # No idea why we multiply this by two, but we do.
			IntToFile(f, self.biPlanes)
			IntToFile(f, self.biBitCount)
			IntToFile(f, self.biCompression, 4)
			IntToFile(f, self.biSizeImage, 4)
			IntToFile(f, self.biXPelsPerMeter, 4)
			IntToFile(f, self.biYPelsPerMeter, 4)
			IntToFile(f, self.biClrUsed, 4)
			IntToFile(f, self.biClrImportant, 4)
			for i in range(self.biHeight*self.biWidth):
				if self.Image[i][3] < 128 and self.biBitCount < 32:
					IntToFile(f,0,1)
					IntToFile(f,0,1)
					IntToFile(f,0,1)
				else:
					IntToFile(f,self.Image[i][2],1)
					IntToFile(f,self.Image[i][1],1)
					IntToFile(f,self.Image[i][0],1)
					if self.biBitCount == 32:
						IntToFile(f,self.Image[i][3],1)
			
			for i in range(self.biHeight * self.biWidth / 8):
				IntToFile(f,self.Mask[i],1)

