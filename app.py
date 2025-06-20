from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "seu_segredo"
DB_PATH = "safecircle.db"

def criar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario(
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL CHECK(LENGTH(nome) <= 50),
            email TEXT UNIQUE NOT NULL CHECK(LENGTH(email) <= 50),
            senha TEXT NOT NULL CHECK(LENGTH(senha) <= 50),
            dat_nac DATE NOT NULL,
            telefone TEXT UNIQUE NOT NULL CHECK(LENGTH(telefone) = 11),
            cpf TEXT UNIQUE NOT NULL CHECK(LENGTH(cpf) = 11),
            rg TEXT UNIQUE NOT NULL CHECK(LENGTH(rg) <= 14),
            ind_front BLOB,
            ind_back BLOB
        );        
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ocorrencia(
            id_ocorrencia INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inicio DATETIME NOT NULL,
            data_conclusao DATETIME,
            descricao TEXT CHECK(LENGTH(descricao) <= 80),
            estagio TEXT NOT NULL CHECK(LENGTH(estagio) <= 50),
            titulo TEXT,
            local TEXT,
            id_user INTEGER,
            FOREIGN KEY (id_user) REFERENCES Usuario(id_user)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Adimin(
            id_adimin INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL CHECK(LENGTH(email) <= 50),
            senha TEXT NOT NULL CHECK(LENGTH(senha) <= 50)
        );        
        """)
        conn.commit()

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["emailUsuario"]
        senha = request.form["senhaUsuario"]

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM Usuario WHERE email = ? AND senha = ?", (email, senha))
            resultado = cursor.fetchone()

            if resultado:
                session["usuario"] = resultado[0]
                return redirect("/telaPrincipal")
            else:
                flash("Email ou senha inválidos!", "erro")
                return redirect("/login")

    return render_template("login.html")

@app.route('/cadastro', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]
    nascimento = request.form["nascimento"]
    telefone = request.form["telefone"]
    cpf = request.form["cpf"]
    rg = request.form["rg"]

    ind_front = request.files["ind_front"].read() if "ind_front" in request.files else None
    ind_back = request.files["ind_back"].read() if "ind_back" in request.files else None

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Usuario (
                    nome, email, senha, dat_nac, telefone, cpf, rg, ind_front, ind_back
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)               
            """, (nome, email, senha, nascimento, telefone, cpf, rg, ind_front, ind_back))
            conn.commit()
        return redirect("/login")
    except sqlite3.IntegrityError as e:
        return f"Erro: {str(e)}"

@app.route("/telaPrincipal")
def tela_principal():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("telaPrincipal.html")

@app.route("/configuracoes")
def configuracoes():
    return render_template("configuracoes.html")

@app.route("/usuario")
def usuario():
    return render_template("usuario.html")


@app.route("/ocorrencia" , methods=["GET", "POST"])
def ocorrencia():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        descricao_completa = request.form["descricao"]
        titulo = request.form["ocorrencia"]
        local = request.form["localizacao"]
        estagio = "Em andamento"
        data_inicio = datetime.now()
        data_conclusao = datetime.now()

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id_user FROM Usuario WHERE nome = ?",
                    (session["usuario"],)
                )
                resultado = cursor.fetchone()
                if resultado:
                    id_user = resultado[0]
                else:
                    return "Usuário não encontrado."

                cursor.execute("""
                    INSERT INTO Ocorrencia (data_inicio, data_conclusao, descricao, estagio, titulo, local, id_user)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (data_inicio, data_conclusao, descricao_completa, estagio, titulo, local, id_user))
                conn.commit()

            return redirect("/telaPrincipal")
        except Exception as e:
            return f"Erro ao registrar ocorrência: {str(e)}"

    return render_template("ocorrencia.html")

if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
