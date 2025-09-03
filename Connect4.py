import pygame
import sys
import math
import numpy as np
import random
import time  # Import time module to measure AI move time

# Initialize Pygame
pygame.init()

# Define colors for the game
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Define constants for the game (e.g., board size and Connect 4 rule)
ROW_COUNT = 6
COLUMN_COUNT = 7
CONNECT = 4  # Number of pieces needed to connect (can be changed for Connect 5/6)

# Screen setup constants
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

# Initialize the Pygame display window
screen = pygame.display.set_mode(size)
myfont = pygame.font.SysFont("monospace", 75)

# AI timing variables to measure how long the AI takes for each move
total_time = 0
move_count = 0

# Create a blank Connect 4 board (6 rows by 7 columns filled with zeros)
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

# Drop a piece in the specified location on the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Check if a column is a valid move (i.e., if there's space to drop a piece)
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0  # True if top row in column is empty

# Get the next open row for a piece in a specific column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:  # Return the first open row (bottom-most available space)
            return r

# Print the board in a way that's visually helpful (flipped so player sees it correctly)
def print_board(board):
    print(np.flip(board, 0))  # Flip the board for display purposes (row 0 at the bottom)

# Check if a player has won the game by connecting pieces
def winning_move(board, piece):
    # Check horizontal locations for a win
    for c in range(COLUMN_COUNT - CONNECT + 1):
        for r in range(ROW_COUNT):
            if np.all(board[r, c:c+CONNECT] == piece):
                return True

    # Check vertical locations for a win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - CONNECT + 1):
            if np.all(board[r:r+CONNECT, c] == piece):
                return True

    # Check positively sloped diagonals (bottom-left to top-right)
    for c in range(COLUMN_COUNT - CONNECT + 1):
        for r in range(ROW_COUNT - CONNECT + 1):
            if all([board[r+i][c+i] == piece for i in range(CONNECT)]):
                return True

    # Check negatively sloped diagonals (top-left to bottom-right)
    for c in range(COLUMN_COUNT - CONNECT + 1):
        for r in range(CONNECT-1, ROW_COUNT):
            if all([board[r-i][c+i] == piece for i in range(CONNECT)]):
                return True

    return False  # No win found


