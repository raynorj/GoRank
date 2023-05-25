#This script runs scripts against GNUGo to ascertain the challenger's rank (measuring by the handicap size, 1 stone = 1 rank)
#GNUGo serves as a reference point here, although its rank is difficult to determine....I've seen anywhere from 9k to 5k.

#AGA rules (as of May 2023) are followed, except handicap is not limited. Area scoring is used.

import os
import importlib
import subprocess

#This function provides an interface between the player script and GNUGo (which serves as the game engine)
#It facilitates the legwork, including deciding player colors, obtaining player moves, 
#obtaining final scores, and returning the winner (either "GNUGo" or the challenger agent's name string).
def game(challenger, challenger_rank):
	#setup board
	#os.system("boardsize")

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
			#get board_string
			#get move
			#apply move
				#check for illegality
				#pass if illegal

		#set turn_player = white
	else:
		#set turn_player = black


	#do game
	passcount = 0
	while true:
		#get board-string
		#pass board-string and get move from turn player
		#if pass, increment pass counter, else passcount = 0
		#if passcount == 2, end game, get final score, and return winner ("GNUGo" or challenger.name), ties are impossible if komi is set properly
		#attempt to play move
			#check if move was legal
			#if illegal, treat as a pass
		#alternate players

def get_move(challenger, turn_player):
	#get board string
	if turn_player == "GNUGo":
		#os.system("genmove " + GNUGo_color)
		#result = subprocess.check_output("genmove " + GNUGo_color), shell=True)
	else:
		new_move = challenger.move()
		#os.system("move " + challenger_color + " " + new_move)
		#result = subprocess.check_output("move " + challenger_color + " " + new_move, shell=True)

	#check stdout to see if move was illegal
	if not result.startswith("="):
		pass

	return new_move

#load list of python script names from file
with open("challengers.txt", "r") as fh:
	scripts = [line.strip() for line in fh.readlines()]

#import standardized class from each script
	#class - contains name, board string parser, and move recommender
agents = [importlib.import_module(script).GoAgent() for script in scripts]

#set up GNUGo
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
