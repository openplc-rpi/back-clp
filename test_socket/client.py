import socketio
from flask_socketio import emit

# Criar uma instância do cliente Socket.IO
sio = socketio.Client()

# Função para lidar com a conexão bem-sucedida ao servidor
@sio.event
def connect():
    print("Conectado ao servidor")
    sio.emit('run', 'teste')

# Função para lidar com a desconexão do servidor
@sio.event
def disconnect():
    print("Desconectado do servidor")

# Função para lidar com o evento 'json_data'
@sio.on('json_data')
def handle_json_data(data):
    print("Dados recebidos:", data)

# Conectar ao servidor (substitua pelo URL do seu servidor)
sio.connect('http://localhost:5000')

# Mantém o cliente ativo
sio.wait()
