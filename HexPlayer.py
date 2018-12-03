#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: Erick Suarez
@contact: esuarez@cs.ucsb.edu
@file: HexPlayer.py
@version: 0.1
@description:
'''

from __future__ import print_function

import sys
import time
import getopt
import random
import copy

# ======================================================================================
# Constants
# ======================================================================================
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTER2INT = {ALPHABET[i]: i for i in range(26)}
VALUE_EMPTY = 0
VALUE_RED = 1  # from letter side to letter side
VALUE_BLUE = -1  # from integer side to integer side

class HexAgent:
    # ======================================================================================
    # Constructor
    # ======================================================================================
    def __init__(self, boardSize, color):
        self.hexBoard = [[VALUE_EMPTY for j in range(boardSize)] for i in range(boardSize)]
        self.boardSize = boardSize
        self.color = color

    # ======================================================================================
    # Public Methods
    # ======================================================================================
    def inp_to_pos(self, inp):
        try:
            pi = inp[0]
            if not (pi in ALPHABET):
                return None
            pi = LETTER2INT[pi]
            pj = int(inp[1:])
            move = (pi,pj)
            if self.check_pos(move):
                return move
            else:
                # out of range
                raise Exception
        except Exception:
            # fail to translate, invalid input
            print("# Error: invalid position.")
            sys.exit(2)

    def pos_to_inp(self, move):
        try:
            pi = move[0]
            pj = move[1]
            if self.check_pos(move):
                inp = "{}{}".format(ALPHABET[pi],pj)
                return inp
            else:
                # out of range
                raise Exception
        except Exception:
            # fail to translate, invalid input
            print("# Error: invalid position.")
            sys.exit(2)

    def update_board(self, board, move, value):
        # update board status
        # return True: successful
        # return False: failed
        try:
            pi = move[0]
            pj = move[1]
            if self.check_pos(move):
                if board[pi][pj]==VALUE_EMPTY:
                    board[pi][pj] = value
                    return True
                else:
                    raise Exception
            else:
                # out of range
                raise Exception
        except Exception:
            print("# Error: invalid position.")
            sys.exit(2)

    def strategy_random(self, board):
        # search for empty position
        d_available_pos = []
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if board[i][j]==VALUE_EMPTY:
                    d_available_pos.append((i,j))
        if len(d_available_pos)==0:
            # END OF GAME
            # print("# Game Over.")
            sys.exit(0)
        # randomized
        random.shuffle(d_available_pos)
        return d_available_pos[0]

    def minimax(self):
        moves = self.getAvailableMoves(self.hexBoard)
        bestMove = moves[0]
        bestScore = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        depth = 2

        for move in moves:
            print(move)
            self.nextState(move, self.color)
            score = self.minValue(alpha, beta, depth)
            if score > bestScore:
                bestMove = move
                bestScore = score
            self.revertState(move)

        return bestMove

    def print_board(self):
        print("     ",end="")
        for j in range(self.boardSize):
            print(" {:<2} ".format(j),end="")
        print()
        print("    +",end="")
        for j in range(self.boardSize):
            print("---+",end="")
        print()
        for i in range(self.boardSize):
            print(" {:3}|".format(ALPHABET[i]),end="")
            for j in range(self.boardSize):
                if self.hexBoard[i][j]==VALUE_RED:
                    print(" R |",end="")
                elif self.hexBoard[i][j]==VALUE_BLUE:
                    print(" B |",end="")
                else:
                    print("   |",end="")
            print()
            print("    +",end="")
            for j in range(self.boardSize):
                print("---+",end="")
            print()

    # ======================================================================================
    # Private Methods
    # ======================================================================================
    def check_pos(self, move):
        # check validity of pos
        try:
            pi = move[0]
            pj = move[1]
            if pi<0 or pi>=self.boardSize or pj<0 or pj>=self.boardSize:
                return False
            else:
                return True
        except Exception:
            # could be type error or something
            return False

    def maxValue(self, alpha, beta, depth):
        if(depth == 0 or self.gameOver(self.hexBoard)):
            return self.heuristicValue(self.hexBoard)

        moves = self.getAvailableMoves(self.hexBoard)
        bestScore = float('-inf')

        for move in moves:
            self.nextState(move, self.color)
            score = self.minValue(alpha, beta, depth-1)
            if score > bestScore:
                bestScore = score
            if score >= beta:
                self.revertState(move)
                return bestScore
            if score > alpha:
                alpha = score
            self.revertState(move)

        return bestScore

    def minValue(self, alpha, beta, depth):
        if(depth == 0 or self.gameOver(self.hexBoard)):
            return self.heuristicValue(self.hexBoard)

        moves = self.getAvailableMoves(self.hexBoard)
        bestScore = float('inf')

        for move in moves:
            if(self.color == VALUE_RED):
                self.nextState(move, VALUE_BLUE)
            else:
                self.nextState(move, VALUE_RED)
            score = self.maxValue(alpha, beta, depth-1)

            if score < bestScore:
                bestScore = score
            if score <= alpha:
                self.revertState(move)
                return bestScore
            if score < beta:
                beta = score
            self.revertState(move)

        return bestScore

    def heuristicValue(self, currentState):
        stateCpy = copy.deepcopy(currentState)
        moves = self.getPlayersMoves(currentState)
        max = 0

        for move in moves:
            lowerLimit = self.boardSize
            upperLimit = self.boardSize
            numberOfConnectedNodes = 0

            if(self.color == VALUE_RED):
                lowerLimit = move[0]
                upperLimit = self.boardSize-1-move[0]
                numberOfConnectedNodes = 1
            else:
                lowerLimit = move[1]
                upperLimit = self.boardSize-1-move[1]
                numberOfConnectedNodes = 1
                
            distance = [lowerLimit, upperLimit, numberOfConnectedNodes]
            numberOfConnectedNodes += self.numberOfConnections(stateCpy, move, distance)
            lowerLimit = distance[0]
            upperLimit = distance[1]
            numberOfConnectedNodes = distance[2]

            value = (self.boardSize-lowerLimit)*(self.boardSize-upperLimit)+numberOfConnectedNodes
            if(value > max):
                max = value

        #return random.randint(1,101)
        return max

    def numberOfConnections(self, currentState, move, distance):
        i = move[0]
        j = move[1]

        connections = 0

        #node = (i-1, j)
        if((i-1) >= 0 and currentState[i-1][j] == self.color):
            currentState[i-1][j] = 42
            if(self.color == VALUE_RED and i-1 < distance[0]):
                distance[0] = i-1
            connections += 1 + self.numberOfConnections(currentState, [i-1,j], distance)
        #node = (i+1, j)
        if((i+1) < self.boardSize and currentState[i+1][j] == self.color):
            currentState[i+1][j] = 42
            if(self.color == VALUE_RED and self.boardSize-1-(i+1) < distance[1]):
                distance[1] = self.boardSize-1-(i+1)
            connections += 1 + self.numberOfConnections(currentState, [i+1,j], distance)
        #node = (i, j-1)
        if((j-1) >= 0 and currentState[i][j-1] == self.color):
            currentState[i][j-1] = 42
            if(self.color == VALUE_BLUE and j-1 < distance[0]):
                distance[0] = j-1
            connections += 1 + self.numberOfConnections(currentState, [i,j-1], distance)
        #node = (i, j+1)
        if((j+1) < self.boardSize and currentState[i][j+1] == self.color):
            currentState[i][j+1] = 42
            if(self.color == VALUE_BLUE and self.boardSize-1-(j+1) < distance[1]):
                distance[1] = self.boardSize-1-(j+1)
            connections += 1 + self.numberOfConnections(currentState, [i,j+1], distance)
        #node = (i+1, j-1)
        if((j-1) >= 0 and (i+1) < self.boardSize and currentState[i+1][j-1] == self.color):
            currentState[i+1][j-1] = 42
            if(self.color == VALUE_RED and self.boardSize-1-(i+1) < distance[1]):
                distance[1] = self.boardSize-1-(i+1)
            if(self.color == VALUE_BLUE and (j-1) < distance[0]):
                distance[0] = j-1
            connections += 1 + self.numberOfConnections(currentState, [i+1,j-1], distance)
        #node = (i-1, j+1)
        if((j+1) < self.boardSize and (i-1) >= 0 and currentState[i-1][j+1] == self.color):
            currentState[i-1][j+1] = 42
            if(self.color == VALUE_RED and (i-1) < distance[0]):
                distance[0] = i-1
            if(self.color == VALUE_BLUE and (j-1) < distance[0]):
                distance[1] = self.boardSize - 1 - (j+1)
            connections += 1 + self.numberOfConnections(currentState, [i-1,j+1], distance)

        return connections

    def getAvailableMoves(self, currentState):
        availableMoves = []

        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if currentState[i][j]==VALUE_EMPTY:
                    availableMoves.append((i,j))

        return availableMoves

    def getPlayersMoves(self, currentState):
        playerMoves = []

        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if currentState[i][j]==self.color:
                    playerMoves.append((i,j))

        return playerMoves

    def nextState(self, move, value):
        self.update_board(self.hexBoard, move, value)

    def revertState(self, move):
        pi = move[0]
        pj = move[1]

        if self.check_pos(move):
            self.hexBoard[pi][pj] = VALUE_EMPTY

    def gameOver(self, currentState):
        return (len(self.getAvailableMoves(currentState)) == 0) or self.someoneHasWon(currentState)

    def someoneHasWon(self, currentState):
        return False #TODO: STUB

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "dp:s:", ["debug","player=","size="])
    except getopt.GetoptError:
        print('Error: RandomHex.py [-d] [-p <ai_color>] [-s <board_size>]')
        print('.  or: RandomHex.py [--debug] [--player=<ai_color>] [--size=<board_size>]')
        sys.exit(2)

    # default arguments
    arg_player = "RED"
    arg_size = 11
    arg_debug = False
    for opt, arg in opts:
        if opt in ("-d","--debug"):
            arg_debug = True
        elif opt in ("-p","--player"):
            arg_player = arg.upper()
            if not arg_player in ["RED","BLUE"]:
                print('Error: Invalid player, should be either "RED" or "BLUE".')
                sys.exit(2)
        elif opt in ("-s","--size"):
            try:
                arg_size = int(arg)
                if arg_size<=0 or arg_size>26:
                    raise Exception()
            except Exception:
                print('Error: Invalid size, should be integer in [1,26].')
                sys.exit(2)

    # initialize the game
    color = 0
    if(arg_player == "RED"):
        color = VALUE_RED
    else:
        color = VALUE_BLUE
    hexAgent = HexAgent(arg_size, color)

    while(True):
        if hexAgent.color==VALUE_RED:
            # RED playes first
            c_pos = hexAgent.minimax()
            c_inp = hexAgent.pos_to_inp(c_pos)
            # introduce random time pause
            # time.sleep(random.randint(0,4))
            print(c_inp)
        else:
            # wait for opponent
            c_inp = input()
            c_pos = hexAgent.inp_to_pos(c_inp)
        # RED MOVES
        hexAgent.update_board(hexAgent.hexBoard, c_pos, VALUE_RED)
        if arg_debug:
            hexAgent.print_board(hexAgent.hexBoard)

        if hexAgent.color==VALUE_BLUE:
            # BLUE playes
            c_pos = hexAgent.minimax()
            c_inp = hexAgent.pos_to_inp(c_pos)
            # introduce random time pause
            # time.sleep(random.randint(0,4))
            print(c_inp)
        else:
            # wait for opponent
            c_inp = raw_input()
            c_pos = hexAgent.inp_to_pos(c_inp)
        # BLUE MOVES
        hexAgent.update_board(hexAgent.hexBoard, c_pos, VALUE_BLUE)
        if arg_debug:
            hexAgent.print_board(hexAgent.hexBoard)


if __name__=="__main__":
    main(sys.argv[1:])
