import random

available = [i for i in range(1, 26)]

# SETTNGS
REMOVED_NUMBER = "█"  # "֍"  "•"  "Ø"
SHOW_COMPUTER_BOARD = True  # see how computer play.
CHALLENGE = "medium"  # "easy", "medium"



def create_board():
    nums = [i for i in range(1, 26)]
    board = [[0 for _ in range(5)] for _ in range(5)]

    for i in range(5):
        for j in range(5):
            x = random.choice(nums)
            board[i][j] = x
            nums.remove(x)

    return board



def find_key_mark(b1, b2, key):
    # marking number selected by players in both tables


    if CHALLENGE == "hard":
        # in mode hard we use a bruteforce method to win.

        for i in range(5):
            for j in range(5):
                if b1[i][j] == key:
                    b1[i][j] = REMOVED_NUMBER


        positions = [
            (0, 0), (0, 1), (0, 2), (0, 3),
            (0, 4), (1, 1), (1, 3), (2, 1),
            (2, 2), (2, 3), (3, 1), (3, 3),
            (4, 0), (4, 1), (4, 3), (4, 4)
                   ]

        for i in positions:
            if b2[i[0]][i[1]] != REMOVED_NUMBER:  
                b2[i[0]][i[1]] = REMOVED_NUMBER
                break

    else:
        for i in range(5):
            for j in range(5):
                if b1[i][j] == key:
                    b1[i][j] = REMOVED_NUMBER

                if b2[i][j] == key:
                    b2[i][j] = REMOVED_NUMBER


def ask_player():
    # ask player for a number to mark
    print()
    while True:
        x = input("Player   : ")
        if x.isdigit() and int(x) in available:
            available.remove(int(x))
            return int(x)


def ask_computer(computer_b):
    # ask computer for a number to mark
    # Hard mode: ensure computer wins after the 16th move
    if CHALLENGE == "hard":
        x = random.choice(available)
        return x

        # the real catch is in find_mark_key()


    if CHALLENGE == "easy":
        # print("easy")
        
        # ------------------------------------------------------
        # 1.EASY (select a random number from available numbers)

        x = random.choice(available)
        return x
        # ------------------------------------------------------

    if CHALLENGE == "medium":
       
        def score(x, p, q):
            # score calculation for computer
            count = 0

            # Check the column
            for k in range(5):
                if x[k][q] == REMOVED_NUMBER:
                    count += 1

            # Check the row
            for k in range(5):
                if x[p][k] == REMOVED_NUMBER:
                    count += 1

            # Check primary diagonal (if the cell is on this diagonal)
            if p == q:
                for k in range(5):
                    if x[k][k] == REMOVED_NUMBER:
                        count += 1

            # Check secondary diagonal (if the cell is on this diagonal)
            if p + q == 4:
                for k in range(5):
                    if x[k][4 - k] == REMOVED_NUMBER:
                        count += 1

            return count

        # -------------------------------------

        # cross the middle element as first move to improve chances
        if computer_b[2][2] in available:
            return computer_b[2][2]

        else:

            column = [[computer_b[j][i] for j in range(5)] for i in range(5)]
            for i in range(5):
                # Check for any rows have 4 "█"(or REMOVED_NUMBER) if yes select the 5th number
                if computer_b[i].count(REMOVED_NUMBER) == 4:
                    for j in range(5):
                        if computer_b[i][j] != REMOVED_NUMBER:
                            return computer_b[i][j]

                # Check for any colums have 4 "█"(or REMOVED_NUMBER) if yes select the 5th number
                if column[i].count(REMOVED_NUMBER) == 4:
                    for j in range(5):
                        if column[i][j] != REMOVED_NUMBER:
                            return column[i][j]

            # Check for main_diagonal have 4 "█"(or REMOVED_NUMBER) if yes select the 5th number
            main_diagonal = [computer_b[i][i] for i in range(5)]
            if main_diagonal.count(REMOVED_NUMBER) == 4:
                for j in range(5):
                    if main_diagonal[j] != REMOVED_NUMBER:
                        return main_diagonal[j]

            # Check for secondary diagonal have 4 "█"(or REMOVED_NUMBER) if yes select the 5th number
            secondary_diagonal = [computer_b[i][4 - i] for i in range(5)]
            if secondary_diagonal.count(REMOVED_NUMBER) == 4:
                for j in range(5):
                    if secondary_diagonal[j] != REMOVED_NUMBER:
                        return secondary_diagonal[j]

            # 2.if there is no row/col/diagnal which have 4 "█"(or REMOVED_NUMBER)
            # we will return best number by calculating the high_score
            high_score = -1
            best = -1

            for i in range(5):
                for j in range(5):

                    if computer_b[i][j] == REMOVED_NUMBER:
                        continue

                    temp = score(computer_b, i, j)

                    if temp >= high_score:
                        high_score = temp
                        best = computer_b[i][j]

            print(high_score, best)

            return best

