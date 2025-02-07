# game.py
import random

class BingoGame:
    def __init__(self):
        self.REMOVED_NUMBER = "█"
        self.games = {}  # Dictionary to store game states for different sessions

    def init_game(self, session_id):
        self.games[session_id] = {
            'computer_b': self.create_board(),
            'player_b': self.create_board(),
            'computer_n': None,
            'player_n': None,
            'player_numbers': [],  # track player numbers
            'available_numbers': list(range(1, 26)),  # track computer numbers
            'count_p': 0,
            'count_c': 0,
            'winner': None,
            'show_computer': None,
            'mode': None,
            'hard_mode_position' : self.get_hard_mode_position(),
            'move_history' : [] # include a new variable
        }
        return self.games[session_id]

    def get_game_state(self, session_id):
        return self.games.get(session_id)


    def get_hard_mode_position(self):
        x = [
            [
                (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), 
                (1, 1), (1, 3),
                (2, 1), (2, 2), (2, 3),
                (3, 1), (3, 3),
                (4, 0), (4, 1), (4, 3), (4, 4)
            ],
            [
                (0, 0), (0, 4), 
                (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                (2, 2), (2, 4),
                (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                (4, 0), (4, 4),
            ],
            [
                (0, 0), (0, 1), (0, 3), (0, 4),
                (1, 1), (1, 3),
                (2, 1), (2, 2), (2, 3),
                (3, 1), (3, 3),
                (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
            ],

            [
                (0, 0), (0, 4), 
                (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                (2, 0), (2, 2),
                (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                (4, 0), (4, 4),
            ],
        ]
        return random.choice(x)

        
    def end_game(self, session_id):
        if session_id in self.games:
            del self.games[session_id]

    # Rest of the game logic methods remain the same, but now take session_id as a parameter
    def create_board(self):
        nums = [i for i in range(1, 26)]
        board = [[0 for _ in range(5)] for _ in range(5)]

        for i in range(5):
            for j in range(5):
                x = random.choice(nums)
                board[i][j] = x
                nums.remove(x)

        return board

    def find_key_mark(self, session_id, b1, b2, key):
        if self.games[session_id]['mode'] == "hard":
            for i in range(5):
                for j in range(5):
                    if b1[i][j] == key:
                        b1[i][j] = self.REMOVED_NUMBER

            positions = self.games[session_id]['hard_mode_position']

            for i in positions:
                if b2[i[0]][i[1]] != self.REMOVED_NUMBER:
                    b2[i[0]][i[1]] = self.REMOVED_NUMBER
                    break
        else:
            for i in range(5):
                for j in range(5):
                    if b1[i][j] == key:
                        b1[i][j] = self.REMOVED_NUMBER
                    if b2[i][j] == key:
                        b2[i][j] = self.REMOVED_NUMBER

    def check_bingo(self, b):
        count = 0
        # row
        for i in range(5):
            if all([spot == self.REMOVED_NUMBER for spot in b[i]]):
                count += 1

        # column
        column = [[b[i][j] for i in range(5)] for j in range(5)]
        for i in range(5):
            if all([spot == self.REMOVED_NUMBER for spot in column[i]]):
                count += 1

        diagonal1 = [b[i][i] for i in range(5)]
        if all([spot == self.REMOVED_NUMBER for spot in diagonal1]):
            count += 1

        diagonal2 = [b[i][5 - i - 1] for i in range(5)]
        if all([spot == self.REMOVED_NUMBER for spot in diagonal2]):
            count += 1

        return count

    def score(self, x, p, q):
        count = 0
        for k in range(5):
            if x[k][q] == self.REMOVED_NUMBER:
                count += 1
        for k in range(5):
            if x[p][k] == self.REMOVED_NUMBER:
                count += 1
        if p == q:
            for k in range(5):
                if x[k][k] == self.REMOVED_NUMBER:
                    count += 1
        if p + q == 4:
            for k in range(5):
                if x[k][4 - k] == self.REMOVED_NUMBER:
                    count += 1
        return count

    def ask_computer(self, session_id, computer_b, CHALLENGE):
        game_state = self.games[session_id]
        
        if CHALLENGE == "hard":
            x = random.choice(game_state['available_numbers'])
            return x

        if CHALLENGE == "easy":
            x = random.choice(game_state['available_numbers'])
            return x

        if CHALLENGE == "medium":
            if computer_b[2][2] in game_state['available_numbers']:
                return computer_b[2][2]

            column = [[computer_b[j][i] for j in range(5)] for i in range(5)]
            for i in range(5):
                if computer_b[i].count(self.REMOVED_NUMBER) == 4:
                    for j in range(5):
                        if computer_b[i][j] != self.REMOVED_NUMBER:
                            return computer_b[i][j]

                if column[i].count(self.REMOVED_NUMBER) == 4:
                    for j in range(5):
                        if column[i][j] != self.REMOVED_NUMBER:
                            return column[i][j]

            main_diagonal = [computer_b[i][i] for i in range(5)]
            if main_diagonal.count(self.REMOVED_NUMBER) == 4:
                for j in range(5):
                    if main_diagonal[j] != self.REMOVED_NUMBER:
                        return main_diagonal[j]

            secondary_diagonal = [computer_b[i][4 - i] for i in range(5)]
            if secondary_diagonal.count(self.REMOVED_NUMBER) == 4:
                for j in range(5):
                    if secondary_diagonal[j] != self.REMOVED_NUMBER:
                        return secondary_diagonal[j]

            high_score = -1
            best = -1

            for i in range(5):
                for j in range(5):
                    if computer_b[i][j] == self.REMOVED_NUMBER:
                        continue

                    temp = self.score(computer_b, i, j)

                    if temp >= high_score:
                        high_score = temp
                        best = computer_b[i][j]

            return best


    def place_elements_randomly(self, session_id, board):
        game_state = self.games[session_id]
        # Find all positions on the board that are not REMOVED_NUMBER
        empty_positions = [(i, j) for i in range(5) for j in range(5) if board[i][j] != self.REMOVED_NUMBER]

        random.shuffle(empty_positions)
        # Place each element in the available list into a random empty position
        available_nums = game_state['available_numbers']
        for element in available_nums:
            if not empty_positions:  # Stop if there are no more empty positions
                break
            # Get a random empty position and place the element there
            pos = empty_positions.pop()
            board[pos[0]][pos[1]] = element
        return board

