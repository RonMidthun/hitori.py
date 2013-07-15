#!/usr/bin/python
from collections import defaultdict

data_log = list()

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

	def __init__(self, width, height, group_index, unknown, black, white, groups):
		self.width = width
		self.height = height
		self.black = black.copy()
		self.white = white.copy()
		self.unknown = unknown.copy()
		self.groups = groups.copy()
		self.group_index = group_index

	def __repr__(self):
		out = []
		out.append('width %d height %d' % (self.width, self.height))
		out.append('group_index %d' % self.group_index)
		out.append('unknown %s' % self.unknown)
		out.append('black %s' % self.black)
		out.append('white %s' % self.white)
		out.append('groups %s' % self.groups)
		return '\n'.join(out)


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
	#extract from a given dictionary
	def row_data(self, row, square_dict):
		data = defaultdict(list)
		for col in range(self.width):
			if (row, col) in square_dict:
				data[square_dict[(row, col)]].append(col)
		return data

	def col_data(self, col, square_dict):
		data = defaultdict(list)
		for row in range(self.width):
			if (row, col) in square_dict:
				data[square_dict[(row, col)]].append(row)
		return data



	# all routines to set values will return (new_board, error?, changes_made?)
	#   set_white (rule 1)
	#   set_black (rule 2/ 7)
	#   initial_solve (rule 3/4)
	#   set_singletons_white  (rule 5)a
	#   merge_groups (rule 8)
	#   breadth_first
	#	backtracking is probably outside this class, as well as the general framework calling these routines

	#these are internal to set_white/set_black and should not be called from anywhere else
	def change_to_black(self, row, col):
		if (row, col) in self.white:
			data_log.append('ERROR: change_to_black (%d,%d) is white' % (row, col))
			return None, True, False
		if (row, col) in self.black:
			data_log.append('ERROR: change_to_black (%d,%d) is black' % (row, col))
			return None, True, False
		if (row, col) not in self.unknown:
			data_log.append('ERROR: change_to_black (%d,%d) is not unknown' % (row, col))
			return None, True, False
		new_unknown = self.unknown.copy()
		new_black = self.black.copy()

		new_black[(row, col)] = self.unknown[(row, col)]
		del new_unknown[(row, col)]

		data_log.append('SET: change_to_black (%d,%d)' % (row, col))
		return HitoriBoard(self.width, self.height, self.group_index, new_unknown, new_black, self.white, self.groups), False, True

	def change_to_white(self, row, col):
		if (row, col) in self.white:
			data_log.append('ERROR: change_to_white (%d,%d) is white' % (row, col))
			return None, True, False
		if (row, col) in self.black:
			data_log.append('ERROR: change_to_white (%d,%d) is black' % (row, col))
			return None, True, False
		if (row, col) not in self.unknown:
			data_log.append('ERROR: change_to_white (%d,%d) is not unknown' % (row, col))
			return None, True, False
		new_unknown = self.unknown.copy()
		new_white = self.white.copy()

		new_white[(row, col)] = self.unknown[(row, col)]
		del new_unknown[(row, col)]

		data_log.append('SET: change_to_white (%d,%d)' % (row, col))
		return HitoriBoard(self.width, self.height, self.group_index, new_unknown, self.black, new_white, self.groups), False, True


	def set_white(self, row, col):
		if (row, col) not in self.unknown:
			data_log.append('ERROR: set_white (%d,%d) not in unknown' % (row, col))			
			return None, True, False
		number = self.unknown[(row, col)]

		#check for white matches in row
		row_match = self.row_data(row, self.white)
		if number in row_match:
			data_log.append('ERROR: set_white (%d,%d) matching white %s' % (row, col, row_match[number]))
			return None, True, False

		#check for white matches in col
		col_match = self.col_data(col, self.white)
		if number in col_match:
			data_log.append('ERROR: set_white (%d,%d) matching white %s' % (row, col, col_match[number]))
			return None, True, False

		#set the square itself
		board, error, changed = self.change_to_white(row, col)
		if(error):
			return None, True, False

		# set all matching numbers to black
		unknown_col = board.col_data(col, board.unknown)
		other_rows = unknown_col.get(number)
		if other_rows:
			for other_row in other_rows:
				if (other_row, col) not in board.black:	 #it might have been set by earlier loop
					board, error, changed = board.set_black(other_row, col)
					if error:
						return None, True, False

		# unknown_row = board.row_data(row, board.unknown)
		# other_cols = unknown_row.get(number)
		# if other_cols:
		# 	for other_col in other_cols:
		# 		if (row, other_col) not in board.black:	 #it might have been set by earlier loop
		# 			board, error, changed = board.set_black(row, other_col)
		# 			if error:
		# 				return None, True, False

		return board, False, True


	def set_black(self, row, col):
		#check for neighboring black cells
		neighbors = set()
		if row > 0:
			neighbors.add((row - 1, col))
		if col > 0:
			neighbors.add((row, col - 1))
		if row < self.height -1 :
			neighbors.add((row + 1, col))
		if col < self.width - 1:
			neighbors.add((row, col + 1))

		for neighbor in neighbors:
			if neighbor in self.black:
				data_log.append('set_black (%d,%d) neighbor (%d,%d) is black' % (row, col, neighbor[0], neighbor[1]))
				return None, True, False


		#set square to black
		board, error, changed = self.change_to_black(row, col)
		if error:
			return None, True, False

		#set neighbors to white
		for neighbor in neighbors:
			if neighbor not in board.white:	#it could have been set from another cascade
				board, error, changed = board.set_white(*neighbor)
				if error:
					return None, True, False

		#update groups
		return board, False, True



