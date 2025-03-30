import sqlite3
import json
import os
import datetime
import tkinter as tk

class BancoDadosFisioterapia:
    """
    Classe responsável por gerenciar o banco de dados da aplicação de fisioterapia.
    Armazena todos os dados do formulário de avaliação fisioterapêutica.
    """
    
    def __init__(self, nome_db="fisioterapia.db"):
        """
        Inicializa o banco de dados e cria as tabelas se não existirem.
        
        Args:
            nome_db (str): Nome do arquivo do banco de dados SQLite.
        """
        self.nome_db = nome_db
        self._criar_tabelas()
    
    def _conectar(self):
        """
        Estabelece uma conexão com o banco de dados SQLite.
        
        Returns:
            tuple: (Conexão, Cursor) para operações no banco de dados.
        """
        conn = sqlite3.connect(self.nome_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        return conn, cursor
    
    def _criar_tabelas(self):
        """
        Cria as tabelas necessárias no banco de dados se não existirem.
        
        A estrutura inclui:
        - pacientes: Informações básicas do paciente
        - avaliacoes: Dados da avaliação fisioterapêutica
        - secoes_historico: Histórico clínico do paciente
        - avaliacao_fisica: Dados da avaliação física detalhada
        - provas_especificas: Resultados de testes específicos
        - medidas_escalas: Dados de medições e escalas de dor
        - diagnosticos: Diagnóstico fisioterapêutico
        - tratamento: Plano de tratamento
        - seguimento: Informações de acompanhamento e reavaliação
        """
        conn, cursor = self._conectar()
        
        # Tabela de Pacientes (dados básicos)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade TEXT,
            genero TEXT,
            contato TEXT,
            data_nascimento TEXT,
            area_consulta TEXT,
            alergias TEXT,
            data_cadastro TEXT
        )
        ''')
        
        # Tabela de Avaliações (principal)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            data_avaliacao TEXT,
            fisioterapeuta TEXT,
            observacoes TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
        )
        ''')
        
        # Tabela de Histórico Clínico
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_clinico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            motivo_consulta TEXT,
            antecedentes TEXT,
            enfermedad_actual TEXT,
            cirugias_previas TEXT,
            medicamentos_actuales TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Avaliação Física (exame físico básico)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exame_fisico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            pa TEXT,
            pulso TEXT,
            talla TEXT,
            peso TEXT,
            temperatura TEXT,
            fr TEXT,
            sat_o2 TEXT,
            idx TEXT,
            conducta TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Inspeção e Palpação
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspeccion_palpacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            postura TEXT,
            simetria_corporal TEXT,
            deformidades_aparentes TEXT,
            puntos_dolorosos TEXT,
            tension_muscular TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Coluna Vertebral
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS columna_vertebral (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            curvas_fisiologicas TEXT,
            escoliosis TEXT,
            cifosis_lordosis TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Mobilidade Articular
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movilidad_articular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            movimiento_activo TEXT,
            movimiento_pasivo TEXT,
            evaluacion_articulaciones TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Força Muscular
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuerza_muscular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            evaluacion_grupos_musculares TEXT,
            grados_fuerza TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Avaliação Neuromuscular
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluacion_neuromuscular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            reflejos TEXT,
            coordinacion_motora TEXT,
            equilibrio TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Avaliação Funcional
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluacion_funcional (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            capacidad_actividades_diarias TEXT,
            limitaciones_dificultades TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Coordenação
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            ejercicios_dedos TEXT,
            precision_movimientos TEXT,
            marcha TEXT,
            equilibrio_dinamico TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Provas Específicas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pruebas_especificas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            pruebas_ortopedicas TEXT,
            pruebas_neurologicas TEXT,
            pruebas_estabilidad TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Escalas de Dor
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS escalas_dolor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            eva_valor INTEGER,
            observaciones_dolor TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Diagnósticos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            resumen_problema TEXT,
            objetivos_tratamiento TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Plano de Tratamento
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_tratamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            sesiones_semana TEXT,
            duracion_sesion TEXT,
            obs_frecuencia TEXT,
            ejercicios_recomendados TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        # Tabela de Seguimento
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS seguimiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER,
            programacion_seguimiento TEXT,
            fecha_evaluacion TEXT,
            criterio_revision TEXT,
            criterios_adicionales TEXT,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def salvar_avaliacao(self, dados_formulario):
        """
        Salva todos os dados do formulário no banco de dados.
        
        Args:
            dados_formulario (dict): Dicionário contendo todos os dados do formulário.
            
        Returns:
            int: ID da avaliação criada.
        """
        conn, cursor = self._conectar()
        
        try:
            # Iniciar transação
            conn.execute("BEGIN TRANSACTION")
            
            # 1. Salvar dados do paciente
            data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Verificar se tem nome do paciente
            nome_paciente = dados_formulario.get('Nombre Completo', '')
            
            # Inserir paciente
            cursor.execute('''
            INSERT INTO pacientes (
                nome, idade, genero, contato, data_nascimento, 
                area_consulta, alergias, data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados_formulario.get('Nombre Completo', ''),
                dados_formulario.get('Edad', ''),
                dados_formulario.get('Genero', ''),
                dados_formulario.get('Contacto', ''),
                dados_formulario.get('Fecha Nasc.', ''),
                dados_formulario.get('Área de consulta', ''),
                dados_formulario.get('Alergias', ''),
                data_atual
            ))
            
            paciente_id = cursor.lastrowid
            
            # 2. Inserir avaliação principal
            cursor.execute('''
            INSERT INTO avaliacoes (
                paciente_id, data_avaliacao, fisioterapeuta, observacoes
            ) VALUES (?, ?, ?, ?)
            ''', (
                paciente_id,
                data_atual,
                '',  # Campo para nome do fisioterapeuta (pode ser adicionado ao formulário)
                ''   # Observações gerais
            ))
            
            avaliacao_id = cursor.lastrowid
            
            # 3. Histórico Clínico
            cursor.execute('''
            INSERT INTO historico_clinico (
                avaliacao_id, motivo_consulta, antecedentes, 
                enfermedad_actual, cirugias_previas, medicamentos_actuales
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Motivo de consulta', ''),
                dados_formulario.get('Antecedentes', ''),
                dados_formulario.get('Efermedad actual', ''),
                dados_formulario.get('Cirurgías previas', ''),
                dados_formulario.get('Medicamentos actuales', '')
            ))
            
            # 4. Exame Físico
            cursor.execute('''
            INSERT INTO exame_fisico (
                avaliacao_id, pa, pulso, talla, peso, 
                temperatura, fr, sat_o2, idx, conducta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('PA', ''),
                dados_formulario.get('Pulso', ''),
                dados_formulario.get('Talla', ''),
                dados_formulario.get('Peso', ''),
                dados_formulario.get('T', ''),
                dados_formulario.get('FR', ''),
                dados_formulario.get('Sat.O2', ''),
                dados_formulario.get('IDx', ''),
                dados_formulario.get('Conducta', '')
            ))
            
            # 5. Inspeção e Palpação
            cursor.execute('''
            INSERT INTO inspeccion_palpacion (
                avaliacao_id, postura, simetria_corporal, 
                deformidades_aparentes, puntos_dolorosos, tension_muscular
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Postura', ''),
                dados_formulario.get('Simetría corporal', ''),
                dados_formulario.get('Deformidades aparentes', ''),
                dados_formulario.get('Puntos dolorosos', ''),
                dados_formulario.get('Tensión muscular', '')
            ))
            
            # 6. Coluna Vertebral
            cursor.execute('''
            INSERT INTO columna_vertebral (
                avaliacao_id, curvas_fisiologicas, escoliosis, cifosis_lordosis
            ) VALUES (?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Curvas Fisiológicas', ''),
                dados_formulario.get('Presencia de Escoliosis', ''),
                dados_formulario.get('Cifosis o Lordosis', '')
            ))
            
            # 7. Mobilidade Articular
            cursor.execute('''
            INSERT INTO movilidad_articular (
                avaliacao_id, movimiento_activo, movimiento_pasivo, evaluacion_articulaciones
            ) VALUES (?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Movimiento Activo', ''),
                dados_formulario.get('Movimiento Pasivo', ''),
                dados_formulario.get('Evaluación de articulaciones', '')
            ))
            
            # 8. Força Muscular
            # Converter lista de opcões selecionadas para string JSON
            forca_muscular = dados_formulario.get('Fuerza Muscular', [])
            forca_json = json.dumps(forca_muscular) if forca_muscular else ''
            
            cursor.execute('''
            INSERT INTO fuerza_muscular (
                avaliacao_id, evaluacion_grupos_musculares, grados_fuerza
            ) VALUES (?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Evaluación de grupos musculares', ''),
                forca_json
            ))
            
            # 9. Avaliação Neuromuscular
            cursor.execute('''
            INSERT INTO evaluacion_neuromuscular (
                avaliacao_id, reflejos, coordinacion_motora, equilibrio
            ) VALUES (?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Reflejos', ''),
                dados_formulario.get('Coordinación motora', ''),
                dados_formulario.get('Equilibrio', '')
            ))
            
            # 10. Avaliação Funcional
            cursor.execute('''
            INSERT INTO evaluacion_funcional (
                avaliacao_id, capacidad_actividades_diarias, limitaciones_dificultades
            ) VALUES (?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Capacidad para realizar actividades diarias', ''),
                dados_formulario.get('Limitaciones y dificultades', '')
            ))
            
            # 11. Coordenação
            cursor.execute('''
            INSERT INTO coordinacion (
                avaliacao_id, ejercicios_dedos, precision_movimientos, 
                marcha, equilibrio_dinamico
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Ejercicios con dedos', ''),
                dados_formulario.get('Precisión en movimientos', ''),
                dados_formulario.get('Marcha', ''),
                dados_formulario.get('Equilibrio Dinámico', '')
            ))
            
            # 12. Provas Específicas
            cursor.execute('''
            INSERT INTO pruebas_especificas (
                avaliacao_id, pruebas_ortopedicas, pruebas_neurologicas, pruebas_estabilidad
            ) VALUES (?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Pruebas ortopédicas', ''),
                dados_formulario.get('Pruebas neurológicas', ''),
                dados_formulario.get('Pruebas de estabilidad', '')
            ))
            
            # 13. Escalas de Dor
            cursor.execute('''
            INSERT INTO escalas_dolor (
                avaliacao_id, eva_valor, observaciones_dolor
            ) VALUES (?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('escala_eva', 0),
                dados_formulario.get('observaciones_dolor', '')
            ))
            
            # 14. Diagnósticos
            cursor.execute('''
            INSERT INTO diagnosticos (
                avaliacao_id, resumen_problema, objetivos_tratamiento
            ) VALUES (?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('Resumen del problema', ''),
                dados_formulario.get('Objetivos del tratamiento', '')
            ))
            
            # 15. Plano de Tratamento
            cursor.execute('''
            INSERT INTO plan_tratamiento (
                avaliacao_id, sesiones_semana, duracion_sesion, 
                obs_frecuencia, ejercicios_recomendados
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('sesiones_semana', ''),
                dados_formulario.get('duracion_sesion', ''),
                dados_formulario.get('obs_frecuencia', ''),
                dados_formulario.get('Ejercicios recomendados', '')
            ))
            
            # 16. Seguimento
            cursor.execute('''
            INSERT INTO seguimiento (
                avaliacao_id, programacion_seguimiento, fecha_evaluacion, 
                criterio_revision, criterios_adicionales
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                avaliacao_id,
                dados_formulario.get('programacion_seguimiento', ''),
                dados_formulario.get('fecha_evaluacion', ''),
                dados_formulario.get('criterio_revision', ''),
                dados_formulario.get('criterios_adicionales', '')
            ))
            
            # Confirmar transação
            conn.commit()
            
            return avaliacao_id
            
        except sqlite3.Error as e:
            # Em caso de erro, reverter transação
            conn.rollback()
            print(f"Erro ao salvar no banco de dados: {e}")
            raise
        
        finally:
            conn.close()
    
    def obter_avaliacao(self, avaliacao_id):
        """
        Obtém uma avaliação completa do banco de dados.
        
        Args:
            avaliacao_id (int): ID da avaliação a ser obtida.
            
        Returns:
            dict: Dicionário contendo todos os dados da avaliação.
        """
        conn, cursor = self._conectar()
        
        # Criar dicionário vazio para armazenar os dados
        dados = {}
        
        try:
            # 1. Obter dados da avaliação e paciente
            cursor.execute('''
            SELECT a.*, p.* FROM avaliacoes a
            JOIN pacientes p ON a.paciente_id = p.id
            WHERE a.id = ?
            ''', (avaliacao_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Preencher dados básicos
            dados['id'] = row['id']
            dados['data_avaliacao'] = row['data_avaliacao']
            dados['Nombre Completo'] = row['nome']
            dados['Edad'] = row['idade']
            dados['Genero'] = row['genero']
            dados['Contacto'] = row['contato']
            dados['Fecha Nasc.'] = row['data_nascimento']
            dados['Área de consulta'] = row['area_consulta']
            dados['Alergias'] = row['alergias']
            
            # 2. Obter histórico clínico
            cursor.execute('SELECT * FROM historico_clinico WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Motivo de consulta'] = row['motivo_consulta']
                dados['Antecedentes'] = row['antecedentes']
                dados['Efermedad actual'] = row['enfermedad_actual']
                dados['Cirurgías previas'] = row['cirugias_previas']
                dados['Medicamentos actuales'] = row['medicamentos_actuales']
            
            # 3. Obter exame físico
            cursor.execute('SELECT * FROM exame_fisico WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['PA'] = row['pa']
                dados['Pulso'] = row['pulso']
                dados['Talla'] = row['talla']
                dados['Peso'] = row['peso']
                dados['T'] = row['temperatura']
                dados['FR'] = row['fr']
                dados['Sat.O2'] = row['sat_o2']
                dados['IDx'] = row['idx']
                dados['Conducta'] = row['conducta']
            
            # 4. Obter inspeção e palpação
            cursor.execute('SELECT * FROM inspeccion_palpacion WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Postura'] = row['postura']
                dados['Simetría corporal'] = row['simetria_corporal']
                dados['Deformidades aparentes'] = row['deformidades_aparentes']
                dados['Puntos dolorosos'] = row['puntos_dolorosos']
                dados['Tensión muscular'] = row['tension_muscular']
            
            # 5. Obter coluna vertebral
            cursor.execute('SELECT * FROM columna_vertebral WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Curvas Fisiológicas'] = row['curvas_fisiologicas']
                dados['Presencia de Escoliosis'] = row['escoliosis']
                dados['Cifosis o Lordosis'] = row['cifosis_lordosis']
            
            # 6. Obter mobilidade articular
            cursor.execute('SELECT * FROM movilidad_articular WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Movimiento Activo'] = row['movimiento_activo']
                dados['Movimiento Pasivo'] = row['movimiento_pasivo']
                dados['Evaluación de articulaciones'] = row['evaluacion_articulaciones']
            
            # 7. Obter força muscular
            cursor.execute('SELECT * FROM fuerza_muscular WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Evaluación de grupos musculares'] = row['evaluacion_grupos_musculares']
                
                # Converter string JSON para lista
                if row['grados_fuerza']:
                    try:
                        dados['Fuerza Muscular'] = json.loads(row['grados_fuerza'])
                    except json.JSONDecodeError:
                        dados['Fuerza Muscular'] = []
                else:
                    dados['Fuerza Muscular'] = []
            
            # 8. Obter avaliação neuromuscular
            cursor.execute('SELECT * FROM evaluacion_neuromuscular WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Reflejos'] = row['reflejos']
                dados['Coordinación motora'] = row['coordinacion_motora']
                dados['Equilibrio'] = row['equilibrio']
            
            # 9. Obter avaliação funcional
            cursor.execute('SELECT * FROM evaluacion_funcional WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Capacidad para realizar actividades diarias'] = row['capacidad_actividades_diarias']
                dados['Limitaciones y dificultades'] = row['limitaciones_dificultades']
            
            # 10. Obter coordenação
            cursor.execute('SELECT * FROM coordinacion WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Ejercicios con dedos'] = row['ejercicios_dedos']
                dados['Precisión en movimientos'] = row['precision_movimientos']
                dados['Marcha'] = row['marcha']
                dados['Equilibrio Dinámico'] = row['equilibrio_dinamico']
            
            # 11. Obter provas específicas
            cursor.execute('SELECT * FROM pruebas_especificas WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Pruebas ortopédicas'] = row['pruebas_ortopedicas']
                dados['Pruebas neurológicas'] = row['pruebas_neurologicas']
                dados['Pruebas de estabilidad'] = row['pruebas_estabilidad']
            
            # 12. Obter escalas de dor
            cursor.execute('SELECT * FROM escalas_dolor WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['escala_eva'] = row['eva_valor']
                dados['observaciones_dolor'] = row['observaciones_dolor']
            
            # 13. Obter diagnósticos
            cursor.execute('SELECT * FROM diagnosticos WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['Resumen del problema'] = row['resumen_problema']
                dados['Objetivos del tratamiento'] = row['objetivos_tratamiento']
            
            # 14. Obter plano de tratamento
            cursor.execute('SELECT * FROM plan_tratamiento WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['sesiones_semana'] = row['sesiones_semana']
                dados['duracion_sesion'] = row['duracion_sesion']
                dados['obs_frecuencia'] = row['obs_frecuencia']
                dados['Ejercicios recomendados'] = row['ejercicios_recomendados']
            
            # 15. Obter seguimento
            cursor.execute('SELECT * FROM seguimiento WHERE avaliacao_id = ?', (avaliacao_id,))
            row = cursor.fetchone()
            if row:
                dados['programacion_seguimiento'] = row['programacion_seguimiento']
                dados['fecha_evaluacion'] = row['fecha_evaluacion']
                dados['criterio_revision'] = row['criterio_revision']
                dados['criterios_adicionales'] = row['criterios_adicionales']
            
            return dados
            
        except sqlite3.Error as e:
            print(f"Erro ao obter avaliação: {e}")
            return None
        
        finally:
            conn.close()
    
    def listar_avaliacoes(self, filtro=None):
        """
        Lista todas as avaliações no banco de dados.
        
        Args:
            filtro (str, opcional): Filtro de pesquisa por nome do paciente.
            
        Returns:
            list: Lista de dicionários com dados resumidos das avaliações.
        """
        conn, cursor = self._conectar()
        
        try:
            query = '''
            SELECT a.id, a.data_avaliacao, p.nome, p.idade, p.genero, 
                p.contato, s.fecha_evaluacion
            FROM avaliacoes a
            JOIN pacientes p ON a.paciente_id = p.id
            LEFT JOIN seguimiento s ON a.id = s.avaliacao_id
            '''
            
            params = []
            if filtro:
                query += " WHERE p.nome LIKE ?"
                params.append(f"%{filtro}%")
            
            query += " ORDER BY a.data_avaliacao DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            avaliacoes = []
            for row in rows:
                # Converter o objeto Row do SQLite para um dicionário
                fecha_evaluacion = row['fecha_evaluacion'] if 'fecha_evaluacion' in row.keys() else ''
                
                avaliacoes.append({
                    'id': row['id'],
                    'data': row['data_avaliacao'],
                    'nome': row['nome'],
                    'idade': row['idade'],
                    'genero': row['genero'],
                    'fecha_evaluacion': fecha_evaluacion
                })
            
            return avaliacoes
            
        except sqlite3.Error as e:
            print(f"Erro ao listar avaliações: {e}")
            return []
        
        finally:
            conn.close()
    
    def atualizar_avaliacao(self, avaliacao_id, dados_formulario):
        """
        Atualiza os dados de uma avaliação existente.
        
        Args:
            avaliacao_id (int): ID da avaliação a ser atualizada.
            dados_formulario (dict): Novos dados do formulário.
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.
        """
        conn, cursor = self._conectar()
        
        try:
            # Iniciar transação
            conn.execute("BEGIN TRANSACTION")
            
            # 1. Obter o ID do paciente
            cursor.execute("SELECT paciente_id FROM avaliacoes WHERE id = ?", (avaliacao_id,))
            row = cursor.fetchone()
            if not row:
                return False
                
            paciente_id = row['paciente_id']
            
            # 2. Atualizar dados do paciente
            cursor.execute('''
            UPDATE pacientes SET
                nome = ?,
                idade = ?,
                genero = ?,
                contato = ?,
                data_nascimento = ?,
                area_consulta = ?,
                alergias = ?
            WHERE id = ?
            ''', (
                dados_formulario.get('Nombre Completo', ''),
                dados_formulario.get('Edad', ''),
                dados_formulario.get('Genero', ''),
                dados_formulario.get('Contacto', ''),
                dados_formulario.get('Fecha Nasc.', ''),
                dados_formulario.get('Área de consulta', ''),
                dados_formulario.get('Alergias', ''),
                paciente_id
            ))
            
            # 3. Atualizar histórico clínico
            cursor.execute('''
            UPDATE historico_clinico SET
                motivo_consulta = ?,
                antecedentes = ?,
                enfermedad_actual = ?,
                cirugias_previas = ?,
                medicamentos_actuales = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Motivo de consulta', ''),
                dados_formulario.get('Antecedentes', ''),
                dados_formulario.get('Efermedad actual', ''),
                dados_formulario.get('Cirurgías previas', ''),
                dados_formulario.get('Medicamentos actuales', ''),
                avaliacao_id
            ))
            
            # 4. Atualizar exame físico
            cursor.execute('''
            UPDATE exame_fisico SET
                pa = ?,
                pulso = ?,
                talla = ?,
                peso = ?,
                temperatura = ?,
                fr = ?,
                sat_o2 = ?,
                idx = ?,
                conducta = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('PA', ''),
                dados_formulario.get('Pulso', ''),
                dados_formulario.get('Talla', ''),
                dados_formulario.get('Peso', ''),
                dados_formulario.get('T', ''),
                dados_formulario.get('FR', ''),
                dados_formulario.get('Sat.O2', ''),
                dados_formulario.get('IDx', ''),
                dados_formulario.get('Conducta', ''),
                avaliacao_id
            ))
            
            # 5. Atualizar inspeção e palpação
            cursor.execute('''
            UPDATE inspeccion_palpacion SET
                postura = ?,
                simetria_corporal = ?,
                deformidades_aparentes = ?,
                puntos_dolorosos = ?,
                tension_muscular = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Postura', ''),
                dados_formulario.get('Simetría corporal', ''),
                dados_formulario.get('Deformidades aparentes', ''),
                dados_formulario.get('Puntos dolorosos', ''),
                dados_formulario.get('Tensión muscular', ''),
                avaliacao_id
            ))
            
            # 6. Atualizar coluna vertebral
            cursor.execute('''
            UPDATE columna_vertebral SET
                curvas_fisiologicas = ?,
                escoliosis = ?,
                cifosis_lordosis = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Curvas Fisiológicas', ''),
                dados_formulario.get('Presencia de Escoliosis', ''),
                dados_formulario.get('Cifosis o Lordosis', ''),
                avaliacao_id
            ))
            
            # 7. Atualizar mobilidade articular
            cursor.execute('''
            UPDATE movilidad_articular SET
                movimiento_activo = ?,
                movimiento_pasivo = ?,
                evaluacion_articulaciones = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Movimiento Activo', ''),
                dados_formulario.get('Movimiento Pasivo', ''),
                dados_formulario.get('Evaluación de articulaciones', ''),
                avaliacao_id
            ))
            
            # 8. Atualizar força muscular
            # Converter lista para JSON
            forca_muscular = dados_formulario.get('Fuerza Muscular', [])
            forca_json = json.dumps(forca_muscular) if forca_muscular else ''
            
            cursor.execute('''
            UPDATE fuerza_muscular SET
                evaluacion_grupos_musculares = ?,
                grados_fuerza = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Evaluación de grupos musculares', ''),
                forca_json,
                avaliacao_id
            ))
            
            # 9. Atualizar avaliação neuromuscular
            cursor.execute('''
            UPDATE evaluacion_neuromuscular SET
                reflejos = ?,
                coordinacion_motora = ?,
                equilibrio = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Reflejos', ''),
                dados_formulario.get('Coordinación motora', ''),
                dados_formulario.get('Equilibrio', ''),
                avaliacao_id
            ))
            
            # 10. Atualizar avaliação funcional
            cursor.execute('''
            UPDATE evaluacion_funcional SET
                capacidad_actividades_diarias = ?,
                limitaciones_dificultades = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Capacidad para realizar actividades diarias', ''),
                dados_formulario.get('Limitaciones y dificultades', ''),
                avaliacao_id
            ))
            
            # 11. Atualizar coordenação
            cursor.execute('''
            UPDATE coordinacion SET
                ejercicios_dedos = ?,
                precision_movimientos = ?,
                marcha = ?,
                equilibrio_dinamico = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Ejercicios con dedos', ''),
                dados_formulario.get('Precisión en movimientos', ''),
                dados_formulario.get('Marcha', ''),
                dados_formulario.get('Equilibrio Dinámico', ''),
                avaliacao_id
            ))
            
            # 12. Atualizar provas específicas
            cursor.execute('''
            UPDATE pruebas_especificas SET
                pruebas_ortopedicas = ?,
                pruebas_neurologicas = ?,
                pruebas_estabilidad = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Pruebas ortopédicas', ''),
                dados_formulario.get('Pruebas neurológicas', ''),
                dados_formulario.get('Pruebas de estabilidad', ''),
                avaliacao_id
            ))
            
            # 13. Atualizar escalas de dor
            cursor.execute('''
            UPDATE escalas_dolor SET
                eva_valor = ?,
                observaciones_dolor = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('escala_eva', 0),
                dados_formulario.get('observaciones_dolor', ''),
                avaliacao_id
            ))
            
            # 14. Atualizar diagnósticos
            cursor.execute('''
            UPDATE diagnosticos SET
                resumen_problema = ?,
                objetivos_tratamiento = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('Resumen del problema', ''),
                dados_formulario.get('Objetivos del tratamiento', ''),
                avaliacao_id
            ))
            
            # 15. Atualizar plano de tratamento
            cursor.execute('''
            UPDATE plan_tratamiento SET
                sesiones_semana = ?,
                duracion_sesion = ?,
                obs_frecuencia = ?,
                ejercicios_recomendados = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('sesiones_semana', ''),
                dados_formulario.get('duracion_sesion', ''),
                dados_formulario.get('obs_frecuencia', ''),
                dados_formulario.get('Ejercicios recomendados', ''),
                avaliacao_id
            ))
            
            # 16. Atualizar seguimento
            cursor.execute('''
            UPDATE seguimiento SET
                programacion_seguimiento = ?,
                fecha_evaluacion = ?,
                criterio_revision = ?,
                criterios_adicionales = ?
            WHERE avaliacao_id = ?
            ''', (
                dados_formulario.get('programacion_seguimiento', ''),
                dados_formulario.get('fecha_evaluacion', ''),
                dados_formulario.get('criterio_revision', ''),
                dados_formulario.get('criterios_adicionales', ''),
                avaliacao_id
            ))
            
            # Confirmar transação
            conn.commit()
            
            return True
            
        except sqlite3.Error as e:
            # Em caso de erro, reverter transação
            conn.rollback()
            print(f"Erro ao atualizar avaliação: {e}")
            return False
        
        finally:
            conn.close()
    
    def excluir_avaliacao(self, avaliacao_id):
        """
        Exclui uma avaliação do banco de dados.
        
        Args:
            avaliacao_id (int): ID da avaliação a ser excluída.
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário.
        """
        conn, cursor = self._conectar()
        
        try:
            # Iniciar transação
            conn.execute("BEGIN TRANSACTION")
            
            # Obter o ID do paciente
            cursor.execute("SELECT paciente_id FROM avaliacoes WHERE id = ?", (avaliacao_id,))
            row = cursor.fetchone()
            if not row:
                return False
                
            paciente_id = row['paciente_id']
            
            # Excluir registros relacionados
            tabelas = [
                'historico_clinico', 'exame_fisico', 'inspeccion_palpacion',
                'columna_vertebral', 'movilidad_articular', 'fuerza_muscular',
                'evaluacion_neuromuscular', 'evaluacion_funcional', 'coordinacion',
                'pruebas_especificas', 'escalas_dolor', 'diagnosticos',
                'plan_tratamiento', 'seguimiento'
            ]
            
            for tabela in tabelas:
                cursor.execute(f"DELETE FROM {tabela} WHERE avaliacao_id = ?", (avaliacao_id,))
            
            # Excluir a avaliação
            cursor.execute("DELETE FROM avaliacoes WHERE id = ?", (avaliacao_id,))
            
            # Excluir o paciente (opcional - pode querer manter para histórico)
            cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
            
            # Confirmar transação
            conn.commit()
            
            return True
            
        except sqlite3.Error as e:
            # Em caso de erro, reverter transação
            conn.rollback()
            print(f"Erro ao excluir avaliação: {e}")
            return False
        
        finally:
            conn.close()
    
    def buscar_pacientes(self, termo_busca):
        """
        Busca pacientes pelo nome ou contato.
        
        Args:
            termo_busca (str): Termo para busca.
            
        Returns:
            list: Lista de dicionários com dados dos pacientes encontrados.
        """
        conn, cursor = self._conectar()
        
        try:
            # Realizar busca
            cursor.execute('''
            SELECT * FROM pacientes 
            WHERE nome LIKE ? OR contato LIKE ?
            ORDER BY nome
            ''', (f"%{termo_busca}%", f"%{termo_busca}%"))
            
            rows = cursor.fetchall()
            
            pacientes = []
            for row in rows:
                pacientes.append({
                    'id': row['id'],
                    'nome': row['nome'],
                    'idade': row['idade'],
                    'genero': row['genero'],
                    'contato': row['contato'],
                    'data_nascimento': row['data_nascimento']
                })
            
            return pacientes
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar pacientes: {e}")
            return []
        
        finally:
            conn.close()
    
    def exportar_avaliacao_json(self, avaliacao_id, caminho_arquivo=None):
        """
        Exporta os dados de uma avaliação para um arquivo JSON.
        
        Args:
            avaliacao_id (int): ID da avaliação a ser exportada.
            caminho_arquivo (str, opcional): Caminho para salvar o arquivo. 
                Se None, retorna o JSON como string.
                
        Returns:
            str ou bool: String JSON se caminho_arquivo for None, 
                        ou True/False indicando sucesso/falha.
        """
        # Obter os dados da avaliação
        dados = self.obter_avaliacao(avaliacao_id)
        if not dados:
            return False
        
        # Converter para JSON formatado
        json_str = json.dumps(dados, ensure_ascii=False, indent=4)
        
        # Se não for especificado caminho, retorna a string JSON
        if not caminho_arquivo:
            return json_str
        
        # Salvar em arquivo
        try:
            nome_paciente = dados.get('Nombre Completo', '').replace(' ', '_').lower()
            if not nome_paciente:
                nome_paciente = 'paciente'
                
            data_atual = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Se não for especificado um caminho completo, criar o nome do arquivo
            if not os.path.basename(caminho_arquivo):
                nome_arquivo = f"{nome_paciente}_{data_atual}.json"
                caminho_arquivo = os.path.join(caminho_arquivo, nome_arquivo)
                
            # Certificar que o diretório existe
            os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
            
            # Salvar arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            return True
            
        except Exception as e:
            print(f"Erro ao exportar para JSON: {e}")
            return False
    
    def importar_avaliacao_json(self, caminho_arquivo):
        """
        Importa uma avaliação de um arquivo JSON.
        
        Args:
            caminho_arquivo (str): Caminho do arquivo JSON.
            
        Returns:
            int ou None: ID da avaliação importada ou None se falhar.
        """
        try:
            # Ler arquivo JSON
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
            
            # Salvar no banco de dados
            return self.salvar_avaliacao(dados_json)
            
        except Exception as e:
            print(f"Erro ao importar arquivo JSON: {e}")
            return None
    
    def estatisticas_gerais(self):
        """
        Obtém estatísticas gerais do banco de dados.
        
        Returns:
            dict: Dicionário com estatísticas.
        """
        conn, cursor = self._conectar()
        
        try:
            stats = {}
            
            # Total de pacientes
            cursor.execute("SELECT COUNT(*) as total FROM pacientes")
            stats['total_pacientes'] = cursor.fetchone()['total']
            
            # Total de avaliações
            cursor.execute("SELECT COUNT(*) as total FROM avaliacoes")
            stats['total_avaliacoes'] = cursor.fetchone()['total']
            
            # Avaliações por mês (últimos 6 meses)
            cursor.execute('''
            SELECT strftime('%Y-%m', data_avaliacao) as mes, COUNT(*) as total 
            FROM avaliacoes 
            WHERE data_avaliacao >= date('now', '-6 months') 
            GROUP BY mes 
            ORDER BY mes DESC
            ''')
            stats['avaliacoes_por_mes'] = [dict(row) for row in cursor.fetchall()]
            
            # Distribuição por gênero
            cursor.execute('''
            SELECT genero, COUNT(*) as total 
            FROM pacientes 
            GROUP BY genero
            ''')
            stats['distribuicao_genero'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
            
        except sqlite3.Error as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
        
        finally:
            conn.close()


# Integração com o formulário

def modificar_salvar_formulario(formulario_fisioterapia_instance):
    """
    Função para substituir o método salvar_formulario do FormularioFisioterapia
    para utilizar o banco de dados SQLite em vez de arquivos JSON.
    
    Args:
        formulario_fisioterapia_instance: Instância da classe FormularioFisioterapia
        
    Returns:
        None
    """
    def novo_salvar_formulario(self):
        """Salva os dados do formulário no banco de dados e atualiza a aba de clientes"""
        try:
            # Coletar todos os dados
            dados = {}
            
            # Processar os campos de texto
            for etiqueta, campo in self.campos.items():
                if hasattr(campo, 'obter'):
                    dados[etiqueta] = campo.obter()
                elif hasattr(campo, 'get_date'):  # Para DateEntry
                    dados[etiqueta] = campo.get_date().strftime('%d/%m/%Y')
                elif hasattr(campo, 'get'):  # Para Scale, StringVar
                    if isinstance(campo, tk.Scale):
                        dados[etiqueta] = int(campo.get())
                    elif isinstance(campo, tk.StringVar):
                        dados[etiqueta] = campo.get()
            
            # Processar os checkbuttons
            forca_muscular = []
            for (check, var) in self.checkbuttons:
                if var.get():
                    forca_muscular.append(check.cget('text'))
            
            dados['Fuerza Muscular'] = forca_muscular
            
            # Processar radio buttons
            for var_name, var in self.radio_buttons.items():
                dados[var_name] = var.get()
            
            # Inicializar banco de dados
            db = BancoDadosFisioterapia()
            
            # Salvar no banco de dados
            avaliacao_id = db.salvar_avaliacao(dados)
            
            # Resetar flag de modificação
            self.modificado = False
            
            # Se estivermos no contexto de uma aplicação integrada, atualizar a aba de clientes
            try:
                # Obter acesso ao notebook
                parent = self.frame.master
                
                # Procurar a aba de clientes
                for index in range(parent.index('end')):
                    tab_name = parent.tab(index, "text")
                    if tab_name == "Clientes":
                        # Encontrar a instância da AbaClientes
                        aba_clientes_widget = None
                        aba_clientes_frame = parent.winfo_children()[index]
                        
                        # Procurar o objeto AbaClientes dentro dos widgets
                        for widget in aba_clientes_frame.winfo_children():
                            if hasattr(widget, 'carregar_pacientes'):
                                aba_clientes_widget = widget
                                break
                            elif hasattr(widget, 'winfo_children'):
                                for child in widget.winfo_children():
                                    if hasattr(child, 'carregar_pacientes'):
                                        aba_clientes_widget = child
                                        break
                        
                        # Se encontramos a aba, atualizamos ela
                        if aba_clientes_widget:
                            aba_clientes_widget.carregar_pacientes()
                        
                # Alterar para a aba de clientes
                parent.select(0)  # Assumindo que a aba de clientes é a primeira
                
            except Exception as e:
                print(f"Aviso: Não foi possível atualizar a aba de clientes: {e}")
            
            # Mostrar mensagem de sucesso
            import tkinter.messagebox as messagebox
            messagebox.showinfo(
                "Guardar", 
                f"Evaluación guardada correctamente.\nID: {avaliacao_id}",
                icon='info'
            )
            
            return dados
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Error", 
                f"Error al guardar el formulario: {str(e)}",
                icon='error'
            )
    
    # Substituir o método
    import types
    formulario_fisioterapia_instance.salvar_formulario = types.MethodType(
        novo_salvar_formulario, formulario_fisioterapia_instance)
    
    return formulario_fisioterapia_instance


# Exemplo de uso:
if __name__ == "__main__":
    db = BancoDadosFisioterapia()
    
    # Testar estrutura do banco de dados
    print("Banco de dados criado com sucesso!")
    
    # Exemplo de dados de formulário
    exemplo_dados = {
        'Nombre Completo': 'João Silva',
        'Edad': '35',
        'Genero': 'Masculino',
        'Contacto': '11 98765-4321',
        'Fecha Nasc.': '15/05/1988',
        'Área de consulta': 'Fisioterapia Ortopédica',
        'Alergias': 'Nenhuma',
        'Motivo de consulta': 'Dor lombar',
        'escala_eva': 7
    }
    
    # Salvar exemplo
    id_avaliacao = db.salvar_avaliacao(exemplo_dados)
    print(f"Avaliação salva com ID: {id_avaliacao}")
    
    # Recuperar dados
    dados_recuperados = db.obter_avaliacao(id_avaliacao)
    print("Dados recuperados:", dados_recuperados['Nombre Completo'], dados_recuperados['escala_eva'])