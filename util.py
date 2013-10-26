def scalecolor(hexclr, perc):
	"""
	Scales a color from 0% - 100% brightness depending on "perc". Color
	must have the form '#aabbcc'
	"""
	if len(hexclr) != 7:
		return None
	hexclr = hexclr.strip("#")
	r, g, b = int(hexclr[:2], 16), int(hexclr[2:4], 16), int(hexclr[4:], 16)
	r = r*perc
	g = g*perc
	b = b*perc
	return "#%02x%02x%02x" % (r, g, b)

def dot(v1, v2):
	"""
	Returns the dot product of two vectors (lists)
	"""
	v1len = len(v1)
	if v1len != len(v2):
		return None
	return sum([v1[e]*v2[e] for e in range(0, v1len)])