# AI function to evaluate the "score" of the board for a given player
def evaluationFunction(board, piece):
    total_score = 0
    
    # The big code block here was my initial attempt at doing adjacency checks. Later on I come to find out that there was a much
    # much much simpler way of implementing this. The code underneath the block comment provides further insight into it.

    '''
    # For each row
    for row in board:
        # For each column
        for column in row:
            if column == piece:
                h1_weight = 0
                
    for row, column in np.ndindex(board.shape):
        print(int(board[row][column]))

        if int(board[row][column]) == piece:
            print(f"Found piece at {row, column}")
            h1_score += 1
            # Begin adjacency checks

            # Up
            if row + 1 < ROW_COUNT and int(board[row + 1][column]) == piece:
                print("Found piece above")
            # Right
            elif column + 1 < COLUMN_COUNT and int(board[row][column + 1]) == piece:
                print("Found piece to the right")
            # Down
            elif row - 1 >= 0 and int(board[row - 1][column]) == piece:
                print("Found piece below")
            # Left
            elif column - 1 >= 0 and int(board[row][column - 1]) == piece:
                print("Found piece to the left")
    '''


    # These are the scores that will be added up when looking at adjacent pieces.
    # The more adjacent pieces that are within the range 
    adjacency_score_values = {0: 0, 1: 1, 2: 4, 3: 6, 4: 100000, 5: 500000, 6: 999999999999}



    # H1 -> Degree of connectivity (Can we place a piece next to a neighboring piece)
    # or create more possibilities of adjacent pieces


    # I noticed in the winning_move function that this line below the comments is used in a similar fashion
    # However in my case here instead of using all() and iterating through each and every row col I use almost like 
    # a "cursor" that scans the board in 4's 

    # I had to update this check a little bit to take into account Connect 5 and 6. I couldn't just hard code
    # COLUMN_COUNT - 3 for example to make sure that I didn't index the cursor outside of the game space
    # It had to be a little more dynamic based on the amount of CONNECT we are playing to. 

    # Throughout each scan what happens is that the AI is scanning through each line and counting the amount of pieces
    # that are placed within that cursor "slice". The list above ties in the piece amount to value putting higher values
    # on boards that have more adjacent pieces, those that have winning moves have tremendous values.
    # It will continously add up the score based on all of the pieces in succession for all possible combinations of moves.


    ai_score = 0
    
    # Horizontal
    for row in range(ROW_COUNT):
        # We don't want to accidentally check indexes outside of the game window
        for column in range(COLUMN_COUNT - CONNECT + 1):
            chunk = [board[row][column + i] for i in range(CONNECT)]
            chunk_score = chunk.count(piece)
            ai_score += adjacency_score_values[chunk_score]
            total_score += ai_score
    
    # Vertical 
    for row in range(ROW_COUNT - CONNECT + 1):
        for column in range(COLUMN_COUNT):
            chunk = [board[row + i][column] for i in range(CONNECT)]
            chunk_score = chunk.count(piece)
            ai_score += adjacency_score_values[chunk_score]
            total_score += ai_score

    # Positive Diagonal (Bottom Left to Top Right)
    for row in range(ROW_COUNT - CONNECT + 1):
        for column in range(COLUMN_COUNT - CONNECT + 1):
            chunk = [board[row + i][column + i] for i in range(CONNECT)]
            chunk_score = chunk.count(piece)
            ai_score += adjacency_score_values[chunk_score]
            total_score += ai_score

    # Negative Diagonal (Top Left to Bottom Right)
    for row in range(CONNECT - 1, ROW_COUNT):
        for column in range(COLUMN_COUNT - CONNECT + 1):
            chunk = [board[row - i][column + i] for i in range(CONNECT)]
            chunk_score = chunk.count(piece)
            ai_score += adjacency_score_values[chunk_score]
            total_score += ai_score


    # H2 -> Center Column Control
    # These values here represent the score that will be added up when taking into account the amount
    # of pieces in the very center column
    center_piece_score_values = {0:0, 1: 100, 2: 300, 3: 500, 4: 750, 5: 1500, 6: 2000}

    h2_score = 0

    # We perform a similar scan like above but instead we only take into account each and
    # every piece that is in the center column and then count up how many pieces the AI would
    # have. The center piece scores are then added to the h2 and total score
    center_piece_score = [board[i][3] for i in range(ROW_COUNT)]
    center_score = center_piece_score.count(piece)

    h2_score += center_piece_score_values[center_score]
    total_score += h2_score

   
    return total_score

# Minimax function to determine the best move for the AI
def minimax(board, depth, maximizingPlayer, alpha, beta):
    valid_locations = get_valid_locations(board)  # Get valid columns to drop the piece

    is_terminal = is_terminal_node(board)
    
    # Terminal state evaluation (game over: win/loss/draw)
    # here is where you will add Max depth and the return of the evaluation function
    if is_terminal:
        if winning_move(board, 2):
            return (None, 100000000000000)  # Large score for AI win
        elif winning_move(board, 1):
            return (None, -10000000000000)  # Large negative score for player win
        else:  # Game over, no moves left
            return (None, 0)
   
    # This is also where we check if we reached the maximum depth level of search
    # I used the below commented version only to find out that I should not be using
    # alpha and beta directly to return a value, which is what ChatGPT helped me point
    # out when trying to see if I could simplify the code below
    # Instead I have to call the evaluation function here to return a weight to associate
    # to the move
    """
    if depth == 0:
        if maximizingPlayer:
            return (None, alpha)
        else:
            return (None, beta)
    """
    # If we have reached the maximum depth of our search limit then we must return the score
    # of the deepest node possible and then run our evaluations based off of that node
    if depth == 0:
        return (None, evaluationFunction(board, 2))

 
    # Player move
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)  # Pick a random valid column

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()  # Copy the board
            drop_piece(b_copy, row, col, 2)

            # If we find a winning move on the board then immediately return out a huge score
            if winning_move(b_copy, 1):
                return col, 99999999999999
            
            # We perform the minimax here on the new board and continue by decreasing the depth
            # Once this function goes all the way down the tree it will retun back the best 
            # move that it has evaluated based on what the deepest board state is
            minimax_score = minimax(b_copy, depth-1, False, alpha, beta)[1]
            
            # if the current minimax score of the new board is greater than -infinity
            if minimax_score > value:
                value = minimax_score
                column = col
                # Then we must set the alpha to the max found score within the search trees
                # This score will be carried up the tree to find the best possible score
                alpha = max(alpha, value)

            # However if it turns out that the evaluated score of the minimax search is not greater
            # than some of the other child nodes, we can simply break out of the loop. This is because
            # there are better options that the AI can traverse through so we can prune the search
            if alpha >= beta:
                break

        return column, value

    # AI Move
    else:
        value = math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 1)

            # If we find a winning move on the board then immediately return out a huge score
            if winning_move(b_copy, 2):
                return col, 99999999999999

            # We perform the minimax here on the new board and continue by decreasing the depth
            # Once this function goes all the way down the tree it will retun back the best 
            # move that it has evaluated based on what the deepest board state is
            minimax_score = minimax(b_copy, depth-1, True, alpha, beta)[1]

            # If the newly calculated minimax score is less than the value we have saved
            # it means that it is a meaningful node that we must account for
            if minimax_score < value:
                value = minimax_score
                column = col

                # Same as above for max however we find the worst possible move that can be made against
                # the player whos piece is being placed           
                beta = min(beta, value)

            # And again here we prune anything does not have a lower score than the currently
            # assigned alpha score. We keep only the most important moves
            if beta <= alpha:
                break

        return column, value

