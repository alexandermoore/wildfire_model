"""
Probabilistic Wildfire Simulator
Oct. 26, 2013

Developed by Alexander Moore
Github: alexandermoore
Email: alexandermoore at college.harvard.edu

This file runs the simulation specified in "classes.py"
"""

from classes import *
import math
import random

# Specify distributions for probabilities
def uniform():
	return random.random()

def constant():
	return 0.70

def emptyconst():
	return 0.30

# NE Wind, 30% strength.
wind = [math.cos(math.pi/4.0), math.sin(math.pi/4.0)]
windstr = 0.3
# Start fire in the middle
start = [0.5, 0.5]

# P(burn) given by uniform distribution, P(die) given by "constant"
simulation = Simulation(start[0], start[1], uniform, constant, emptyconst, wind, windstr)

graphic = GraphicWrapper(simulation)
graphic.run()