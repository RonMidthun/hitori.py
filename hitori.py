#!/usr/bin/python


class HitoriBoard(object):
	'''Assumes fileData is a list of integers width height, then all the numbers in the puzzle in reading order'''
	@staticmethod
	def make_from_data(fileData):
		width = fileData[0]
		height = fileData[1]
		fileData = fileData[2:]
		unknown = dict()
		for row in range(height):
			for col in range(width):
				unknown[(row, col)] = fileData[row * width + col];

		return HitoriBoard(width, height, 0, unknown, dict(), dict(), dict())

	def __init__(self, width, height, groupIndex, unknown, black, white, groups):
		self.width = width
		self.height = height
		self.black = black.copy()
		self.white = white.copy()
		self.unknown = unknown.copy()
		self.groups = groups.copy()
		self.groupIndex = groupIndex

	def display(self):
		'''Show the current state with B for black and a * to indicate that a white value has been fixed'''
		out = []
		for row in range(self.height):
			for col in range(self.width):
				if (row, col) in self.black:
					out.append('BBB ')
				elif (row, col) in self.white:
					out.append('%2d  ' %  self.white[(row, col)])
				else:					
					out.append('%2d# ' %  self.unknown[(row, col)])
			out.append('\n')
		return ''.join(out)

	#will also have a number of methods to get squares matching row, column or number
	# generally, for a given row or column we want a dict where number tells the index in the row
	# so a row   1  2  1  3  6  2  would appear as  { 1:[0, 2], 2:[1, 5], 3:[3], 6:[4] }
	# this would be simple enough to calculate and generally would apply to unknowns

	# need a way to get all corner neighbors, including marking edges

	# all routines to set values will return (new_board, error_bool, changes_made)
	#   set_white (rule 1)
	#   set_black (rule 2/ 7)
	#   initial_solve (rule 3/4)
	#   set_singletons_white  (rule 5)a
	#   merge_groups (rule 8)
	#   breadth_first
	#	backtracking is probably outside this class, as well as the general framework calling these routines





