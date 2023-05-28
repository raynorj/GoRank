#TODO
#write boardstate_recursive_check()
#does GNUGo check for ko?

#This script runs scripts against GNUGo to ascertain the challenger's rank (measuring by the handicap size, 1 stone = 1 rank)
#GNUGo serves as a reference point here, although its rank is difficult to determine....I've seen anywhere from 9k to 5k.

#AGA rules (as of May 2023) are followed, except handicap is not limited. Area scoring is used.

import os, re
import importlib
import subprocess

#This function provides an interface between the player script and GNUGo (which serves as the game engine)
#It facilitates the legwork, including deciding player colors, obtaining player moves, 
#obtaining final scores, and returning the winner (either "GNUGo" or the challenger agent's name string).

def game(challenger, challenger_rank):
	#setup board
	communicate_with_GNUGo("boardsize 19")

	rank_difference = challenger_rank - GNUGo_rank

	#decide handicaps
	if (rank_difference > 1): 	#challenger gets handicap stones
		black_player = challenger
		white_player = "GNUGo"
		handicap = abs(rank_difference)
		komi = 0.5 #added to white's final score

	elif (rank_difference < -1): 	#GNUGo gets handicap stones
		black_player = "GNUGo"
		white_player = challenger
		handicap = abs(rank_difference)
		komi = 0.5

	elif (rank_difference == 1):	#a one stone handicap would be a regular move, so reduce komi instead
		black_player = challenger
		white_player = "GNUGo"
		handicap = 0
		komi = 0.5

	elif (rank_difference == -1):
		black_player = "GNUGo"
		white_player = challenger
		handicap = 0
		komi = 0.5

	else: 				#are equal
		black_player = challenger
		white_player = "GNUGo"
		handicap = 0
		komi = 7.5 #according to Wikipedia, the AGA uses 7.5


	#perform preliminaries
	if handicap > 0:
		#get n=handicap moves from black player
		for i in range(handicap):
			play_move(challenger, black_player)

		turn_player = white_player
	else:
		turn_player = black_player


	#do game
	passcount = 0
	while true:
		if turn_player == white_player:
			last_move = play_move(challenger, turn_player)
			turn_player = black_player
		else:
			last_move = play_move(challenger, turn_player)
			turn_player = white_player

		if last_move == "pass":
			passcount += 1
		else:
			passcount = 0

		if passcount == 2:
			#get final score
			#return winner ("GNUGo" or challenger.name)
			#ties are impossible if komi is set properly

			final_score = score_board(komi):
			if final_score[0] == "W":
				return "GNUGo"
			else:
				return challenger.name

#note: internally, it is always assumed that the challenger is black and GNUGo is white
#practically, this should not make a difference and won't affect game(), provided that the scoring function is written correctly
def play_move(challenger, turn_player):
	if turn_player == "GNUGo":
		command = "genmove white"
		result = communicate_with_GNUGo(command)
	else:
		boardstate = get_and_parse_board()
		new_move = challenger.move(boardstate)
		command = "play black " + new_move
		result = communicate_with_GNUGo(command)

	#if move is illegal or was a pass, name new_move to "pass"
	if result[0] == "? illegal move" or result[0] == "=":
		new_move = "pass"

	#check for ko?

	return new_move

#we assume the board has been played through completely
def score_board(komi):
	boardstate = get_and_parse_board()

	for j in range(len(boardstate)):
		for i in range(len(boardstate[j])):
			if boardstate[j][i] == ".":
				#execute recursive fill on boardstate[j][i]
				fill_type = boardstate_recursive_check(boardstate, i, j)
				boardstate_recursive_fill(boardstate, i, j, fill_type)
	
	score = -komi
	for j in range(len(boardstate)):
		for i in range(len(boardstate[j])):
			if boardstate[j][i] == "B":
				score += 1
			elif boardstate[j][i] == "W":
				score -= 1

	if score > 0:
		return "B+" + score
	elif score < 0:
		return "W+" + abs(score)
	else:
		return "tie"

#returns "W", "B", or "M"
def boardstate_recursive_check(boardstate, x, y):
	pass

def boardstate_recursive_fill(boardstate, x, y, symbol):
	boardstate[y][x] = symbol
	x_size = len(boardstate[y])
	y_size = len(boardstate)

	if (x-1 >= 0) and boardstate[y][x-1] == ".":
		boardstate_recursive_fill(boardstate, x-1, y)

	if (y-1 >= 0) and boardstate[y-1][x] == ".":
		boardstate_recursive_fill(boardstate, x, y-1)

	if (x+1 < x_size) and boardstate[y][x+1] == ".":
		boardstate_recursive_fill(boardstate, x+1, y)

	if (y+1 < y_size) and boardstate[y+1][x] == ".":
		boardstate_recursive_fill(boardstate, x, y+1)

def get_and_parse_board():
	board_strings = communicate_with_GNUGo("showboard")
	board_arr = []

	#parse board_string
	for row in board_strings[2:-1]:
		board_arr.append([])
		row_data = board_regex.search(row)[0].strip()
		for char in row_data:
			if char != " ":
				if char == "+":
					board_arr[-1].append(".")
				else:
					board_arr[-1].append(char)					

	return board_arr

def communicate_with_GNUGo(command):
	
	proc.stdin.write("{}\n".format(command).encode('UTF-8'))
	proc.stdin.flush()

	output = []
	last_read = None

	while(last_read != b'\n'):
		last_read = proc.stdout.readline()
		output.append(last_read.decode('UTF-8').strip())

	return output[:-1]

#load list of python script names from file
with open("challengers.txt", "r") as fh:
	scripts = [line.strip() for line in fh.readlines()]

#import standardized class from each script
	#class - contains name, board string parser, and move recommender
agents = [importlib.import_module(script).GoAgent() for script in scripts]

#define useful variables
proc = subprocess.Popen("gnugo-3.8/gnugo --mode gtp", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
board_regex = re.compile("[XO\.\+\s]+")
GNUGo_rank = 9 #9 kyu
result_file = open("results.txt", "w")
gamecount = 100

#run games between GNUGo and challengers
for agent in agents:
	results = {}

	for challenger_rank in range(30, -6):
		wincount = 0
		
		for i in range(gamecount):
			#play games at different handicaps, find one with 50% winrate?
			if (game(agent, challenger_rank) != "GNUGo"):
				wincount += 1.0

			results[rank] = wincount / gamecount

	best_match_rank = -9999999999
	best_match_val = 99999999999 #double-check this
	for key,val in results.items():
		if (abs(val - 0.50) < best_match_val):
			best_match_val = val
			best_match_rank = key

	#print best_match_rank and agent name to file
	print(agent.name + ":" + best_match_rank, file = result_file)