# Get a list of all valid columns (i.e., those with open spaces)
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# Check if the game is over (win or no valid moves left)
def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

# Function to draw the board (visual representation)
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):      
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()  # Update the display with the new board state

# Main game logic
board = create_board()  # Create the initial empty board
print_board(board)
print("\n")
game_over = False
turn = 0  # Variable to track turns (0 for Player 1, 1 for Player 2/AI)

draw_board(board)  # Draw the initial empty board

# Main game loop
while not game_over:
    # Event handler to check for user input and quitting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # If the user closes the game window
            sys.exit()

        
        
        # Display the piece that the human player is about to drop
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))  # Clear the top row
            posx = event.pos[0]  # Get the x-position of the mouse
            if turn == 0:  # Player 1's turn
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            else:  # Player 2's (AI's) turn
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()  # Update the display

        # Handle mouse click event (drop a piece)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))  # Clear the top row
            if turn == 0:  # Player 1's turn
                posx = event.pos[0]  # Get the x-position of the click
                col = int(math.floor(posx/SQUARESIZE))  # Determine the column based on the x-position

                if is_valid_location(board, col):  # Check if the column is valid
                    row = get_next_open_row(board, col)  # Get the next open row in the column
                    drop_piece(board, row, col, 1)  # Drop Player 1's piece

                    if winning_move(board, 1):  # Check if Player 1 wins
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40, 10))  # Display the winning message
                        game_over = True  # End the game

                    turn += 1  # Switch to the next turn
                    turn = turn % 2  # Ensure turn alternates between 0 and 1

                    print_board(board)  # Print the board to the console
                    print("\n")
                    draw_board(board)  # Draw the updated board


    # AI's turn (Player 2)
    if turn == 1 and not game_over:

        start_time = time.time()  # Start timer to measure AI move time
        #here is where you will call min/max
        col, mnimax_score = minimax(board, 6, True, -math.inf, math.inf)


        end_time = time.time()  # Stop the timer
        time_taken = end_time - start_time  # Calculate the time taken for the AI's move

        # Update the total time and number of moves for performance analysis
        total_time += time_taken
        move_count += 1

        print(f"AI Move Time: {time_taken:.4f} seconds")  # Print the time for the current move
        print(f"Average AI Move Time: {total_time / move_count:.4f} seconds")  # Print the average move time

        if is_valid_location(board, col):  # Check if the column is valid
            pygame.time.wait(500)  # Delay for visual effect
            row = get_next_open_row(board, col)  # Get the next open row in the column
            drop_piece(board, row, col, 2)  # Drop the AI's piece

            if winning_move(board, 2):  # Check if the AI wins
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40, 10))  # Display the winning message
                game_over = True  # End the game

            print_board(board)  # Print the board to the console
            draw_board(board)  # Draw the updated board

            turn += 1  # Switch to the next turn
            turn = turn % 2  # Ensure turn alternates between 0 and 1

    # End the game if someone has won
    if game_over:
        pygame.time.wait(3000)  # Wait for 3 seconds before exiting
