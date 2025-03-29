class Paciente:
    """
    Classe que representa um paciente no sistema.
    
    Armazena as informações pessoais e de contato do paciente.
    
    Attributes:
        id (int): Identificador único do paciente no sistema.
        nome (str): Nome completo do paciente.
        cpf (str): CPF do paciente (documento de identificação).
        data_nascimento (str): Data de nascimento do paciente.
        telefone (str, opcional): Número de telefone para contato.
        email (str, opcional): Endereço de e-mail do paciente.
        endereco (str, opcional): Endereço residencial do paciente.
    """
    
    def __init__(self, nome, cpf, data_nascimento, telefone=None, email=None, endereco=None, id=None):
        """
        Inicializa um novo objeto Paciente.
        
        Args:
            nome (str): Nome completo do paciente.
            cpf (str): CPF do paciente.
            data_nascimento (str): Data de nascimento do paciente.
            telefone (str, opcional): Número de telefone para contato.
            email (str, opcional): Endereço de e-mail do paciente.
            endereco (str, opcional): Endereço residencial do paciente.
            id (int, opcional): Identificador único, geralmente atribuído pelo banco de dados.
        """
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.telefone = telefone
        self.email = email
        self.endereco = endereco
    
    def para_dict(self):
        """
        Converte o objeto Paciente para um dicionário.
        
        Returns:
            dict: Representação do paciente em formato de dicionário.
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco
        }


class Medico:
    """
    Classe que representa um médico no sistema.
    
    Armazena as informações profissionais e de contato do médico.
    
    Attributes:
        id (int): Identificador único do médico no sistema.
        nome (str): Nome completo do médico.
        crm (str): Número do CRM (registro profissional).
        especializacao (str): Área de especialização médica.
        telefone (str, opcional): Número de telefone para contato.
        email (str, opcional): Endereço de e-mail do médico.
    """
    
    def __init__(self, nome, crm, especializacao, telefone=None, email=None, id=None):
        """
        Inicializa um novo objeto Medico.
        
        Args:
            nome (str): Nome completo do médico.
            crm (str): Número do CRM (registro profissional).
            especializacao (str): Área de especialização médica.
            telefone (str, opcional): Número de telefone para contato.
            email (str, opcional): Endereço de e-mail do médico.
            id (int, opcional): Identificador único, geralmente atribuído pelo banco de dados.
        """
        self.id = id
        self.nome = nome
        self.crm = crm
        self.especializacao = especializacao
        self.telefone = telefone
        self.email = email
    
    def para_dict(self):
        """
        Converte o objeto Medico para um dicionário.
        
        Returns:
            dict: Representação do médico em formato de dicionário.
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'crm': self.crm,
            'especializacao': self.especializacao,
            'telefone': self.telefone,
            'email': self.email
        }


class Consulta:
    """
    Classe que representa uma consulta médica no sistema.
    
    Armazena as informações de agendamento, status e observações da consulta.
    
    Attributes:
        id (int): Identificador único da consulta no sistema.
        paciente_id (int): ID do paciente associado à consulta.
        medico_id (int): ID do médico responsável pela consulta.
        data (str): Data agendada para a consulta.
        hora (str): Horário agendado para a consulta.
        status (str): Status atual da consulta (ex: "Agendada", "Concluída", "Cancelada").
        observacoes (str): Observações adicionais sobre a consulta.
        nome_paciente (str, opcional): Nome do paciente, não armazenado no banco.
        nome_medico (str, opcional): Nome do médico, não armazenado no banco.
    """
    
    def __init__(self, paciente_id, medico_id, data, hora, status="Agendada", observacoes="", id=None, nome_paciente=None, nome_medico=None):
        """
        Inicializa um novo objeto Consulta.
        
        Args:
            paciente_id (int): ID do paciente associado à consulta.
            medico_id (int): ID do médico responsável pela consulta.
            data (str): Data agendada para a consulta.
            hora (str): Horário agendado para a consulta.
            status (str, opcional): Status atual da consulta. Padrão: "Agendada".
            observacoes (str, opcional): Observações adicionais sobre a consulta.
            id (int, opcional): Identificador único, geralmente atribuído pelo banco de dados.
            nome_paciente (str, opcional): Nome do paciente (campo auxiliar para a interface).
            nome_medico (str, opcional): Nome do médico (campo auxiliar para a interface).
        """
        self.id = id
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.data = data
        self.hora = hora
        self.status = status
        self.observacoes = observacoes
        
        # Campos adicionais não armazenados no banco, mas úteis para a interface
        self.nome_paciente = nome_paciente
        self.nome_medico = nome_medico
    
    def para_dict(self):
        """
        Converte o objeto Consulta para um dicionário.
        
        Returns:
            dict: Representação da consulta em formato de dicionário.
        """
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'medico_id': self.medico_id,
            'data': self.data,
            'hora': self.hora,
            'status': self.status,
            'observacoes': self.observacoes,
            'nome_paciente': self.nome_paciente,
            'nome_medico': self.nome_medico
        }