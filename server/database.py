import sqlite3
from models import Paciente, Medico, Consulta

class DataBase:
    """
    Classe responsável pela interação com o banco de dados SQLite.
    
    Gerencia a conexão com o banco, criação de tabelas e todas as operações CRUD
    (Create, Read, Update, Delete) para pacientes, médicos e consultas.
    
    Attributes:
        db_name (str): Nome do arquivo do banco de dados SQLite.
    """
    
    def __init__(self, nome_db="clinica.db"):
        """
        Inicializa o banco de dados e cria as tabelas se não existirem.
        
        Args:
            nome_db (str, opcional): Nome do arquivo do banco de dados. Padrão: "clinica.db".
        """
        self.nome_db = nome_db
        self._criar_tabelas()
    
    def _conectar(self):
        """
        Estabelece uma conexão com o banco de dados SQLite.
        
        Returns:
            sqlite3.Connection: Objeto de conexão com o banco de dados.
        """
        conn = sqlite3.connect(self.nome_db)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _criar_tabelas(self):
        """
        Cria as tabelas necessárias no banco de dados se não existirem.
        
        Cria três tabelas:
        - pacientes: Para armazenar informações dos pacientes
        - medicos: Para armazenar informações dos médicos
        - consultas: Para armazenar informações das consultas
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        # Tabela de Pacientes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            data_nascimento TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            endereco TEXT
        )
        ''')
        
        # Tabela de Médicos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crm TEXT UNIQUE NOT NULL,
            especializacao TEXT NOT NULL,
            telefone TEXT,
            email TEXT
        )
        ''')
        
        # Tabela de Consultas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medico_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            status TEXT NOT NULL,
            observacoes TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
            FOREIGN KEY (medico_id) REFERENCES medicos (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # Métodos para Pacientes
    def obter_todos_pacientes(self):
        """
        Obtém todos os pacientes cadastrados no banco de dados.
        
        Returns:
            list: Lista de objetos Paciente.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pacientes")
        rows = cursor.fetchall()
        
        pacientes = []
        for row in rows:
            paciente = Paciente(
                id=row['id'],
                nome=row['nome'],
                cpf=row['cpf'],
                data_nascimento=row['data_nascimento'],
                telefone=row['telefone'],
                email=row['email'],
                endereco=row['endereco']
            )
            pacientes.append(paciente)
        
        conn.close()
        return pacientes
    
    def obter_paciente(self, paciente_id):
        """
        Obtém um paciente específico pelo seu ID.
        
        Args:
            paciente_id (int): ID do paciente a ser obtido.
            
        Returns:
            Paciente: Objeto Paciente se encontrado, None caso contrário.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        
        if row:
            paciente = Paciente(
                id=row['id'],
                nome=row['nome'],
                cpf=row['cpf'],
                data_nascimento=row['data_nascimento'],
                telefone=row['telefone'],
                email=row['email'],
                endereco=row['endereco']
            )
            conn.close()
            return paciente
        
        conn.close()
        return None
    
    def adicionar_paciente(self, paciente):
        """
        Adiciona um novo paciente ao banco de dados.
        
        Args:
            paciente (Paciente): Objeto Paciente a ser adicionado.
            
        Returns:
            Paciente: Objeto Paciente com ID atualizado.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, email, endereco) VALUES (?, ?, ?, ?, ?, ?)",
            (paciente.nome, paciente.cpf, paciente.data_nascimento, paciente.telefone, paciente.email, paciente.endereco)
        )
        
        paciente.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return paciente
    
    def atualizar_paciente(self, paciente):
        """
        Atualiza os dados de um paciente existente.
        
        Args:
            paciente (Paciente): Objeto Paciente com os dados atualizados.
            
        Returns:
            Paciente: Objeto Paciente atualizado.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE pacientes SET nome = ?, cpf = ?, data_nascimento = ?, telefone = ?, email = ?, endereco = ? WHERE id = ?",
            (paciente.nome, paciente.cpf, paciente.data_nascimento, paciente.telefone, paciente.email, paciente.endereco, paciente.id)
        )
        
        conn.commit()
        conn.close()
        
        return paciente
    
    def remover_paciente(self, paciente_id):
        """
        Remove um paciente do banco de dados.
        
        Args:
            paciente_id (int): ID do paciente a ser removido.
            
        Returns:
            bool: True se o paciente foi removido, False caso contrário.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        
        removido = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return removido
    
    # Métodos para Médicos
    def obter_todos_medicos(self):
        """
        Obtém todos os médicos cadastrados no banco de dados.
        
        Returns:
            list: Lista de objetos Medico.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM medicos")
        rows = cursor.fetchall()
        
        medicos = []
        for row in rows:
            medico = Medico(
                id=row['id'],
                nome=row['nome'],
                crm=row['crm'],
                especializacao=row['especializacao'],
                telefone=row['telefone'],
                email=row['email']
            )
            medicos.append(medico)
        
        conn.close()
        return medicos
    
    def obter_medico(self, medico_id):
        """
        Obtém um médico específico pelo seu ID.
        
        Args:
            medico_id (int): ID do médico a ser obtido.
            
        Returns:
            Medico: Objeto Medico se encontrado, None caso contrário.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM medicos WHERE id = ?", (medico_id,))
        row = cursor.fetchone()
        
        if row:
            medico = Medico(
                id=row['id'],
                nome=row['nome'],
                crm=row['crm'],
                especializacao=row['especializacao'],
                telefone=row['telefone'],
                email=row['email']
            )
            conn.close()
            return medico
        
        conn.close()
        return None
    
    def adicionar_medico(self, medico):
        """
        Adiciona um novo médico ao banco de dados.
        
        Args:
            medico (Medico): Objeto Medico a ser adicionado.
            
        Returns:
            Medico: Objeto Medico com ID atualizado.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO medicos (nome, crm, especializacao, telefone, email) VALUES (?, ?, ?, ?, ?)",
            (medico.nome, medico.crm, medico.especializacao, medico.telefone, medico.email)
        )
        
        medico.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return medico
    
    # Métodos para Consultas
    def obter_todas_consultas(self):
        """
        Obtém todas as consultas cadastradas no banco de dados.
        
        Inclui o nome do paciente e do médico para cada consulta.
        
        Returns:
            list: Lista de objetos Consulta.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, p.nome as nome_paciente, m.nome as nome_medico 
            FROM consultas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN medicos m ON c.medico_id = m.id
        """)
        rows = cursor.fetchall()
        
        consultas = []
        for row in rows:
            consulta = Consulta(
                id=row['id'],
                paciente_id=row['paciente_id'],
                medico_id=row['medico_id'],
                data=row['data'],
                hora=row['hora'],
                status=row['status'],
                observacoes=row['observacoes'],
                nome_paciente=row['nome_paciente'],
                nome_medico=row['nome_medico']
            )
            consultas.append(consulta)
        
        conn.close()
        return consultas
    
    def obter_consulta(self, consulta_id):
        """
        Obtém uma consulta específica pelo seu ID.
        
        Inclui o nome do paciente e do médico.
        
        Args:
            consulta_id (int): ID da consulta a ser obtida.
            
        Returns:
            Consulta: Objeto Consulta se encontrado, None caso contrário.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, p.nome as nome_paciente, m.nome as nome_medico 
            FROM consultas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN medicos m ON c.medico_id = m.id
            WHERE c.id = ?
        """, (consulta_id,))
        row = cursor.fetchone()
        
        if row:
            consulta = Consulta(
                id=row['id'],
                paciente_id=row['paciente_id'],
                medico_id=row['medico_id'],
                data=row['data'],
                hora=row['hora'],
                status=row['status'],
                observacoes=row['observacoes'],
                nome_paciente=row['nome_paciente'],
                nome_medico=row['nome_medico']
            )
            conn.close()
            return consulta
        
        conn.close()
        return None
    
    def adicionar_consulta(self, consulta):
        """
        Adiciona uma nova consulta ao banco de dados.
        
        Args:
            consulta (Consulta): Objeto Consulta a ser adicionado.
            
        Returns:
            Consulta: Objeto Consulta com ID atualizado.
        """
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO consultas (paciente_id, medico_id, data, hora, status, observacoes) VALUES (?, ?, ?, ?, ?, ?)",
            (consulta.paciente_id, consulta.medico_id, consulta.data, consulta.hora, consulta.status, consulta.observacoes)
        )
        
        consulta.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return consulta