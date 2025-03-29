# Sistema de Gerenciamento de Clínica Médica

Este é um sistema de gerenciamento para clínicas médicas que permite cadastrar e gerenciar pacientes, médicos e consultas. O sistema é composto por um servidor central e um cliente desktop.

## Estrutura do Projeto

```
📂 clinica_system/
├── 📂 server/ 
│   ├── server.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│
├── 📂 client/
│   ├── app.py
│   ├── requests_handler.py
│   ├── config.py
│
└── README.md
```

## Requisitos

### Servidor
- Python 3.6+
- Flask
- flask-cors
- SQLAlchemy

### Cliente
- Python 3.6+
- tkinter
- tkcalendar
- requests

## Instalação

### Servidor

1. Navegue até a pasta do servidor:
```
cd clinica_system/server
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Execute o servidor:
```
python server.py
```

O servidor será iniciado em `http://localhost:5000`.

### Cliente

1. Navegue até a pasta do cliente:
```
cd clinica_system/client
```

2. Instale as dependências:
```
pip install tkinter tkcalendar requests
```

3. Execute o aplicativo:
```
python app.py
```

## Configuração

Se o servidor estiver rodando em um host ou porta diferente, edite o arquivo `config.py` no diretório do cliente.

## Funcionalidades

### Gerenciamento de Pacientes
- Cadastrar pacientes
- Editar informações de pacientes
- Visualizar lista de pacientes
- Excluir pacientes

### Gerenciamento de Médicos
- Cadastrar médicos
- Editar informações de médicos
- Visualizar lista de médicos
- Excluir médicos

### Agendamento de Consultas
- Agendar novas consultas
- Editar consultas existentes
- Visualizar agenda de consultas
- Cancelar consultas

## Banco de Dados

O sistema utiliza SQLite como banco de dados para simplicidade. O arquivo do banco de dados será criado automaticamente na pasta do servidor como `clinica.db`.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou abrir issues com sugestões.