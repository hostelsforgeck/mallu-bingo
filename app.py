from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from game import BingoGame
import uuid  # This import is fine, as long as it's the standard uuid module from Python 3

app = Flask(__name__)
app.secret_key = 'you_cant_find_my_secret_key'  # Change this to a secure secret key in production

game = BingoGame()

class GameSettingsForm(FlaskForm):
    mode = SelectField('Mode', choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], validators=[DataRequired()])
    show_computer = BooleanField('Show_computer')
    submit = SubmitField("Let's Go")

def get_or_create_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Python 3's uuid is fine here
    return session['session_id']

@app.route('/', methods=['GET', 'POST'])
def home():
    session_id = get_or_create_session()
    form = GameSettingsForm()
    
    if form.validate_on_submit():
        game_state = game.get_game_state(session_id) or game.init_game(session_id)
        game_state['mode'] = form.mode.data
        game_state['show_computer'] = form.show_computer.data
        game_state['player_b'] = game.create_board()
        return redirect(url_for('play'))
    else:
        game_state = game.get_game_state(session_id) or game.init_game(session_id)
        return render_template('index.html', form=form, board=game_state['player_b'])

@app.route('/play')
def play():
    session_id = get_or_create_session()
    game_state = game.get_game_state(session_id)
    if not game_state:
        return redirect(url_for('home'))
    return render_template('play.html', game_state=game_state)

@app.route('/mark', methods=['POST'])
def mark():
    session_id = get_or_create_session()
    game_state = game.get_game_state(session_id)
    
    if not game_state:
        return jsonify({'status': 'error', 'message': 'No active game'}), 400

    data = request.get_json()
    number = data.get('number')

    if number and int(number) in range(1, 26):
        number = int(number)

        if game_state["winner"] is not None:
            return jsonify({
                'status': 'game_over',
                'winner': 'player' if game_state["winner"] == 1 else 'computer'
            })

        if number not in game_state['player_numbers']:
            game_state["player_n"] = number
            game_state['move_history'].append(number)

            game.find_key_mark(session_id, game_state['player_b'],
                             game_state['computer_b'], number)
            game_state['player_numbers'].append(number)

            game_state["count_p"] = game.check_bingo(game_state['player_b'])
            game_state["count_c"] = game.check_bingo(game_state['computer_b'])

            if game_state["count_p"] >= 5:
                game_state["winner"] = 1
                return jsonify({
                    'status': 'game_over',
                    'winner': 'player',
                    'player_board': game_state['player_b'],
                    'move_history': game_state['move_history']
                })

            # Computer's move
            game_state['computer_n'] = game.ask_computer(
                session_id, game_state['computer_b'], game_state['mode'])
                
            game_state['move_history'].append(game_state['computer_n'])

            game.find_key_mark(
                session_id, game_state['player_b'], game_state['computer_b'], game_state['computer_n'])
            game_state['available_numbers'].remove(game_state['computer_n'])

            game_state["count_c"] = game.check_bingo(game_state['computer_b'])
            game_state["count_p"] = game.check_bingo(game_state['player_b'])

            if game_state["count_c"] >= 5:
                game_state["winner"] = 0
                if game_state['mode'] == 'hard':
                    game_state['computer_b'] = game.place_elements_randomly(session_id,game_state['computer_b'])
                return jsonify({
                    'status': 'game_over',
                    'winner': 'computer',
                    'computer_board': game_state['computer_b'],
                    'move_history': game_state['move_history']
                })

            return jsonify({
                'status': 'success',
                'player_board': game_state['player_b'],
                'computer_board': game_state['computer_b'] if game_state['show_computer'] else None,
                'computer_number': game_state['computer_n'],
                'player_number': game_state['player_n'],
                'count_p': game_state['count_p'],
                'count_c': game_state['count_c'],
                'winner': game_state['winner'],
                'move_history': game_state['move_history']
            })

    return jsonify({'status': 'error', 'message': 'Invalid number'}), 400

@app.route('/generate_board', methods=['GET'])
def generate_board():
    session_id = get_or_create_session()
    game_state = game.get_game_state(session_id)
    if not game_state:
        return jsonify({'status': 'error', 'message': 'No active game'}), 400
    
    game_state['player_b'] = game.create_board()
    return jsonify(game_state['player_b'])

@app.route('/submit_settings', methods=['POST'])
def submit_settings():
    session_id = get_or_create_session()
    game_state = game.get_game_state(session_id)
    if not game_state:
        return jsonify({'status': 'error', 'message': 'No active game'}), 400

    data = request.get_json()
    if data:
        game_state['mode'] = data.get('mode')
        game_state['show_computer'] = data.get('show_computer', False)
        game_state['player_b'] = data.get('board', [])

        return jsonify({
            'status': 'success',
            'mode': game_state['mode'],
            'show_computer': game_state['show_computer'],
            'board': game_state['player_b']
        })

    return jsonify({'error': 'Invalid form submission'}), 400

@app.route('/win')
def win():
    session_id = get_or_create_session()
    game_state = game.get_game_state(session_id)
    
    if not game_state:
        return redirect(url_for('home'))

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
        move_history=game_state['move_history']
    )

@app.route('/play_again')
def play_again():
    session_id = get_or_create_session()
    game.end_game(session_id)
    game.init_game(session_id)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)