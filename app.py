from flask import Flask, render_template, request, redirect, send_from_directory
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def criar_banco():
    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        tipo TEXT,
        data TEXT,
        horario TEXT,
        local TEXT,
        descricao TEXT,
        imagem TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        comentario TEXT
    )
    """)

    conexao.commit()
    conexao.close()

criar_banco()

@app.route('/')
def index():

    busca = request.args.get('busca')

    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    if busca:

       cursor.execute("""
        SELECT * FROM eventos
        WHERE nome LIKE ?
        OR tipo LIKE ?
        """, (
                '%' + busca + '%',
                '%' + busca + '%'
))

    else:

        cursor.execute("SELECT * FROM eventos")

    eventos = cursor.fetchall()

    conexao.close()

    return render_template('index.html', eventos=eventos)

@app.route('/adicionar')
def adicionar():
    return render_template('adicionar.html')

@app.route('/salvar', methods=['POST'])
def salvar():

    nome = request.form['nome']
    tipo = request.form['tipo']
    data = request.form['data']
    horario = request.form['horario']
    local = request.form['local']
    descricao = request.form['descricao']

    imagem = request.files['imagem']

    if imagem.filename != "":

        nome_imagem = imagem.filename

        imagem.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                nome_imagem
            )
        )

    else:

        nome_imagem = "sem_imagem.png"

    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO eventos
    (nome,tipo,data,horario,local,descricao,imagem)
    VALUES (?,?,?,?,?,?,?)
    """,
    (
        nome,
        tipo,
        data,
        horario,
        local,
        descricao,
        nome_imagem
    ))

    conexao.commit()
    conexao.close()

    return redirect('/')

@app.route('/evento/<int:id>')
def detalhes(id):

    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM eventos WHERE id=?", (id,))
    evento = cursor.fetchone()

    conexao.close()

    return render_template('detalhes.html', evento=evento)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/enviar_feedback', methods=['POST'])
def enviar_feedback():

    nome = request.form['nome']
    comentario = request.form['comentario']

    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO feedback(nome,comentario)
    VALUES (?,?)
    """,(nome,comentario))

    conexao.commit()
    conexao.close()

    return redirect('/')


@app.route('/excluir/<int:id>')
def excluir(id):

    
    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM eventos WHERE id=?",
        (id,)
    )

    conexao.commit()
    conexao.close()

    return redirect('/')

@app.route('/comentarios')
def comentarios():

    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM feedback"
    )

    comentarios = cursor.fetchall()

    conexao.close()

    return render_template(
        'comentarios.html',
        comentarios=comentarios
    )
@app.route('/uploads/<filename>')
def upload(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )

if __name__ == '__main__':
    app.run(debug=True)