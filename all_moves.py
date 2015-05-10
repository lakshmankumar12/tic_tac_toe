#!/usr/bin/python

import os
import sys

#debugAllMovesfd=open("debug_all_moves.txt","w")
debugWinMovesfd=open("debug_win_moves.txt","w")
debugWinProbTreefd=open("debug_win_prob_tree.txt","w")

def build_board_strokes(board_strokes):
  # 3 horizontal
  for i in range(3): board_strokes.append((i,i+1,i+2))
  # 3 horizontal
  for i in range(3): board_strokes.append((i,i+3,i+6))
  # top-left diagnol
  board_strokes.append((0,4,8))
  # top-right diagnol
  board_strokes.append((2,4,6))

def is_board_won(board):
  #check the 3 rows
  for stroke in board_strokes:
    if board[stroke[0]] != None and \
        board[stroke[0]] == board[stroke[1]] and \
        board[stroke[1]] == board[stroke[2]]:
      return 1
  return 0

discard ='''
  for i in range(3):
    this_row = i*3;
    if board[this_row+0] != None and \
        board[this_row+0] == board[this_row+1] and \
        board[this_row+1] == board[this_row+2]:
      return 1
  # check the 3 columns
  for i in range(3):
    this_column = i
    if board[this_column+0] != None and \
        board[this_column+0] == board[this_column+3] and \
        board[this_column+3] == board[this_column+6]:
      return 1
  # check the top-left start diagnol
  if board[0] != None and \
      board[0] == board[4] and \
      board[4] == board[8]:
    return 1
  # check the top-right start diagnol
  if board[2] != None and \
      board[2] == board[4] and \
      board[4] == board[6]:
    return 1
  return 0
'''

def next_move(board, moves_so_far, winning_moves, move_no, who):
  if move_no >= 9:
    return
  indent=" "*move_no
  #debugAllMovesfd.write('%sNext Move: %d, Board: %s, who: %d\n'%(indent, move_no, board, who))
  for i in range(9):
    if board[i] == None:
      moves_so_far.append(i)
      board[i] = who
      if is_board_won(board):
        winning_moves[who].append(moves_so_far[:])
        debugWinMovesfd.write('Who: %d, Moves :%s, Board: %s\n'%(who, moves_so_far, board))
      else:
        next_move(board, moves_so_far, winning_moves, move_no+1, 1-who)
      moves_so_far.pop()
      board[i] = None
  return

class WinProbTreeNode:
  TotCreated = 0
  def __init__(self,who):
    self.counts = [0,0]
    self.counts[who] += 1
    self.nextMoves = [None]*9
    WinProbTreeNode.TotCreated += 1


def build_win_prob_tree(RootNode, winning_moves, who):

  # This can optimize later as we are re-walking the tree
  # from nodes for every move!
  for one_win in winning_moves:
    curr_node = RootNode
    for move in one_win:
      if curr_node.nextMoves[move] != None:
        curr_node.nextMoves[move].counts[who] += 1
      else:
        curr_node.nextMoves[move] = WinProbTreeNode(who)
      curr_node = curr_node.nextMoves[move]

def print_win_prob_tree(fd, RootNode):
  for i in range(9):
    so_far = []
    if RootNode.nextMoves[i] != None:
      print_one_node(fd, so_far, i, RootNode.nextMoves[i])

def print_one_node(fd, so_far, this_move, my_node):
  so_far.append(this_move)
  fd.write("%s, 0's: %d, 1's: %d\n"%(so_far, my_node.counts[0], my_node.counts[1]))
  for i in range(9):
    if my_node.nextMoves[i] != None:
      print_one_node(fd, so_far, i, my_node.nextMoves[i])
  so_far.pop()

board=[None]*9
board_strokes = []
build_board_strokes(board_strokes)
moves_so_far=[]
winning_moves=[[],[]]

next_move(board, moves_so_far, winning_moves, 0, 0)
print "Total winning moves for 0:%d"%len(winning_moves[0])
print "Total winning moves for 1:%d"%len(winning_moves[1])
RootNode = WinProbTreeNode(0)
build_win_prob_tree(RootNode, winning_moves[0], 0)
build_win_prob_tree(RootNode, winning_moves[1], 1)

print "Total nodes created:%d"%WinProbTreeNode.TotCreated
print_win_prob_tree(debugWinProbTreefd, RootNode)

def get_user_choice():
  which_user=int(raw_input("Which user do you want to play(0/1):"))
  if not which_user in [0,1]:
    print "Sorry.. choose only 0 or 1. You chose %d"%which_user
    sys.exit(1)
  return which_user

def get_move_choice(board):
  possible_moves = [ i for i in range(9) if board[i] == None ]
  which_move=int(raw_input("Choose a move %s:"%possible_moves))
  if not which_move in possible_moves:
    print "Sorry.. You didn't amongs possible moves. You chose %d"%which_move
    sys.exit(1)
  return which_move

def draw_board(board):
  values = [ "o", "x" ]
  print_list = []
  for i in board:
    if i == None: print_list.append("-")
    else: print_list.append(values[i])
  print "Board:"
  print " %s | %s | %s\n---+---+---\n %s | %s | %s\n---+---+---\n %s | %s | %s"% \
      tuple(print_list)

def is_pattern_imminent(moves, board, who_to_win):
  return -1

def get_computer_move(moves, board, who_to_win):
  curr_node = RootNode
  print "Moves so far:%s"%moves

  # Lets break an imminent pattern
  move = is_pattern_imminent(moves, board, who_to_win)
  if move != -1:
    return move

  # come to the decision node
  for i in moves:
    if curr_node.nextMoves[i] == None:
      return -1
    curr_node = curr_node.nextMoves[i]
  if curr_node == None:
    return -1
  my_max = (-1,-1)
  opp_max = (-1,-1)
  for i in range(0,9):
    if curr_node.nextMoves[i] != None:
      if curr_node.nextMoves[i].counts[who_to_win] > my_max[1]:
        my_max = (i, curr_node.nextMoves[i].counts[who_to_win])
      if curr_node.nextMoves[i].counts[1-who_to_win] > opp_max[1]:
        opp_max = (i, curr_node.nextMoves[i].counts[1-who_to_win])
  return my_max[0]

board = [None]*9
moves=[]
human = get_user_choice()
computer = 1 - human
is_human_turn = 1 - human
for i in range(9):
  draw_board(board)
  if is_human_turn:
    move = get_move_choice(board)
    board[move] = human
  else:
    move = get_computer_move(moves, board, computer)
    print "Got computer move of %d"%move
    if move == -1:
      print "Its going to be a tie"
      sys.exit(1)
    board[move] = computer
  moves.append(move)
  won = is_board_won(board)
  if won:
    if is_human_turn:
      print "You win!"
    else:
      print "I win!"
    draw_board(board)
    sys.exit(0)
  is_human_turn = 1 - is_human_turn

print "Tie.."

