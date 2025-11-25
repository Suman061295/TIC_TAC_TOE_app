import os
from flask import Flask, jsonify, request, session
from flask_session import Session # Using flask_session for simple state management

# --- Game State and Logic ---
BOARD_SIZE = 9 # 3x3 board
WINNING_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6)             # Diagonals
]

def check_winner(board):
    for a, b, c in WINNING_COMBOS:
        if board[a] == board[b] and board[b] == board[c] and board[a] != ' ':
            return board[a]
    if ' ' not in board:
        return 'Draw'
    return None

def new_game():
    return {
        'board': [' '] * BOARD_SIZE,
        'current_player': 'X',
        'game_over': False,
        'message': "Player X's turn."
    }
# --- Flask Setup ---
app = Flask(__name__)

# Configure session (required for storing game state across requests)
# NOTE: In a real-world k8s deployment, use a centralized store like Redis for sessions.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem" # Temporary, local storage for testing
app.secret_key = os.urandom(24) 
Session(app)

@app.route('/game', methods=['GET'])
def get_state():
    """Get the current game state."""
    if 'game' not in session:
        session['game'] = new_game()
    return jsonify(session['game'])

@app.route('/game/move', methods=['POST'])
def make_move():
    """Process a move from the client."""
    game = session.get('game', new_game())
    
    if game['game_over']:
        return jsonify(game)
    
    data = request.get_json()
    index = data.get('index')

    if index is None or not (0 <= index < BOARD_SIZE):
        game['message'] = "Invalid move index."
    elif game['board'][index] != ' ':
        game['message'] = "Cell already taken."
    else:
        # Valid move: Update board
        game['board'][index] = game['current_player']
        winner = check_winner(game['board'])

        if winner:
            game['game_over'] = True
            game['message'] = f"Game Over! Player {winner} wins!" if winner != 'Draw' else "Game Over! It's a Draw!"
        else:
            # Switch player and update message
            game['current_player'] = 'O' if game['current_player'] == 'X' else 'X'
            game['message'] = f"Player {game['current_player']}'s turn."

    session['game'] = game
    return jsonify(game)

@app.route('/game/reset', methods=['POST'])
def reset_game():
    """Start a new game."""
    session['game'] = new_game()
    return jsonify(session['game'])

if __name__ == '__main__':
    # Flask runs on port 5000 as defined in the Dockerfile and K8s manifest
    app.run(host='0.0.0.0', port=5000)