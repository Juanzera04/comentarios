from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.get("/")
def home():
    return render_template("index.html")

@socketio.on("atualizar_texto")
def handle_update(data):
    emit("receber_atualizacao", data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app)
