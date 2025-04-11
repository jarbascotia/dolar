from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

DB_PATH = '/app/db/carteira.db'

def init_db():
    """Inicializa apenas a tabela do dólar"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dolar (
            id INTEGER PRIMARY KEY,
            data_compra TEXT NOT NULL,
            valor_compra REAL NOT NULL,
            taxa_compra REAL NOT NULL,
            quantidade REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_cotacao_atual():  # MOVIDA PARA ANTES DAS ROTAS
    try:
        response = requests.get('https://economia.awesomeapi.com.br/json/last/USD-BRL')
        response.raise_for_status()
        return float(response.json()['USDBRL']['bid'])
    except Exception as e:
        raise ValueError(f'Erro ao obter cotação: {str(e)}')

@app.route('/api/dolar', methods=['GET'])  # ROTA CORRETAMENTE INDENTADA
def get_dolar():
    try:
        cotacao = get_cotacao_atual()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        registros = conn.execute('SELECT * FROM dolar').fetchall()
        
        resultados = []
        for reg in registros:
            registro = dict(reg)
            registro.update({
                'valor_atual': round(reg['quantidade'] * cotacao, 2),
                'lucro': round(reg['quantidade'] * cotacao - reg['valor_compra'], 2),
                'cotacao_atual': cotacao
            })
            resultados.append(registro)
            
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dolar', methods=['POST'])  # ROTA CORRETAMENTE INDENTADA
def add_dolar():
    try:
        data = request.get_json()
        if not data or not all(field in data for field in ['data_compra', 'valor_compra', 'quantidade']):
            return jsonify({'error': 'Dados incompletos'}), 400

        valor = float(data['valor_compra'])
        qtd = float(data['quantidade'])
        taxa = valor / qtd

        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO dolar (data_compra, valor_compra, taxa_compra, quantidade)
            VALUES (?, ?, ?, ?)
        ''', (data['data_compra'], valor, taxa, qtd))
        conn.commit()
        return jsonify({'message': 'Registro criado'}), 201
        
    except ValueError:
        return jsonify({'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dolar/<int:id>', methods=['PUT'])
def update_dolar(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400

        required = ['data_compra', 'valor_compra', 'quantidade']
        if not all(field in data for field in required):
            return jsonify({'error': f'Campos obrigatórios: {", ".join(required)}'}), 400

        # Conversão dos valores
        valor = float(data['valor_compra'])
        qtd = float(data['quantidade'])
        taxa = valor / qtd

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE dolar SET
                data_compra = ?,
                valor_compra = ?,
                taxa_compra = ?,
                quantidade = ?
            WHERE id = ?
        ''', (data['data_compra'], valor, taxa, qtd, id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Registro não encontrado'}), 404
            
        conn.commit()
        conn.close()
        return jsonify({'message': 'Atualizado com sucesso'}), 200

    except ValueError:
        return jsonify({'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dolar/<int:id>', methods=['DELETE'])
def delete_dolar(id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM dolar WHERE id = ?', (id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Registro não encontrado'}), 404
            
        conn.commit()
        conn.close()
        return jsonify({'message': 'Excluído com sucesso'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3004)