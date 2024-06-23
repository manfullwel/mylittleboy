from flask import Flask, render_template, request, jsonify
from pydantic import BaseModel, ValidationError
from datetime import datetime
import csv
import os
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'
logging.basicConfig(level=logging.DEBUG)

log_filename = 'log.txt'

# Logging function
def log(message):
    with open(log_filename, 'a') as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

@app.route('/')
def index():
    return render_template('index.html')

# Pydantic model for Cliente
class Cliente(BaseModel):
    nome: str
    usuario: str
    telefone: str
    rg: str
    valor: float

    @property
    def horas(self):
        tarifas = {1: 3, 2: 5, 5: 10, 11: 20, 48: 50}
        for horas, valor in sorted(tarifas.items(), reverse=True):
            if self.valor >= valor:
                return horas
        return 0

# Helper function to read clientes from CSV
def read_clientes_from_csv():
    clientes = []
    try:
        if os.path.exists('clientes.csv'):
            with open('clientes.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    clientes.append(row)
        else:
            logging.error("Arquivo clientes.csv não encontrado")
    except Exception as e:
        logging.error(f"Erro ao ler clientes: {str(e)}")
    return clientes

# Helper function to write clientes to CSV
def write_clientes_to_csv(clientes):
    try:
        with open('clientes.csv', mode='w', newline='') as file:
            fieldnames = ['nome', 'usuario', 'telefone', 'rg', 'valor', 'horas', 'data_hora_cadastro']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for cliente in clientes:
                writer.writerow(cliente)
    except Exception as e:
        logging.error(f"Erro ao escrever clientes: {str(e)}")

@app.route('/cadastrar_cliente', methods=['POST'])
def cadastrar_cliente():
    try:
        data = request.form.to_dict()
        cliente = Cliente(**data)
        clientes = read_clientes_from_csv()
        for c in clientes:
            if c['nome'] == cliente.nome or c['usuario'] == cliente.usuario:
                return jsonify({'message': 'Cliente já cadastrado'}), 400
        
        data_hora_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clientes.append({
            'nome': cliente.nome,
            'usuario': cliente.usuario,
            'telefone': cliente.telefone,
            'rg': cliente.rg,
            'valor': cliente.valor,
            'horas': cliente.horas,
            'data_hora_cadastro': data_hora_cadastro
        })
        write_clientes_to_csv(clientes)
        log("Cliente cadastrado: " + cliente.nome)
        return jsonify({'message': 'Cliente cadastrado com sucesso'}), 200
    except ValidationError as e:
        return jsonify({'message': f'Dados inválidos: {e.json()}'}), 400
    except Exception as e:
        logging.error(f"Erro ao cadastrar cliente: {str(e)}")
        return jsonify({'message': f'Erro ao cadastrar cliente: {str(e)}'}), 500

@app.route('/listar_clientes', methods=['GET'])
def listar_clientes():
    logging.debug("Acessando a rota listar_clientes")
    try:
        clientes = read_clientes_from_csv()
        logging.debug(f"Clientes encontrados: {clientes}")
        return jsonify({'clientes': clientes}), 200
    except Exception as e:
        logging.error(f"Erro ao listar clientes: {str(e)}")
        return jsonify({'message': f'Erro ao listar clientes: {str(e)}'}), 500

@app.route('/deletar_cliente', methods=['POST'])
def deletar_cliente():
    try:
        if not request.is_json:
            return jsonify({'message': 'Content-Type deve ser application/json'}), 415
        
        data = request.get_json()
        usuario = data.get('usuario')
        
        if not usuario:
            return jsonify({'message': 'Usuário não especificado'}), 400
        
        clientes = read_clientes_from_csv()
        cliente_encontrado = any(c['usuario'] == usuario for c in clientes)
        
        if not cliente_encontrado:
            return jsonify({'message': 'Cliente não encontrado'}), 404
        
        clientes = [c for c in clientes if c['usuario'] != usuario]
        write_clientes_to_csv(clientes)
        log("Cliente deletado: " + usuario)
        return jsonify({'message': 'Cliente deletado com sucesso'}), 200
    
    except Exception as e:
        logging.error(f"Erro ao deletar cliente: {str(e)}")
        return jsonify({'message': f'Erro ao deletar cliente: {str(e)}'}), 500


@app.route('/cadastrar_cliente')
def form_cadastrar_cliente():
    return render_template('cadastrar_cliente.html')

@app.route('/clientes')
def listar_clientes_page():
    clientes = read_clientes_from_csv()
    return render_template('listar_clientes.html', clientes=clientes)

@app.route('/editar_cliente', methods=['GET', 'POST'])
def editar_cliente_page():
    if request.method == 'GET':
        usuario = request.args.get('usuario')
        if not usuario:
            return "Usuário não especificado", 400
        clientes = read_clientes_from_csv()
        cliente = next((c for c in clientes if c['usuario'] == usuario), None)
        if cliente:
            return render_template('editar_cliente.html', cliente=cliente)
        else:
            return "Cliente não encontrado", 404
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            cliente_atualizado = Cliente(**data)
            clientes = read_clientes_from_csv()
            for c in clientes:
                if c['usuario'] == cliente_atualizado.usuario:
                    c.update({
                        'nome': cliente_atualizado.nome,
                        'telefone': cliente_atualizado.telefone,
                        'rg': cliente_atualizado.rg,
                        'valor': cliente_atualizado.valor,
                        'horas': cliente_atualizado.horas
                    })
                    break
            write_clientes_to_csv(clientes)
            log("Cliente atualizado: " + cliente_atualizado.usuario)
            return jsonify({'message': 'Cliente atualizado com sucesso'}), 200
        except ValidationError as e:
            return jsonify({'message': f'Dados inválidos: {e.json()}'}), 400
        except Exception as e:
            logging.error(f"Erro ao atualizar cliente: {str(e)}")
            return jsonify({'message': f'Erro ao atualizar cliente: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
