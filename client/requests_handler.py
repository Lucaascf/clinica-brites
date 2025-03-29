import requests
import json
from config import SERVER_URL

class ManipuladorRequisicoes:
    """
    Classe responsável por fazer requisições para o servidor.
    
    Gerencia todas as comunicações HTTP com o servidor da API,
    incluindo operações CRUD para pacientes, médicos e consultas.
    
    Attributes:
        base_url (str): URL base do servidor da API.
    """
    
    def __init__(self):
        """
        Inicializa o manipulador de requisições com a URL base do servidor.
        """
        self.base_url = SERVER_URL
    
    def _tratar_resposta(self, resposta):
        """
        Trata a resposta da requisição HTTP.
        
        Verifica o código de status da resposta e retorna os dados JSON
        ou levanta uma exceção com a mensagem de erro apropriada.
        
        Args:
            resposta (Response): Objeto de resposta da requisição HTTP.
            
        Returns:
            dict: Dados JSON da resposta se bem-sucedida.
            
        Raises:
            Exception: Se a requisição falhar, com a mensagem de erro.
        """
        if resposta.status_code >= 200 and resposta.status_code < 300:
            return resposta.json()
        else:
            try:
                dados_erro = resposta.json()
                mensagem_erro = dados_erro.get('erro', 'Erro desconhecido')
            except:
                mensagem_erro = f"Erro na requisição: {resposta.status_code}"
            
            raise Exception(mensagem_erro)
    
    # PACIENTES
    def obter_pacientes(self):
        """
        Obtém a lista de todos os pacientes cadastrados.
        
        Returns:
            list: Lista de pacientes em formato de dicionário.
            
        Raises:
            Exception: Se ocorrer um erro na requisição.
        """
        resposta = requests.get(f"{self.base_url}/pacientes")
        return self._tratar_resposta(resposta)
    
    def obter_paciente(self, paciente_id):
        """
        Obtém os detalhes de um paciente específico.
        
        Args:
            paciente_id (int): ID do paciente a ser obtido.
            
        Returns:
            dict: Dados do paciente em formato de dicionário.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se o paciente não for encontrado.
        """
        resposta = requests.get(f"{self.base_url}/pacientes/{paciente_id}")
        return self._tratar_resposta(resposta)
    
    def adicionar_paciente(self, dados_paciente):
        """
        Adiciona um novo paciente ao sistema.
        
        Args:
            dados_paciente (dict): Dicionário com os dados do paciente a ser adicionado.
            
        Returns:
            dict: Dados do paciente adicionado, incluindo o ID gerado.
            
        Raises:
            Exception: Se ocorrer um erro na requisição.
        """
        resposta = requests.post(
            f"{self.base_url}/pacientes",
            json=dados_paciente,
            headers={"Content-Type": "application/json"}
        )
        return self._tratar_resposta(resposta)
    
    def atualizar_paciente(self, dados_paciente):
        """
        Atualiza os dados de um paciente existente.
        
        Args:
            dados_paciente (dict): Dicionário com os dados atualizados do paciente,
                                   deve incluir a chave 'id'.
            
        Returns:
            dict: Dados atualizados do paciente.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se o paciente não for encontrado.
        """
        paciente_id = dados_paciente.pop('id')
        resposta = requests.put(
            f"{self.base_url}/pacientes/{paciente_id}",
            json=dados_paciente,
            headers={"Content-Type": "application/json"}
        )
        return self._tratar_resposta(resposta)
    
    def remover_paciente(self, paciente_id):
        """
        Remove um paciente do sistema.
        
        Args:
            paciente_id (int): ID do paciente a ser removido.
            
        Returns:
            dict: Mensagem de confirmação.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se o paciente não for encontrado.
        """
        resposta = requests.delete(f"{self.base_url}/pacientes/{paciente_id}")
        return self._tratar_resposta(resposta)
    
    # MÉDICOS
    def obter_medicos(self):
        """
        Obtém a lista de todos os médicos cadastrados.
        
        Returns:
            list: Lista de médicos em formato de dicionário.
            
        Raises:
            Exception: Se ocorrer um erro na requisição.
        """
        resposta = requests.get(f"{self.base_url}/medicos")
        return self._tratar_resposta(resposta)
    
    def obter_medico(self, medico_id):
        """
        Obtém os detalhes de um médico específico.
        
        Args:
            medico_id (int): ID do médico a ser obtido.
            
        Returns:
            dict: Dados do médico em formato de dicionário.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se o médico não for encontrado.
        """
        resposta = requests.get(f"{self.base_url}/medicos/{medico_id}")
        return self._tratar_resposta(resposta)
    
    def adicionar_medico(self, dados_medico):
        """
        Adiciona um novo médico ao sistema.
        
        Args:
            dados_medico (dict): Dicionário com os dados do médico a ser adicionado.
            
        Returns:
            dict: Dados do médico adicionado, incluindo o ID gerado.
            
        Raises:
            Exception: Se ocorrer um erro na requisição.
        """
        resposta = requests.post(
            f"{self.base_url}/medicos",
            json=dados_medico,
            headers={"Content-Type": "application/json"}
        )
        return self._tratar_resposta(resposta)
    
    def atualizar_medico(self, dados_medico):
        """
        Atualiza os dados de um médico existente.
        
        Args:
            dados_medico (dict): Dicionário com os dados atualizados do médico,
                                 deve incluir a chave 'id'.
            
        Returns:
            dict: Dados atualizados do médico.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se o médico não for encontrado.
        """
        medico_id = dados_medico.pop('id')
        resposta = requests.put(
            f"{self.base_url}/medicos/{medico_id}",
            json=dados_medico,
            headers={"Content-Type": "application/json"}
        )
        return self._tratar_resposta(resposta)
    
    def remover_medico(self, medico_id):
        """
        Remove um médico do sistema.
        
        Args:
            medico_id (int): ID do médico a ser removido.
            
        Returns:
            dict: Mensagem de confirmação.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se o médico não for encontrado.
        """
        resposta = requests.delete(f"{self.base_url}/medicos/{medico_id}")
        return self._tratar_resposta(resposta)
    
    # CONSULTAS
    def obter_consultas(self):
        """
        Obtém a lista de todas as consultas cadastradas.
        
        Returns:
            list: Lista de consultas em formato de dicionário.
            
        Raises:
            Exception: Se ocorrer um erro na requisição.
        """
        resposta = requests.get(f"{self.base_url}/consultas")
        return self._tratar_resposta(resposta)
    
    def obter_consulta(self, consulta_id):
        """
        Obtém os detalhes de uma consulta específica.
        
        Args:
            consulta_id (int): ID da consulta a ser obtida.
            
        Returns:
            dict: Dados da consulta em formato de dicionário.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se a consulta não for encontrada.
        """
        resposta = requests.get(f"{self.base_url}/consultas/{consulta_id}")
        return self._tratar_resposta(resposta)
    
    def adicionar_consulta(self, dados_consulta):
        """
        Adiciona uma nova consulta ao sistema.
        
        Args:
            dados_consulta (dict): Dicionário com os dados da consulta a ser adicionada.
            
        Returns:
            dict: Dados da consulta adicionada, incluindo o ID gerado.
            
        Raises:
            Exception: Se ocorrer um erro na requisição.
        """
        resposta = requests.post(
            f"{self.base_url}/consultas",
            json=dados_consulta,
            headers={"Content-Type": "application/json"}
        )
        return self._tratar_resposta(resposta)
    
    def atualizar_consulta(self, dados_consulta):
        """
        Atualiza os dados de uma consulta existente.
        
        Args:
            dados_consulta (dict): Dicionário com os dados atualizados da consulta,
                                   deve incluir a chave 'id'.
            
        Returns:
            dict: Dados atualizados da consulta.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se a consulta não for encontrada.
        """
        consulta_id = dados_consulta.pop('id')
        resposta = requests.put(
            f"{self.base_url}/consultas/{consulta_id}",
            json=dados_consulta,
            headers={"Content-Type": "application/json"}
        )
        return self._tratar_resposta(resposta)
    
    def remover_consulta(self, consulta_id):
        """
        Remove uma consulta do sistema.
        
        Args:
            consulta_id (int): ID da consulta a ser removida.
            
        Returns:
            dict: Mensagem de confirmação.
            
        Raises:
            Exception: Se ocorrer um erro na requisição ou se a consulta não for encontrada.
        """
        resposta = requests.delete(f"{self.base_url}/consultas/{consulta_id}")
        return self._tratar_resposta(resposta)