from flask import Flask, request, jsonify
from flask_cors import CORS
from database import DataBase
from models import Paciente, Medico, Consulta

app = Flask(__name__)
CORS(app)  # Permite requisições cross-origin

db = DataBase()

@app.route('/pacientes', methods=['GET'])
def obter_pacientes():
    """
    Obtém todos os pacientes cadastrados no sistema.
    
    Returns:
        list: Uma lista de pacientes convertidos para dicionário.
    """
    pacientes = db.obter_todos_pacientes()
    return jsonify([paciente.para_dict() for paciente in pacientes])

@app.route('/pacientes/<int:paciente_id>', methods=['GET'])
def obter_paciente(paciente_id):
    """
    Obtém um paciente específico pelo seu ID.
    
    Args:
        paciente_id (int): O ID do paciente a ser obtido.
        
    Returns:
        dict: Os dados do paciente se encontrado.
        tuple: Mensagem de erro e código 404 se não encontrado.
    """
    paciente = db.obter_paciente(paciente_id)
    if paciente:
        return jsonify(paciente.para_dict())
    return jsonify({"erro": "Paciente não encontrado"}), 404

@app.route('/pacientes', methods=['POST'])
def adicionar_paciente():
    """
    Adiciona um novo paciente ao sistema.
    
    Returns:
        tuple: Os dados do paciente adicionado e código 201 (Created).
    """
    dados = request.json
    paciente = Paciente(
        nome=dados.get('nome'),
        cpf=dados.get('cpf'),
        data_nascimento=dados.get('data_nascimento'),
        telefone=dados.get('telefone'),
        email=dados.get('email'),
        endereco=dados.get('endereco')
    )
    db.adicionar_paciente(paciente)
    return jsonify(paciente.para_dict()), 201

@app.route('/pacientes/<int:paciente_id>', methods=['PUT'])
def atualizar_paciente(paciente_id):
    """
    Atualiza os dados de um paciente existente.
    
    Args:
        paciente_id (int): O ID do paciente a ser atualizado.
        
    Returns:
        dict: Os dados atualizados do paciente se encontrado.
        tuple: Mensagem de erro e código 404 se não encontrado.
    """
    dados = request.json
    paciente = db.obter_paciente(paciente_id)
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404
        
    paciente.nome = dados.get('nome', paciente.nome)
    paciente.cpf = dados.get('cpf', paciente.cpf)
    paciente.data_nascimento = dados.get('data_nascimento', paciente.data_nascimento)
    paciente.telefone = dados.get('telefone', paciente.telefone)
    paciente.email = dados.get('email', paciente.email)
    paciente.endereco = dados.get('endereco', paciente.endereco)
    
    db.atualizar_paciente(paciente)
    return jsonify(paciente.para_dict())

@app.route('/pacientes/<int:paciente_id>', methods=['DELETE'])
def remover_paciente(paciente_id):
    """
    Remove um paciente do sistema pelo seu ID.
    
    Args:
        paciente_id (int): O ID do paciente a ser removido.
        
    Returns:
        dict: Mensagem de sucesso se removido.
        tuple: Mensagem de erro e código 404 se não encontrado.
    """
    resultado = db.remover_paciente(paciente_id)
    if resultado:
        return jsonify({"mensagem": "Paciente removido com sucesso"})
    return jsonify({"erro": "Paciente não encontrado"}), 404

# Rotas para médicos
@app.route('/medicos', methods=['GET'])
def obter_medicos():
    """
    Obtém todos os médicos cadastrados no sistema.
    
    Returns:
        list: Uma lista de médicos convertidos para dicionário.
    """
    medicos = db.obter_todos_medicos()
    return jsonify([medico.para_dict() for medico in medicos])

@app.route('/medicos/<int:medico_id>', methods=['GET'])
def obter_medico(medico_id):
    """
    Obtém um médico específico pelo seu ID.
    
    Args:
        medico_id (int): O ID do médico a ser obtido.
        
    Returns:
        dict: Os dados do médico se encontrado.
        tuple: Mensagem de erro e código 404 se não encontrado.
    """
    medico = db.obter_medico(medico_id)
    if medico:
        return jsonify(medico.para_dict())
    return jsonify({"erro": "Médico não encontrado"}), 404

@app.route('/medicos', methods=['POST'])
def adicionar_medico():
    """
    Adiciona um novo médico ao sistema.
    
    Returns:
        tuple: Os dados do médico adicionado e código 201 (Created).
    """
    dados = request.json
    medico = Medico(
        nome=dados.get('nome'),
        crm=dados.get('crm'),
        especializacao=dados.get('especializacao'),
        telefone=dados.get('telefone'),
        email=dados.get('email')
    )
    db.adicionar_medico(medico)
    return jsonify(medico.para_dict()), 201

# Rotas para consultas
@app.route('/consultas', methods=['GET'])
def obter_consultas():
    """
    Obtém todas as consultas cadastradas no sistema.
    
    Returns:
        list: Uma lista de consultas convertidas para dicionário.
    """
    consultas = db.obter_todas_consultas()
    return jsonify([consulta.para_dict() for consulta in consultas])

@app.route('/consultas/<int:consulta_id>', methods=['GET'])
def obter_consulta(consulta_id):
    """
    Obtém uma consulta específica pelo seu ID.
    
    Args:
        consulta_id (int): O ID da consulta a ser obtida.
        
    Returns:
        dict: Os dados da consulta se encontrada.
        tuple: Mensagem de erro e código 404 se não encontrada.
    """
    consulta = db.obter_consulta(consulta_id)
    if consulta:
        return jsonify(consulta.para_dict())
    return jsonify({"erro": "Consulta não encontrada"}), 404

@app.route('/consultas', methods=['POST'])
def adicionar_consulta():
    """
    Adiciona uma nova consulta ao sistema.
    
    Returns:
        tuple: Os dados da consulta adicionada e código 201 (Created).
    """
    dados = request.json
    consulta = Consulta(
        paciente_id=dados.get('paciente_id'),
        medico_id=dados.get('medico_id'),
        data=dados.get('data'),
        hora=dados.get('hora'),
        status=dados.get('status', 'Agendada'),
        observacoes=dados.get('observacoes', '')
    )
    db.adicionar_consulta(consulta)
    return jsonify(consulta.para_dict()), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)