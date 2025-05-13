import pyodbc
import os
from datetime import datetime


"""

Na parte de UID e PWD
Use suas credenciais 
Para executar 

"""

def conectar_bd():
    dados_conexao = (
        "Driver={SQL Server};"
        "Server=RAFAEL;"
        "Database=SafeCircle;"
        "UID=sa;"
        "PWD=291690Rc@;"
    )
    return pyodbc.connect(dados_conexao)


def ler_imagem(nome_arquivo):
    caminho_base = os.path.dirname(os.path.abspath(__file__))
    caminho_foto = os.path.join(caminho_base, nome_arquivo)

    if not os.path.exists(caminho_foto):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_foto}")

    with open(caminho_foto, "rb") as f:
        return f.read()


def inserir_usuario(cursor, dados_usuario):
    comando = """
    INSERT INTO Usuario (
        nome, email, senha, dat_nac, telefone, cpf, rg, ind_front, ind_back
    )
    OUTPUT INSERTED.id_user
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.execute(comando, dados_usuario)
        resultado = cursor.fetchone()
        if resultado and resultado[0] is not None:
            return int(resultado[0])
        else:
            raise Exception("Falha ao recuperar o ID do usuário inserido.")
    except pyodbc.IntegrityError as e:
        if "UNIQUE" in str(e):
            print("Erro: Já existe um usuário com algum dos dados únicos (cpf, rg, telefone). Buscando ID existente...")
            cursor.execute("SELECT id_user FROM Usuario WHERE rg = ?", (dados_usuario[6],))
            resultado = cursor.fetchone()
            if resultado:
                return int(resultado[0])
            else:
                raise Exception("Usuário existente, mas ID não pôde ser recuperado.")
        else:
            raise


def inserir_ocorrencia(cursor, dados_ocorrencia):
    comando = """
    INSERT INTO Ocorrencia (
        data_inicio, data_conclusao, descricao, estagio, id_user
    ) VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(comando, dados_ocorrencia)


# Programa principal
try:
    conexao = conectar_bd()
    cursor = conexao.cursor()
    print("Conexão Bem Sucedida")

    # Inserção de usuário
    ind_front = ler_imagem("ind_front.jpg")
    ind_back = ler_imagem("ind_back.jpg")
    dados_usuario = (
        "João Silva",
        "joa.si32a@email.com",
        "senh13",
        "1990-05-20",
        "47989932888",
        "12845632901",
        "MG1283567",
        ind_front,
        ind_back
    )
    id_user = inserir_usuario(cursor, dados_usuario)
    print(f"ID do usuário a ser usado: {id_user}")

    # Inserção de ocorrência
    dados_ocorrencia = (
        datetime(2024, 5, 13, 14, 0, 0),
        datetime(2024, 5, 13, 16, 30, 0),
        "Vazamento no corredor principal",
        "Em andamento",
        id_user
    )
    inserir_ocorrencia(cursor, dados_ocorrencia)
    print("Ocorrência inserida com sucesso!")

    conexao.commit()

except Exception as e:
    print("Erro:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conexao' in locals():
        conexao.close()
