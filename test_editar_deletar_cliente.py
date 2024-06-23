import pytest
import json
from flask import Flask
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_editar_cliente_existente(client):
    # Adicionar cliente para edição
    response = client.post('/cadastrar_cliente', data=json.dumps({
        'nome': 'Teste',
        'usuario': 'testuser',
        'telefone': '999999999',
        'rg': '123456789',
        'valor': 10.0
    }), content_type='application/json')
    print(response.data)  # Adicionar log para verificar a resposta
    assert response.status_code == 200, f"Response data: {response.data}"
    
    # Editar cliente existente
    response = client.post('/editar_cliente', data=json.dumps({
        'nome': 'Teste Editado',
        'usuario': 'testuser',
        'telefone': '888888888',
        'rg': '987654321',
        'valor': 20.0
    }), content_type='application/json')
    print(response.data)  # Adicionar log para verificar a resposta
    assert response.status_code == 200, f"Response data: {response.data}"
    assert b'Cliente atualizado com sucesso' in response.data

def test_deletar_cliente_sem_usuario(client):
    response = client.post('/deletar_cliente', data=json.dumps({}), content_type='application/json')
    print(response.data)  # Adicionar log para verificar a resposta
    assert response.status_code == 400, f"Response data: {response.data}"
    assert b'Usu\\u00e1rio n\\u00e3o especificado' in response.data

def test_deletar_cliente_sem_parametro(client):
    response = client.post('/deletar_cliente', data=json.dumps({'invalid': 'param'}), content_type='application/json')
    print(response.data)  # Adicionar log para verificar a resposta
    assert response.status_code == 400, f"Response data: {response.data}"
    assert b'Usu\\u00e1rio n\\u00e3o especificado' in response.data

def test_deletar_cliente_inexistente(client):
    response = client.post('/deletar_cliente', data=json.dumps({'usuario': 'inexistente'}), content_type='application/json')
    print(response.data)  # Adicionar log para verificar a resposta
    assert response.status_code == 404, f"Response data: {response.data}"
    assert b'Cliente n\\u00e3o encontrado' in response.data
