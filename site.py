import sqlite3
from flask import Flask, render_template, request, redirect, flash, session, jsonify

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Para usar o flash

# Função para criar o banco de dados e as tabelas
def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        cpf TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        senha TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS propostas (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        andamento TEXT NOT NULL,
        parcela INTEGER NOT NULL,
        saldo_devedor REAL NOT NULL,
        banco TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota para a página de criação de usuário
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        senha = request.form['senha']

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (cpf, nome, senha) VALUES (?, ?, ?)", (cpf, nome, senha))
            conn.commit()
            conn.close()
            flash('Usuário criado com sucesso!')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('CPF já cadastrado!')

    return render_template('create_user.html')

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE cpf = ? AND senha = ?", (cpf, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['cpf'] = user[1]
            session['nome'] = user[2]
            session['is_admin'] = user[4] == 1
            flash('Login bem-sucedido!')

            if session['is_admin']:
                return redirect('/admin')
            return redirect('/dashboard')
        else:
            flash('Usuário não cadastrado!')

    return render_template('login.html')

# Rota para a página de administração
@app.route('/admin')
def admin_page():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, cpf, nome, is_admin FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT id, nome, andamento, parcela, saldo_devedor, banco FROM propostas")
    propostas = cursor.fetchall()

    conn.close()

    return render_template('admin.html', nome=session['nome'], users=users, propostas=propostas)

# Rota para editar proposta
@app.route('/edit_proposta/<int:proposta_id>', methods=['POST'])
def edit_proposta(proposta_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    data = request.get_json()
    nome = data['nome']
    andamento = data['andamento']
    parcela = data['parcela']
    saldo_devedor = data['saldo_devedor']
    banco = data['banco']

    cursor.execute(
        "UPDATE propostas SET nome=?, andamento=?, parcela=?, saldo_devedor=?, banco=? WHERE id=?",
        (nome, andamento, parcela, saldo_devedor, banco, proposta_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)

# Rota de logout
@app.route('/logout')
def logout():
    session.clear()  # Limpa a sessão
    flash('Você foi desconectado com sucesso!')
    return redirect('/login')

# Rota para o dashboard do usuário
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT p.*, u.cpf FROM propostas p JOIN users u ON p.user_id = u.id WHERE u.id = ?", (session['user_id'],))
    propostas = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', nome=session['nome'], cpf=session['cpf'], propostas=propostas)

# Rota para solicitar proposta
@app.route('/solicitar_proposta', methods=['POST'])
def solicitar_proposta():
    if 'user_id' not in session:
        return redirect('/login')

    tipo_proposta = request.form['tipo_proposta']
    andamento = "Solicitada"
    parcela = request.form['parcela']
    saldo_devedor = request.form['saldo_devedor']
    banco = request.form['banco']
    user_id = session['user_id']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO propostas (nome, andamento, parcela, saldo_devedor, banco, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (tipo_proposta, andamento, parcela, saldo_devedor, banco, user_id))
    conn.commit()
    conn.close()

    flash('Proposta solicitada com sucesso!')
    return redirect('/dashboard')

if __name__ == '__main__':
    create_db()  # Cria o banco de dados ao iniciar
    app.run(debug=True)
