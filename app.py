from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "seu_segredo"
DB_PATH = "safecircle.db"

##########################################
########### BANCO DE DADOS ###############
##########################################



def criar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario(
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL CHECK(LENGTH(nome) <= 50),
            email TEXT UNIQUE NOT NULL CHECK(LENGTH(email) <= 50),
            senha TEXT NOT NULL CHECK(LENGTH(senha) <= 255),
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
            senha TEXT NOT NULL CHECK(LENGTH(senha) <= 255)
        );        
        """)
        conn.commit()



##########################################
############### Funções ##################
##########################################




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["emailUsuario"]
        senha = request.form["senhaUsuario"]

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, senha FROM Usuario WHERE email = ?", (email,))
            resultado = cursor.fetchone()

            if resultado and check_password_hash(resultado[1], senha):
                session["usuario"] = resultado[0]
                return redirect("/telaPrincipal")
            else:
                flash("Email ou senha inválidos!", "erro")
                return redirect("/login")

    return render_template("login.html")





@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = generate_password_hash(request.form["senha"])
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





@app.route("/usuario", methods=["GET", "POST"])
def usuario():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
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
                    UPDATE Usuario SET nome=?, email=?, senha=?, dat_nac=?, telefone=?, cpf=?, rg=?, ind_front=?, ind_back=?
                    WHERE nome=?
                """, (nome, email, senha, nascimento, telefone, cpf, rg, ind_front, ind_back, session["usuario"]))
                conn.commit()
            session["usuario"] = nome
        except sqlite3.IntegrityError as e:
            return f"Erro ao atualizar: {str(e)}"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome, email, senha, dat_nac, telefone FROM Usuario WHERE nome = ?", (session["usuario"],))
        dados = cursor.fetchone()

    if dados:
        return render_template("usuario.html", usuario=dados)
    else:
        return "Usuário não encontrado."





@app.route("/editar", methods=["GET", "POST"])
def editar():
    if "usuario" not in session:
        return redirect("/login")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            nome = request.form["nome"]
            email = request.form["email"]
            telefone = request.form["telefone"]
            nascimento = request.form["nascimento"]

            cursor.execute("""
                UPDATE Usuario
                SET nome = ?, email = ?, telefone = ?, dat_nac = ?
                WHERE nome = ?
            """, (nome, email, telefone, nascimento, session["usuario"]))
            conn.commit()
            session["usuario"] = nome
            return redirect("/usuario")

        cursor.execute("SELECT nome, email, senha, dat_nac, telefone FROM Usuario WHERE nome = ?", (session["usuario"],))
        usuario = cursor.fetchone()
        if usuario:
            return render_template("editar_perfil.html", usuario=usuario)
        else:
            return "Usuário não encontrado."





@app.route("/alterar_senha", methods=["GET", "POST"])
def alterar_senha():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        senha_atual = request.form["senha_atual"]
        nova_senha = request.form["nova_senha"]
        confirmar_senha = request.form["confirmar_senha"]

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT senha FROM Usuario WHERE nome = ?", (session["usuario"],))
            resultado = cursor.fetchone()
            if not resultado:
                return "Usuário não encontrado."

            senha_no_banco = resultado[0]

            if not check_password_hash(senha_no_banco, senha_atual):
                return "Senha atual incorreta."

            if nova_senha != confirmar_senha:
                return "As novas senhas não coincidem."

            nova_senha_hash = generate_password_hash(nova_senha)
            cursor.execute("UPDATE Usuario SET senha = ? WHERE nome = ?", (nova_senha_hash, session["usuario"]))
            conn.commit()
            return redirect("/usuario")

    return render_template("alterar_senha.html")




@app.route("/historicoDeOcorrencias")
def historico_de_ocorrencias():
    if "usuario" not in session:
        return redirect("/login")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Recupera o ID do usuário atual pela sessão
        cursor.execute("SELECT id_user FROM Usuario WHERE nome = ?", (session["usuario"],))
        resultado = cursor.fetchone()

        if not resultado:
            return "Usuário não encontrado."

        id_user = resultado[0]

        # Busca todas as ocorrências desse usuário
        cursor.execute("""
            SELECT data_inicio, data_conclusao, titulo, descricao, estagio, local
            FROM Ocorrencia
            WHERE id_user = ?
            ORDER BY data_inicio DESC
        """, (id_user,))

        ocorrencias = cursor.fetchall()

    return render_template("historicoDeOcorrencias.html", ocorrencias=ocorrencias)



##########################################
################# Rotas ##################
##########################################

@app.route("/telaPrincipal")
def tela_principal():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("telaPrincipal.html")

@app.route("/configuracoes")
def configuracoes():
    return render_template("configuracoes.html")

@app.route("/usuario_simples")
def usuario_simples():
    return render_template("usuario.html")

@app.route('/cadastro', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    return render_template("login.html")

if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
