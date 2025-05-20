CREATE DATABASE SafeCircle
USE SafeCircle

CREATE TABLE Usuario (
	id_user INT PRIMARY KEY IDENTITY,
	nome VARCHAR(50) NOT NULL
	email VARCHAR(50) NOT NULL,
	senha VARCHAR(50) NOT NULL,
	dat_nac DATE NOT NULL,
	telefone VARCHAR(11) UNIQUE NOT NULL,
	cpf VARCHAR(11) UNIQUE NOT NULL,
	rg VARCHAR(14) UNIQUE NOT NULL,
	ind_front VARBINARY(MAX), -- foto da indentidade 
	ind_back VARBINARY(MAX)  -- foto do outro lado da indentidade
);

CREATE TABLE Ocorrencia (
	id_ocorrencia INT PRIMARY KEY IDENTITY,
	data_inicio DATETIME NOT NULL,
	data_conclusao DATETIME NOT NULL,
	descricao VARCHAR(80),
	estagio VARCHAR(50) NOT NULL,
	id_user INT FOREIGN KEY REFERENCES Usuario(id_user)
);

