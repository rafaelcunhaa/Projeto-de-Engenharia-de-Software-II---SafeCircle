from flask import Flask, tender_tamplete, request, redirect
import sqlite3
import os


app = Flask(__name__)
DB_PATH = "safecircle.db"

def criar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario(
        id user INTEGER PRIMARY KEY AUTOINCREMENT
        nome TEXT NOT NULL
        email TEXT UNIQUE NOT NULL
        senha TEXT NOT NULL
        dat_nac DATE NOT NULL
        telefone TEXT UNIQUE NOT NULL
        cpf TEXT UNIQUE NOT NULL
        rg TEXT UNIQUE NOT NULL                                                                                          
        ind_front BLOB                           
        ind_back BLOB               
    );        
    """)
    conn.commit()

@app.route("/")
def index():
    return render_template("cadastro.html")

@app.route("/cadastrar", methods["POST"])
def cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]
    nascimento = request.form["nascimento"]
    telefone = request.form["telefone"]
    cpf = request.form["cpf"]
    rg = request.form["rg"]

    ind_front = request.files["ind_front"].read()
    ind_back = request.files["ind_back"].read()

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
    except sqlite3.IntegrityErrora as e:
        return f"Erro: {str(e)}"
    
if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
