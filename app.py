from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import random
import os

app = Flask(__name__)


app.secret_key = os.environ.get('SECRET_KEY', '9c9b7cf3531af44af87c9eb43ac673ec73e4f822ba675dcf')


def get_db_connection():
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row  
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/player_status')
def player_status():
    if 'player_id' not in session:
        session['player_id'] = 1  
    conn = get_db_connection()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (session['player_id'],)).fetchone()
    conn.close()

    if player:
        return jsonify(dict(player))
    else:
        return jsonify({"error": "Player not found"}), 404

@app.route('/api/inventory')
def get_inventory():
    if 'player_id' not in session:
        session['player_id'] = 1  

    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM inventory WHERE player_id = ?", (session['player_id'],))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/complete_quest/<quest_name>')
def complete_quest(quest_name):
    if 'player_id' not in session:
        session['player_id'] = 1

    conn = get_db_connection()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (session['player_id'],)).fetchone()

    completed = player['quests_completed'].split(',') if player['quests_completed'] else []
    if quest_name not in completed:
        completed.append(quest_name)
        new_score = player['score'] + 50
        conn.execute("UPDATE players SET quests_completed = ?, score = ? WHERE id = ?",
                     (','.join(completed), new_score, session['player_id']))
        conn.commit()

    conn.close()
    return redirect(url_for('index'))

@app.route('/battle')
def battle():
    if 'player_id' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (session['player_id'],)).fetchone()
    conn.close()

    if not player:
        return "Player not found in database", 404

    if 'health' not in player:
        return "Player health not found!", 500

    enemy_power = random.randint(5, 30)
    player_health = player['health'] - enemy_power
    result = ""

    if player_health <= 0:
        result = f"You were defeated by an enemy with {enemy_power} power!"
        conn = get_db_connection()
        conn.execute("UPDATE players SET health = 100, score = 0 WHERE id = ?", (session['player_id'],))
        conn.commit()
        conn.close()
    else:
        result = f"You defeated an enemy with {enemy_power} power!"
        new_score = player['score'] + 20
        conn = get_db_connection()
        conn.execute("UPDATE players SET health = ?, score = ? WHERE id = ?",
                     (player_health, new_score, session['player_id']))
        conn.commit()
        conn.close()

    return render_template('battle_result.html', result=result, player=player)

def check_level_up(player_id):
    conn = get_db_connection()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    new_level = player['level']
    new_score = player['score']

    if new_score >= player['level'] * 100:
        new_level += 1
        conn.execute("UPDATE players SET level = ? WHERE id = ?", (new_level, player_id))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

@app.route('/run_query', methods=['POST'])
def run_query():
    query = request.form.get('query')

    if not query:
        return jsonify({'success': False, 'error': 'No query provided'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Query executed successfully!',
                'result': [dict(zip(columns, row)) for row in result]
            })
        else:
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Query executed successfully!', 'result': []})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_db')
def test_db():
    conn = get_db_connection()
    data = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

if __name__ == '__main__':
    app.run(debug=True)
