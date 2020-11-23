#MenuTitle: 05. WetPaint
# -*- coding: utf-8 -*-
__doc__="""
05. WetPaint
"""

import GlyphsApp
from NaNGFGraphikshared import *
from NaNGFAngularizzle import *
from NaNGFNoise import *
from NaNFilter import NaNFilter

class Drip(NaNFilter):
	params = {
		"S": { "maxdrip": 150, "iterations": 1 },
		"M": { "maxdrip": 350, "iterations": 2 },
		"L": { "maxdrip": 400, "iterations": 2 }
	}

	def doDrip(self, thislayer, outlinedata, maxdrip):
		# find drippable segments within path and store indices
		indices = []
		pathcount = 0
		degvariance = 40

		for direction, nodes in outlinedata:
			nodelen = len(nodes)
			index = []
			n=0
			index_start = -999
			index_end = -999

			# collect all possible drippable segments within certain angle

			while n < nodelen-1:
				x1,y1 = nodes[n]
				x2,y2 = nodes[n+1]
				a = atan2(y1-y2, x1-x2)
				deg = degrees(a)

				if abs(deg)>(180-degvariance) and abs(deg)<(180+degvariance):
					if index_start == -999:
						index_start = n
					else:
						index_end = n
				else:
					if index_start != -999:
						index.append( [ index_start, index_end ] )
					index_start = -999
				n+=1

			indices.append([ pathcount, index ])
			pathcount+=1

		# run through each drippable segment and do something
		for p in range(0, len(outlinedata)):
			direction, structure = outlinedata[p]
			nodelen = len(structure)
			n=0
			segs = indices[p][1]

			for seg in segs:
				index_start, index_end = seg

				seedx = random.randrange(0,100000)
				seedy = random.randrange(0,100000)
				noisescale = 0.01

				steps = float(index_end - index_start)
				steppos = 0

				for n in range(index_start, index_end):

					angle = 180/steps * steppos
					t = math.sin(math.radians(angle))
					adjust = 1

					x,y = structure[n]

					if n < index_end:
						x2, y2 = structure[n+1]

						searchblack = DistanceToNextBlack(thislayer, [x, y], [x2, y2], outlinedata, searchlimit=200)
						#print searchblack

						if searchblack is not None and searchblack < 200:
								adjust = 0.2

					# insert distance to next black checker here

					noiz = pnoise1( (n+seedx)*noisescale, 4) 
					size = noiseMap( noiz, 0, maxdrip )
					if direction=="False": size*=0.2
					size = t * abs(size) * adjust

					structure[n][1] = y - size

					steppos+=1


		# draw updated outline
		for path in outlinedata:
			p = convertToFitpath(path[1], True)
			thislayer.paths.append(p)


	def processLayer(self, thislayer, params):
		for n in range(0, params["iterations"]):
			pathlist = doAngularizzle(thislayer.paths, 4) # small seg size = quicker
			outlinedata = setGlyphCoords(pathlist)
			self.doDrip(thislayer, outlinedata, params["maxdrip"])

Drip()
Font.enableUpdateInterface()

