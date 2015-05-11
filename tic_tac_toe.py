#!/usr/bin/python

import sys

def build_board_strokes(board_strokes):
  # 3 horizontal
  for i in range(3): board_strokes.append((i*3,i*3+1,i*3+2))
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

def next_move(board, moves_so_far, winning_moves, move_no, who):
  ''' Given a moves_so_far and the player to play next(who)
      it adds to the moves and if a game is over at this point,
      it updates the winning moves '''
  if move_no >= 9:
    return
  indent=" "*move_no
  for i in range(9):
    if board[i] == None:
      moves_so_far.append(i)
      board[i] = who
      if is_board_won(board):
        winning_moves[who].append(moves_so_far[:])
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

print "building moves..",
sys.stdout.flush()
next_move(board, moves_so_far, winning_moves, 0, 0)
RootNode = WinProbTreeNode(0)
build_win_prob_tree(RootNode, winning_moves[0], 0)
build_win_prob_tree(RootNode, winning_moves[1], 1)
print "done"

def get_user_choice():
  which_user=int(raw_input("Which user do you want to play .. (first:0/second:1):"))
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
  for stroke in board_strokes:
    nones = 0
    first = None
    same = 0
    none_position = -1
    this_stroke = [board[i] for i in stroke ]
    for i in range(2,-1,-1):
      a = this_stroke.pop()
      if a == None:
        nones += 1
        none_position = i
      elif first == None:
        first = a
      elif first == a and first == who_to_win:
        same = 1
    if nones == 1 and same == 1:
      #ah!imminent
      return stroke[none_position]
  return -1

def get_computer_move(moves, board, who_to_win):
  curr_node = RootNode

  # Lets choose a winning move
  move = is_pattern_imminent(moves, board, who_to_win)
  if move != -1:
    return move

  # Lets break an imminent pattern
  move = is_pattern_imminent(moves, board, 1-who_to_win)
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
  for i in range(0,9):
    if curr_node.nextMoves[i] != None:
      if curr_node.nextMoves[i].counts[who_to_win] > my_max[1]:
        my_max = (i, curr_node.nextMoves[i].counts[who_to_win])
  return my_max[0]

while True:
  print "Starting game.."
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
      print "I played a move of %d"%move
      if move == -1:
        print "Its going to be a tie"
        break
      board[move] = computer
    moves.append(move)
    won = is_board_won(board)
    if won:
      if is_human_turn:
        print "You win!"
      else:
        print "I win!"
      draw_board(board)
      break
    is_human_turn = 1 - is_human_turn
  print "Tie.."

