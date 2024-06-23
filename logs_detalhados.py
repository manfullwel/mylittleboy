import logging
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

class Cliente(BaseModel):
    nome: str
    usuario: str
    telefone: str
    rg: str
    valor: float

@app.route('/cadastrar_cliente', methods=['POST'])
def cadastrar_cliente():
    try:
        data = request.get_json()
        logging.info(f"Recebido para cadastro: {data}")
        cliente = Cliente(**data)
        logging.info(f"Cliente validado: {cliente}")
        # Adicione aqui a lógica para cadastrar o cliente
        return jsonify({'message': 'Cliente cadastrado com sucesso'}), 200
    except ValidationError as e:
        logging.exception("Dados inválidos")
        return jsonify({'message': f'Dados inválidos: {e.errors()}'}), 400
    except Exception as e:
        logging.exception("Erro ao cadastrar cliente")
        return jsonify({'message': f'Erro ao cadastrar cliente: {str(e)}'}), 500

@app.route('/editar_cliente', methods=['POST'])
def editar_cliente():
    try:
        data = request.get_json()
        logging.info(f"Recebido para edição: {data}")
        cliente = Cliente(**data)
        logging.info(f"Cliente validado: {cliente}")
        # Adicione aqui a lógica para editar o cliente
        return jsonify({'message': 'Cliente atualizado com sucesso'}), 200
    except ValidationError as e:
        logging.exception("Dados inválidos")
        return jsonify({'message': f'Dados inválidos: {e.errors()}'}), 400
    except Exception as e:
        logging.exception("Erro ao editar cliente")
        return jsonify({'message': f'Erro ao editar cliente: {str(e)}'}), 500

@app.route('/deletar_cliente', methods=['POST'])
def deletar_cliente():
    try:
        if not request.is_json:
            logging.error("Content-Type não é application/json")
            return jsonify({'message': 'Content-Type deve ser application/json'}), 415
        
        data = request.get_json()
        usuario = data.get('usuario')
        
        if not usuario:
            logging.error("Usuário não especificado")
            return jsonify({'message': 'Usuário não especificado'}), 400
        
        logging.info(f"Recebido para deleção: {usuario}")
        # Adicione aqui a lógica para deletar o cliente
        return jsonify({'message': 'Cliente deletado com sucesso'}), 200
    
    except Exception as e:
        logging.exception("Erro ao deletar cliente")
        return jsonify({'message': f'Erro ao deletar cliente: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
