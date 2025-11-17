import os
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "secret-key")
socketio = SocketIO(app, cors_allowed_origins="*")

# estrutura para armazenar usuários conectados
# chave = sid (session id), valor = {"nick": ..., "avatar": ...}
connected_users = {}

# rota principal
@app.get("/")
def index():
    return render_template("index.html")

# retorna lista de escudos (procura em templates/escudos e static/escudos se existir)
@app.get("/escudos_list")
def escudos_list():
    escudos = []
    # primeiro: templates/escudos
    tmpl_dir = os.path.join(app.root_path, "templates", "escudos")
    if os.path.isdir(tmpl_dir):
        for f in sorted(os.listdir(tmpl_dir)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
                escudos.append({"name": f, "url": f"/escudo/{f}"})
    # também verifica static/escudos (caso queira duplicar lá)
    static_dir = os.path.join(app.root_path, "static", "escudos")
    if os.path.isdir(static_dir):
        for f in sorted(os.listdir(static_dir)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
                # evita duplicatas pelo mesmo nome
                if not any(e["name"] == f for e in escudos):
                    escudos.append({"name": f, "url": f"/static/escudos/{f}"})
    return jsonify(escudos)

# serve o arquivo de templates/escudos/<filename>
@app.get("/escudo/<filename>")
def serve_escudo(filename):
    tmpl_dir = os.path.join(app.root_path, "templates", "escudos")
    if os.path.isdir(tmpl_dir) and os.path.exists(os.path.join(tmpl_dir, filename)):
        return send_from_directory(tmpl_dir, filename)
    # fallback para static if exists
    static_path = os.path.join(app.root_path, "static", "escudos")
    if os.path.isdir(static_path) and os.path.exists(os.path.join(static_path, filename)):
        return send_from_directory(static_path, filename)
    return ("Not Found", 404)

# socket events
@socketio.on("join")
def on_join(data):
    sid = request_sid()
    nick = data.get("nick", "Anon")
    avatar = data.get("avatar", "")
    connected_users[sid] = {"nick": nick, "avatar": avatar}
    emit_user_list()

@socketio.on("atualizar_texto")
def handle_update(data):
    # recebeu {id: caixaId, valor: texto}
    emit("receber_atualizacao", data, broadcast=True, include_self=False)

@socketio.on("disconnect")
def on_disconnect():
    sid = request_sid()
    if sid in connected_users:
        del connected_users[sid]
        emit_user_list()

def emit_user_list():
    # envia lista de usuários como array: [{sid, nick, avatar}, ...]
    users = []
    for sid, info in connected_users.items():
        users.append({"sid": sid, "nick": info["nick"], "avatar": info["avatar"]})
    emit("users_update", users, broadcast=True)

def request_sid():
    # helper para pegar sid da request do socket
    # flask-socketio disponibiliza via flask.request? usamos socketio.server e flask-socketio internamente
    # mas a maneira garantida:
    from flask import request
    return request.sid

if __name__ == "__main__":
    # apenas para desenvolvimento; no Render usamos gunicorn + eventlet
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
