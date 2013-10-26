"""
Probabilistic Wildfire Simulator
Oct. 26, 2013

Developed by Alexander Moore
Github: alexandermoore
Email: alexandermoore at college.harvard.edu

This file handles the simulation's inner workings.
The simulation is based on the model described by Almeida and Macau here: 
http://iopscience.iop.org/1742-6596/285/1/012038
Additional complicatons such as wind and probabilities that vary per tree were added by me.
"""


import Tkinter
import random
import math
import util

# Define tree states
STATES = {
	'alive': {'color': "#00ff00"},
	'burning': {'color': "#ff0000"},
	'dead': {'color': "#aaaaaa"},
}

# Define grid size, size of window and size of each tree rectangle
LANDSIZE = 60
WINDOWSIZE = 600
RECTSZ = WINDOWSIZE/LANDSIZE

SQRT_2_2 = math.sqrt(2.0) / 2.0


class GraphicWrapper:
	"""
	Run the specified simulation and updates the graphics in the process
	"""

	def __init__(self, sim):
		"""
		Initializes the graphical wrapper of the simulation. Takes in a simulation object
		for use in the updating process.
		"""
		# Update every 100ms
		self.timestep = 100

		self.sim = sim

		# Setup graphics
		self.tk = Tkinter.Tk()
		self.tk.after(0, self.draw)
		self.canvas = Tkinter.Canvas(self.tk, width=WINDOWSIZE, height=WINDOWSIZE)
		self.canvas.pack()

		# Create rectangles to represent trees
		self.rects = [[
						self.canvas.create_rectangle(x*RECTSZ, y*RECTSZ, 
							x*RECTSZ + RECTSZ, y*RECTSZ + RECTSZ,
							fill="pink", outline="pink") 
						for x in range(LANDSIZE)] for y in range(LANDSIZE)
					]

	def draw(self):
		"""
		Draws trees by updating the colors of the rectangles to those dictated by the
		simulation. I understand an abstraction barrier is sortof broken here because the color is specified
		in the simulation and in the special "#aabbcc" format which is particular to Tkinter. This color
		could be generalizable to other graphics libraries, however, as the "#aabbcc" format is common.
		"""
		# Draw trees by updating colors of rectangles
		for row in range(LANDSIZE):
			for col in range(LANDSIZE):
				self.canvas.itemconfig(self.rects[row][col], 
					fill=self.sim.board[row][col].color,
					outline='black',
					width=1)

	def update(self):
		"""
		Updates a given timestep of the simulation and makes sure to draw the trees when it does so.
		"""
		# Draw trees
		self.draw()
		# Update simulation
		self.sim.update()
		# Schedule next update
		self.tk.after(self.timestep, self.update)

	def run(self):
		"""
		Begins the simulation
		"""
		self.update()
		Tkinter.mainloop()
		

class Simulation:
	"""
	Contains a function for handling the execution of the simulation
	"""

	def __init__(self, rowfireperc, colfireperc, burnfunc, diefunc, windvec, windstr):
		"""
		Sets up the necessary parameters for running a simulation of a fire in a LANDSIZE * LANDSIZE forest.
		The first fire starts rowfireperc percent of the way down the grid and colfireperc percent of the
		way across the grid.
		burnfunc and diefunc are functions which return a random probability of being burned or
		dying. The purpose of this is to be able to use probability distributions
		when assigning probabilities to individual trees.
		Windvec should be a normalized direction vector of the form [Xdir, Ydir].
		Windstr specifies the strength of the wind (from 0.0 to 1.0)
		"""
		# Initialize board to bunch of trees. 
		self.board = [[Tree(burnfunc(), diefunc()) for _ in range(LANDSIZE)] for _ in range(LANDSIZE)]

		# Make the specified tree burn
		self.board[int(LANDSIZE * rowfireperc)][int(LANDSIZE * colfireperc)].state = STATES['burning']

		# Tuple vector with wind direction at 45 degrees NE (Positive Y is up for the wind. Calculation
		# of the wind's effect in update() takes this into account)
		# Wind must be converted from [Xdir, Ydir] to [Ydir, Xdir]
		self.wind = [windvec[x] for x in range(1, -1, -1)]
		# Y component must be negative b/c in simulation positive Ydir is actually
		# down
		self.wind[0] = -self.wind[0]
		# Scale the wind down to 'windstr' strength
		self.wind = [x*windstr for x in self.wind]

	def update(self):
		"""
		Progresses the simulation by one timestep
		"""
		# Iterate over all trees and update
		for row in range(LANDSIZE):
			for col in range(LANDSIZE):
				# Update everything adjacent to current tree
				for r in range(row-1, row+2):
					for c in range(col-1, col+2):
						if r < LANDSIZE and r >= 0 and c < LANDSIZE and c >= 0 and (r!= row or c!= col):
							# Get normalized direction vector [Y, X] (normalization occurs if row and column are both different)
							dirvec = [(r - row) if (c - col) == 0 else (r - row) * SQRT_2_2, 
									  (c - col) if (r - row) == 0 else (c - col) * SQRT_2_2]
							# Attempt to affect neighbors. Take direction of wind into account. Wind more likely to
							# burn something in front than it is to burn something behind.
							self.board[r][c].attempt_effect(self.board[row][col], util.dot(self.wind, dirvec))
				# Update current tree
				self.board[row][col].update()
		

class Tree:
	"""
	A representation of a Tree with a given state and various parameters.
	"""

	def __init__(self, pburn, pdie):
		"""
		Specifies initial state of trees. Takes in probability of igniting given an
		adjacent tree is burning and the probability of dying given it has been ignited.
		"""
		# Trees alive at start
		self.state = STATES['alive']
		# Probabilities of starting to burn (given an adjacent tree is burning) and dying while burning at each timestep
		self.pburn = pburn
		self.pdie = pdie
		# Set to true if this tree started burning in this timestep
		self.just_ignited = False
		self.color = None
		self.__scalecolor()

	def attempt_effect(self, source, windperc):
		"""
		Attempts to make the source Tree effect this Tree.
		Currently the only effect is that this tree can be ignited if
		the source is burning
		"""
		if self.state == STATES['alive'] and source.state == STATES['burning'] and not source.just_ignited:
			# Burn probability affected by wind and Tree's prior probability of burning.
			# Can be pushed above 1 or below 0, which is the same thing as having probability 1 or 0.
			if random.random() <= self.pburn + windperc:
				self.state = STATES['burning']
				self.__scalecolor()
				self.just_ignited = True

	def update(self):
		"""
		Allow this tree to die probabilistically if it's burning
		"""
		if self.state == STATES['burning'] and not self.just_ignited:
			if random.random() <= self.pdie:
				self.state = STATES['dead']
				self.__scalecolor()
		self.just_ignited = False

	def __scalecolor(self):
		"""
		Brighten/darken color based on burn probability
		"""
		self.color = util.scalecolor(self.state['color'], 0.25 + self.pburn*0.75)
