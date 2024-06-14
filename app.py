from flask import Flask, render_template, request
import sqlite3
import csv

app = Flask(__name__)

# Veritabanı bağlantısı ve tablo oluşturma
def init_db():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# CSV dosyasından soruları içeri aktarma
def import_questions_from_csv(filepath):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute('''
                INSERT INTO questions (question, option1, option2, option3, option4, answer)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['question'], row['option1'], row['option2'], row['option3'], row['option4'], row['answer']))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    highest_score, highest_scorer = get_highest_score()
    return render_template('index.html', highest_score=highest_score, highest_scorer=highest_scorer)

@app.route('/quiz')
def quiz():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    questions = cursor.fetchall()
    conn.close()
    highest_score, highest_scorer = get_highest_score()
    return render_template('quiz.html', questions=questions, highest_score=highest_score, highest_scorer=highest_scorer)

@app.route('/result', methods=['POST'])
def result():
    score = 0
    name = request.form.get('name')
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    questions = cursor.fetchall()
    for question in questions:
        selected_option = request.form.get(str(question[0]))
        if selected_option == question[6]:
            score += 1
    cursor.execute('''
        INSERT INTO scores (name, score) VALUES (?, ?)
    ''', (name, score))
    conn.commit()
    conn.close()
    highest_score, highest_scorer = get_highest_score()
    return render_template('results.html', score=score, total=len(questions), name=name, highest_score=highest_score, highest_scorer=highest_scorer)

def get_highest_score():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, score FROM scores ORDER BY score DESC, id ASC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[1], row[0]
    return None, None

if __name__ == '__main__':
    init_db()
    # Sadece ilk çalıştırmada CSV'den soruları içeri aktarmak için bu satırı kullanın:
    # import_questions_from_csv('questions.csv')
    app.run(debug=True)
