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
        self.playersMoves = []
        self.firstMove = True
        self.secondMove = False

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
                    if(value == self.color):
                        self.playersMoves.append(move)
                    return True
                else:
                    raise Exception
            else:
                # out of range
                raise Exception
        except Exception:
            print("# Error: invalid position.")
            sys.exit(2)

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

    def minimax(self):
        moves = []
        if(self.firstMove):
            self.firstMove = False
            moves = self.getAvailableMoves(self.hexBoard)
        else:
            moves = self.getAdjacentMoves()
        bestMove = moves[0]
        bestScore = float('inf')
        alpha = float('-inf')
        beta = float('inf')
        depth = 3

        for move in moves:
            self.nextState(move, self.color)
            score = self.minValue(alpha, beta, depth)
            if score < bestScore:
                bestMove = move
                bestScore = score
            self.revertState(move)

        return bestMove

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

        moves = self.getAdjacentMoves()
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

        moves = self.getAdjacentMoves()
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
        visitedPositions = {}
        value = 0
        averagePosition = 1;

        for move in self.playersMoves:

            if move not in visitedPositions:
                lowerLimit = 0
                upperLimit = 0
                numberOfConnectedNodes = 0

                if(self.color == VALUE_RED):
                    lowerLimit = move[0]
                    upperLimit = move[0]
                    numberOfConnectedNodes = 1

                else:
                    lowerLimit = move[1]
                    upperLimit = move[1]
                    numberOfConnectedNodes = 1

                distance = [lowerLimit, upperLimit, numberOfConnectedNodes]
                numberOfConnectedNodes += self.numberOfConnections(move, distance, visitedPositions, averagePosition)
                lowerLimit = distance[0]
                upperLimit = distance[1]
                numberOfConnectedNodes = distance[2]

                penalty = 2
                if((averagePosition*1.0)/self.boardSize > ((1.0*self.boardSize)/2) + (1.0*self.boardSize)/3 or (averagePosition*1.0)/self.boardSize < ((1.0*self.boardSize)/2) - (1.0*self.boardSize)/3):
                    penalty = 1.0/3
                value += (3*numberOfConnectedNodes) + (numberOfConnectedNodes * upperLimit + 1 * (1/(lowerLimit+1)) * penalty)

        return value

    def numberOfConnections(self, move, distance, visitedPositions, averagePosition):
        i = move[0]
        j = move[1]
        connections = 0
        if(move in visitedPositions):
            return connections

        if(self.color == VALUE_RED):
            averagePosition += move[0]
        else:
            averagePosition += move[1]

        visitedPositions[move] = True

        #node = (i-1, j)
        if((i-1) >= 0 and self.hexBoard[i-1][j] == self.color):
            if(self.color == VALUE_BLUE and i-1 < distance[0]):
                distance[0] = i-1
            connections += 1 + self.numberOfConnections((i-1,j), distance, visitedPositions, averagePosition)
        #node = (i+1, j)
        if((i+1) < self.boardSize and self.hexBoard[i+1][j] == self.color):
            if(self.color == VALUE_BLUE and (i+1) > distance[1]):
                distance[1] = (i+1)
            connections += 1 + self.numberOfConnections((i+1,j), distance, visitedPositions, averagePosition)
        #node = (i, j-1)
        if((j-1) >= 0 and self.hexBoard[i][j-1] == self.color):
            if(self.color == VALUE_RED and j-1 < distance[0]):
                distance[0] = j-1
            connections += 1 + self.numberOfConnections((i,j-1), distance, visitedPositions, averagePosition)
        #node = (i, j+1)
        if((j+1) < self.boardSize and self.hexBoard[i][j+1] == self.color):
            if(self.color == VALUE_RED and (j+1) > distance[1]):
                distance[1] = (j+1)
            connections += 1 + self.numberOfConnections((i,j+1), distance, visitedPositions, averagePosition)
        #node = (i+1, j-1)
        if((j-1) >= 0 and (i+1) < self.boardSize and self.hexBoard[i+1][j-1] == self.color, averagePosition):
            if(self.color == VALUE_BLUE and (i+1) > distance[1]):
                distance[1] = (i+1)
            if(self.color == VALUE_RED and (j-1) < distance[0]):
                distance[0] = j-1
            connections += 1 + self.numberOfConnections((i+1,j-1), distance, visitedPositions, averagePosition)
        #node = (i-1, j+1)
        if((j+1) < self.boardSize and (i-1) >= 0 and self.hexBoard[i-1][j+1] == self.color):
            if(self.color == VALUE_BLUE and (i-1) < distance[0]):
                distance[0] = i-1
            if(self.color == VALUE_RED and (j+1) > distance[0]):
                distance[1] = (j+1)
            connections += 1 + self.numberOfConnections((i-1,j+1), distance, visitedPositions, averagePosition)

        return connections

    def getAvailableMoves(self, currentState):
        availableMoves = []

        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if currentState[i][j]==VALUE_EMPTY:
                    availableMoves.append((i,j))

        return availableMoves

    def getAdjacentMoves(self):
        adjacentMoves = []
        radius = 2
        playersMoves = self.getPlayersMoves(self.hexBoard)
        for playerMove in playersMoves:
            for i in range(self.boardSize):
                for j in range(self.boardSize):
                    if self.hexBoard[i][j] == VALUE_EMPTY and self.inIRangeOf(i, playerMove, radius) and self.inJRangeOf(j, playerMove, radius):
                        adjacentMoves.append((i,j))

        return adjacentMoves

    def inIRangeOf(self, i, playerMove, radius):
        lowerLimit = playerMove[0] - radius
        upperLimit = playerMove[0] + radius

        return(lowerLimit <= i and i <= upperLimit)
    def inJRangeOf(self, j, playerMove, radius):
        lowerLimit = playerMove[1] - radius
        upperLimit = playerMove[1] + radius

        return(lowerLimit <= j and j <= upperLimit)


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
            if(self.hexBoard[pi][pj] == self.color):
                del self.playersMoves[-1]
            self.hexBoard[pi][pj] = VALUE_EMPTY

    def gameOver(self, currentState):
        return (len(self.getAvailableMoves(currentState)) == 0)

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
            hexAgent.print_board()

        if hexAgent.color==VALUE_BLUE:
            # BLUE playes
            c_pos = hexAgent.minimax()
            c_inp = hexAgent.pos_to_inp(c_pos)
            # introduce random time pause
            # time.sleep(random.randint(0,4))
            print(c_inp)
        else:
            # wait for opponent
            c_inp = input()
            c_pos = hexAgent.inp_to_pos(c_inp)
        # BLUE MOVES
        hexAgent.update_board(hexAgent.hexBoard, c_pos, VALUE_BLUE)
        if arg_debug:
            hexAgent.print_board()


if __name__=="__main__":
    main(sys.argv[1:])
