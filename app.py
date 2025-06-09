from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "seu_segredo"  # Necessário para usar sessões
DB_PATH = "safecircle.db"

def criar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario(
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            dat_nac DATE NOT NULL,
            telefone TEXT UNIQUE NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            rg TEXT UNIQUE NOT NULL,                                                                                          
            ind_front BLOB,
            ind_back BLOB
        );        
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ocorrencia(
            id_ocorrencia INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inicio DATETIME NOT NULL,
            data_conclusao DATETIME NOT NULL,
            descricao TEXT,
            estagio TEXT NOT NULL,
            id_user INTEGER,
            FOREIGN KEY (id_user) REFERENCES Usuario(id_user)
        );
        """)
        conn.commit()

@app.route("/")
def index():
    return render_template("cadastro.html")

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
        return "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError as e:
        return f"Erro: {str(e)}"

@app.route("/ocorrencia", methods=["GET", "POST"])
def ocorrencia():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        descricao = request.form["descricao"]
        titulo = request.form["ocorrencia"]
        local = request.form["localizacao"]

        estagio = "Em andamento"
        data_inicio = datetime.now()
        data_conclusao = datetime.now()  # ou defina como None e atualize depois

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
                    INSERT INTO Ocorrencia (data_inicio, data_conclusao, descricao, estagio, id_user)
                    VALUES (?, ?, ?, ?, ?)
                """, (data_inicio, data_conclusao, f"{titulo} - {local}: {descricao}", estagio, id_user))
                conn.commit()

            return "Ocorrência registrada com sucesso!"

        except Exception as e:
            return f"Erro ao registrar ocorrência: {e}"

    return render_template("ocorrencia.html")

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
                return redirect("/ocorrencia")
            else:
                return "Email ou senha inválidos."

    return render_template("login.html")


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
