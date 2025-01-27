from flask import Flask, render_template, request, jsonify, redirect, url_for, g
from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import random
import json

app = Flask(__name__)
# Replace with a real secret key in production
app.secret_key = 'you_cant_find_my_secret_key'

# Global game state
game_state = {}

# SETTNGS

REMOVED_NUMBER = "█"  # "֍"  "•"  "Ø"


class GameSettingsForm(FlaskForm):
    mode = SelectField('Mode', choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], validators=[DataRequired()])
    show_computer = BooleanField('Show_comouter')
    submit = SubmitField("Let's Go")


def create_board():
    nums = [i for i in range(1, 26)]
    board = [[0 for _ in range(5)] for _ in range(5)]

    for i in range(5):
        for j in range(5):
            x = random.choice(nums)
            board[i][j] = x
            nums.remove(x)

    return board


def init_game():
    global game_state
    game_state = {
        'computer_b': create_board(),
        'player_b': create_board(),
        'computer_n': None,
        'player_n': None,
        'player_numbers': [],  # track player numbers
        'available_numbers': list(range(1, 26)),  # track computer numbers
        'count_p': 0,
        'count_c': 0,
        'winner': None,
        'show_computer': None,
        'mode': None,
    }


@app.route('/', methods=['GET', 'POST'])
def home():
    form = GameSettingsForm()
    if form.validate_on_submit():
        game_state['mode'] = form.mode.data
        game_state['show_computer'] = form.show_computer.data
        game_state['player_b'] = create_board()
        return redirect(url_for('play'))
    else:
        if not game_state:
            init_game()
        return render_template('index.html', form=form, board=game_state['player_b'])


@app.route('/play')
def play():
    return render_template('play.html', game_state=game_state)


@app.route('/mark', methods=['POST'])
def mark():
    data = request.get_json()
    number = data.get('number')

    if number and int(number) in range(1, 26):
        number = int(number)

        if game_state["winner"] is not None:
            return jsonify({
                'status': 'game_over',
                'winner': 'player' if game_state["winner"] == 1 else 'computer'
            })

        # Prevent duplicate moves
        if number not in game_state['player_numbers']:
            game_state["player_n"] = number

            # Call find_key_mark to mark player's board
            find_key_mark(game_state['player_b'],
                          game_state['computer_b'], number)
            game_state['player_numbers'].append(number)

            # Check for winner on the player's board
            game_state["count_p"] = check_bingo(game_state['player_b'])
            game_state["count_c"] = check_bingo(game_state['computer_b'])

            print(f"pn : {game_state['player_n']}")
            print(f"pb : {game_state['player_b']}")
            print("count_p : ", {game_state["count_p"]})
            print()

            # End the game if the player wins
            if game_state["count_p"] >= 5:
                game_state["winner"] = 1
                return jsonify({
                    'status': 'game_over',
                    'winner': 'player',
                    'player_board': game_state['player_b']
                })

            # Simulate computer's move
            game_state['computer_n'] = ask_computer(
                game_state['computer_b'], game_state['mode'])

            find_key_mark(
                game_state['player_b'], game_state['computer_b'], game_state['computer_n'])
            game_state['available_numbers'].remove(game_state['computer_n'])

            # Check for winner on the computer's board
            game_state["count_c"] = check_bingo(game_state['computer_b'])
            game_state["count_p"] = check_bingo(game_state['player_b'])

            print()
            print(f"cn : {game_state['computer_n']}")
            print(f"cb : {game_state['computer_b']}")
            print("count_c : ", {game_state["count_c"]})

            # End the game if the computer wins
            if game_state["count_c"] >= 5:
                game_state["winner"] = 0
                return jsonify({
                    'status': 'game_over',
                    'winner': 'computer',
                    'computer_board': game_state['computer_b']
                })

            return jsonify({
                'status': 'success',
                'player_board': game_state['player_b'],
                'computer_board': game_state['computer_b'] if game_state['show_computer'] else None,
                'computer_number': game_state['computer_n'],
                'player_number': game_state['player_n'],
                'count_p': game_state['count_p'],
                'count_c': game_state['count_c'],
                'winner': game_state['winner']
            })

    return jsonify({'status': 'error', 'message': 'Invalid number'}), 400


@app.route('/generate_board', methods=['GET'])
def generate_board():
    game_state['player_b'] = create_board()
    return jsonify(game_state['player_b'])


@app.route('/submit_settings', methods=['POST'])
def submit_settings():

    data = request.get_json()

    if data:
        game_state['mode'] = data.get('mode')
        game_state['show_computer'] = data.get('show_computer', False)
        game_state['player_b'] = data.get('board', [])

        # print settings and board
        print("Game settings:")
        print(f"Mode: {game_state['mode']}")
        print(f"Show Computer: {game_state['show_computer']}")
        print("Chosen Board:")
        for row in game_state['player_b']:
            print(row)

        return jsonify({
            'status': 'success',
            'mode': game_state['mode'],
            'show_computer': game_state['show_computer'],
            'board': game_state['player_b']
        })

    return jsonify({'error': 'Invalid form submission'}), 400


# ========================================================================
def find_key_mark(b1, b2, key):
    # marking number selected by players in both tables

    if game_state['mode'] == "hard":
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


def ask_computer(computer_b, CHALLENGE):
    # ask computer for a number to mark
    # Hard mode: ensure computer wins after the 16th move
    if CHALLENGE == "hard":
        print("hard")

        x = random.choice(game_state['available_numbers'])
        return x

        # the real catch is in find_mark_key()

    if CHALLENGE == "easy":
        print("easy")

        # ------------------------------------------------------
        # 1.EASY (select a random number from available numbers)

        x = random.choice(game_state['available_numbers'])
        return x
        # ------------------------------------------------------

    if CHALLENGE == "medium":
        print("medium")

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
        if computer_b[2][2] in game_state['available_numbers']:
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
    empty_positions = [(i, j) for i in range(5)
                       for j in range(5) if board[i][j] != REMOVED_NUMBER]

    # Shuffle the list of available positions
    random.shuffle(empty_positions)

    # Place each element in the available list into a random empty position
    for element in game_state['available_numbers']:
        if not empty_positions:  # Stop if there are no more empty positions
            break
        # Get a random empty position and place the element there
        pos = empty_positions.pop()
        board[pos[0]][pos[1]] = element
    return board

# ====================================================================


@app.route('/win')
def win():
    if game_state["winner"] == 1:
        winner = "Player"
    elif game_state["winner"] == 0:
        winner = "Computer"
    else:
        return redirect(url_for('play'))

    return render_template(
        "win.html",
        candidate=winner,
        player_b=game_state['player_b'],
        computer_b=game_state['computer_b'],
        count_c=game_state["count_c"],
        count_p=game_state["count_p"],
    )


@app.route('/play_again')
def play_again():
    init_game()  # Reset the game state
    return redirect(url_for('home'))  # Redirect to the home page


if __name__ == '__main__':
    init_game()
    app.run(debug=True)