def place_elements_randomly(board):
    # Find all positions on the board that are not REMOVED_NUMBER
    empty_positions = [(i, j) for i in range(5) for j in range(5) if board[i][j] != REMOVED_NUMBER]
    
    # Shuffle the list of available positions
    random.shuffle(empty_positions)
    
    # Place each element in the available list into a random empty position
    for element in available:
        if not empty_positions:  # Stop if there are no more empty positions
            break
        # Get a random empty position and place the element there
        pos = empty_positions.pop()
        board[pos[0]][pos[1]] = element
    return board

def check_bingo(b):
    # if every element in the row/column == REMOVED NUMBER: increment count

    count = 0
    # row
    for i in range(5):
        if all([spot == REMOVED_NUMBER for spot in b[i]]):
            # print("row")
            count += 1

    # column
    column = [[b[i][j] for i in range(5)] for j in range(5)]
    for i in range(5):
        if all([spot == REMOVED_NUMBER for spot in column[i]]):
            # print("column")
            count += 1

    diagonal1 = [b[i][i] for i in range(5)]
    if all([spot == REMOVED_NUMBER for spot in diagonal1]):
        # print("dia1")
        count += 1

    diagonal2 = [b[i][5 - i - 1] for i in range(5)]
    if all([spot == REMOVED_NUMBER for spot in diagonal2]):
        # print("dia2")
        count += 1

    return count


def print_bingo(index):
    # print bingo according to the count in check_bingo()
    BINGO = "BINGO"

    if index <= 0:
        pass
    else:
        if index >= 5:
            index = 5

        print('+----------------------------+')

        print("| ", end=" ")
        for i in range(index):
            print(f"{BINGO[i]}   ", end=" ")
        print(" |", end="")

        print('\n+----------------------------+')


def main():
    # create boards for computer and player
    if CHALLENGE == "hard":
        computer_b = [[0 for _ in range(5)] for _ in range(5)]
    else:
        computer_b = create_board()

    player_b = create_board()

    while True:

        # PLAYER
        player_n = ask_player()

        # AUTOMATION -> Computer vs Computer

        # player_n = ask_computer(player_b)
        # available.remove(player_n)
        # print(f"\nplayer   : {player_n}")

        find_key_mark(player_b, computer_b, player_n)

        count_p = check_bingo(player_b)
        count_c = check_bingo(computer_b)

        if count_p >= 5:
            print("\n@@@@@@@ PLAYER WON @@@@@@@\n")
            print_all_boards(player_b, count_p, computer_b, count_c, player_first=True)
            break

        if count_c >= 5:
            print("\n@@@@@@@ COMPUTER WON @@@@@@@\n")
            print_all_boards(player_b, count_p, computer_b, count_c, player_first=False)
            break

        # COMPUTER
        computer_n = ask_computer(computer_b)
        print(f"Computer : {computer_n}\n")

        # removing that number from available to prevent user say the same number again.
        available.remove(computer_n)

        find_key_mark(player_b, computer_b, computer_n)

        count_c = check_bingo(computer_b)
        count_p = check_bingo(player_b)

        if count_c >= 5:
            print("\n@@@@@@@ COMPUTER WON @@@@@@@\n")
            print_all_boards(player_b, count_p, computer_b, count_c, player_first=False)
            break

        if count_p >= 5:
            print("\n@@@@@@@ PLAYER WON @@@@@@@\n")
            print_all_boards(player_b, count_p, computer_b, count_c, player_first=True)
            break

        # --
        print("      -- PLAYER BOARD --")
        print_bingo(count_p)
        print_board(player_b)

        if SHOW_COMPUTER_BOARD and CHALLENGE!="hard":
            print("     -- COMPUTER BOARD --")
            print_bingo(count_c)
            print_board(computer_b)


if __name__ == '__main__':
    main()
