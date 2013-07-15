Solving Hitori

A Hitori puzzle is a grid of numbers, some of which need to be blackened in.

A simple puzzle:

4  3  2  2  3
3  4  1  5  2
1  3  4  5  5
4  3  5  4  1
5  1  2  2  2

Instructions:
  Blacken out numbers to meet the following criteria:
	1) A given row or column will have at most one of a given number
	2) No black sqaures are next to each other horizontally or vertically
	3) All white squares are connected via a horizontal/vertical path

The sample solution:

4  X  2  X  3
3  4  1  5  2
1  X  4  X  5
X  3  5  4  1
5  1  X  2  X


Basic rules:

1) When placing a white square, all matching numbers in row/column are black
2) When placing black, all neighboring squares are white
3) If a number is surrounded by the same number on both sides, it is white   1 2 1 == Unknown White Unknown
4) If a number appears next to itself, all other numbers on that line must be black



3.5) From these two, you can determine that 3 in a row must be black/white/black, this is helpful in solving by hand but isn't needed here.

These are the basic rules, 3 and 4 can be used to place initial positions while 1 & 2 are used each time a square is determined.

5) If a square does not have a match in row or column, it is white.
	This one is a bit harder to reason, but it comes down to assuming that there's one answer.   In order for that to be true, every square needs to be forced to an answer.  White can be forced by being next to black or avoiding enclosures.  Black is forced by a white in the same row or column.  Therefore, if there are no matching numbers, then the force must be to white.  Enclosure is non-local and harder to predetermine

	Another way to look at it, if a given black square has no white matches in row or column, would there be any reason it couldn't also be white?   If it's valid black then all neighbors are white, so it can't cause two blacks to be next to each other. Adding another white in the midst of existing ones also can't cause the whites to get disconnected.  Therefore such a black square could also be white, breaking the idea that only one answer exists.  By assuming the white, we'll effectively be choosing a specific answer.

Rule 5 can be evaluated each time a black square is filled in.

6) Adjacent pairs must be filled in opposing squares:    1  1  ==  W  B  or  B  W
														 2  2      B  W      W  B

Rule 6 is harder to check for programmatically, but it's used in several edge cases which could be hardcoded.  The square in the corner would be a good example.


The other rules are based on the requirement that white connect.  These are by necessity non-local.
Black squares that are connected will be considered to be in a group.  This group may also be listed as "grounded" if there's an edge in the group.
There's also a virtually connected group.  This is where the same number (in a row/column) in two places would connect the groups.  One of these must be black.  It also leads to a rule where any other values in that row must be black as well. 

7) Upon placement of a black:
	check each of the diagonal values
		If edge then mark EDGE
		If black, then note the group that square belongs to.   
	The following results are possible:  (Grounded edges will be listed with a G, ungrounded U, don't case X)
		Nothing: new group with this square
		EDGE: new group with this square
		EDGE, G1:  ERROR condition, will cause G1 to touch two edges
		EDGE, U1:  add to U, mark U grounded (G1)
		G1, G2: ERROR, resulting group would touch two edges
		X1, X1: ERROR, closing a loop
		X1, U2: change all squares in U2 to X1, add new one

		for cases of 3 or 4 matches (EDGE is impossible in this case), check for (G1,G2) or (X1, X1) condition for failure
		in all others, combine together and set to G if any source was G.

8) For pairs of white numbers in a row or column, find any groups that touch at corners.
	If the same group touches both, then combine those groups together
		Any squares other than those two will be set black

And for finding errors:
9) If you place two whites with the same number in row or column, ERROR


Implementation of the rules:

3/4/5 are all easy to process in the initial stages.  
Special cases of rule 6 could also be performed.
1/2/7 are used for every placement of a square
8 should be checked for periodically, perhaps after setting any black square?


Backtracking:
	At this point, it's down to guessing and backtracking on failure
	Failure conditions are rule 7 or 9 breaking down.
	Rule 6 sort of falls out from 1&2, but the existence of pairs could be useful to determine what square to choose.


So we need a board state with three values per square: unknown, white, black
A way to quickly find matching numbers in row or column
Groups are a list of squares per index and a BOOLEAN to determine if is grounded
When moving on a board, rules 1/2/7/9 should be used to fill in all the details as well as report ERROR conditions.

Fill the initial board with 3/4/5/6.
5/8 can gain additional information as the board is filled, so try them periodically.

Once this has gone as far as possible, the remaining values must be backtracked.
Breadth-first is probably appropriate, try each square as black and white and see if an error results, if so then you can fix that square.

If these fail to give real values, then resort to a real backtracking system.  Hopefully that won't need to go very deep...


What should the board look like:

Square = row, column, number, state (unknown, white, black)
Set of unknown squares, white squares, black squares?  In which case the state is redundant.
Set of groups with some kind of id, grounded? and set of squares

Set white: (rule 1/9)
	extract square from white squares, if not in there == ERROR
	extract [row, number] and [column, number] from white, if any match ERROR
	search unknown for match in [row, number] and [col, number] set each of those to black.  propogate ERRORS
	put square in white set

Set black: (rule 2/ 7)
	extract square from black squares, if not in there == ERROR
	if any neighbors found in black ERROR
	put square in black set
	find diagonal neighbors, if EDGE set EDGE, if black set the group
	If no groups, then create a new group
	If EDGE and grounded group, then ERROR
	If any group duplicated, then ERROR
	If two grounded groups, then ERROR
	Else combine all the groups, set combination to grounded if EDGE or any group is grounded
	for each neighbor, set white.  propogate ERRORS


The setBlack and setWhite methods will both return BOOL for error and a new state

Start the process by running the following:
Rule 3/4/5
	for each row and column
		find all matching sets
			if two indices with one in the middle, mark middle white (3)
			if two indices adjacent, mark all others black (4)
	squares marked single in both row and column are marked white (5)

Rule5:
	for each row, column
		find all matching sets
		if only one in a set, mark it
		if a square is marked for row and column, mark white


Rule 6 is sort of ad-hoc pattern match that may not be necessary since most of these will be caught quickly

Rule8:  (incorporate into set black?)
	Check unknowns matching in row/column
		Find diagonal neighbors
		If the same group is touching more than one space, then combine the groups
			Set any squares other than the matching pair to black, propogate ERRORS


Breadth-first:
	For each square in unknown
		blackErr, blackState = setBlack()
		whiteErr, whiteState = setWhite()
		if blackErr && ! whiteErr gameState = whiteState
		if !blackErr && whiteErr gameState = blackState

Use breadth-first, Rule5, Rule8 until no changes have been found.

At this point, we need to resort to backtracking
Recursive check:
	If nothing in unknown then we WIN!!!!!!!!!!

	Grab an unknown
	setBlack
	Run BF/5/8 on blackState until stable or ERROR
	setWhite
	Run BF/5/8 until stable or ERROR

	if both error, return error
	if only one errors recurse on it
	if neither error, then recurse both, return ERROR if both fail
		hopefully they both won't succeed....

Yep, thats a really nasty dual recursion....
Pretty easy to keep a log of why different decisions were made, so that would be useful.


HitoriBoard is a class, can be initialized from a file or created from an existing one.
	Data is four sets: unknown, white, black, groups
	Square data is row, column, value
	Group data is Grounded flag, set of squares (assumed to be black)





