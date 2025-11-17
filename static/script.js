// socket
const socket = io();

// UI elements
const welcomeOverlay = document.getElementById("welcomeOverlay");
const nickInput = document.getElementById("nickInput");
const escudosContainer = document.getElementById("escudosContainer");
const enterBtn = document.getElementById("enterBtn");

const usersList = document.getElementById("usersList");

// caixas
const caixas = document.querySelectorAll(".caixa");

// estado local
let chosenAvatar = null;
let mySid = null;

// fetch escudos list and render thumbnails
async function loadEscudos(){
    escudosContainer.innerHTML = "<p class='mini'>Carregando escudos...</p>";
    try {
        const res = await fetch("/escudos_list");
        const escudos = await res.json();
        if (!escudos || escudos.length === 0) {
            escudosContainer.innerHTML = "<p class='mini'>Nenhum escudo encontrado em templates/escudos/</p>";
            return;
        }
        escudosContainer.innerHTML = "";
        escudos.forEach(e => {
            const img = document.createElement("img");
            img.src = e.url;
            img.className = "escudoThumb";
            img.title = e.name;
            img.addEventListener("click", () => {
                // reset selected
                document.querySelectorAll(".escudoThumb").forEach(i => i.classList.remove("escudoSelected"));
                img.classList.add("escudoSelected");
                chosenAvatar = e.url;
                validateEntry();
            });
            escudosContainer.appendChild(img);
        });
    } catch (err) {
        escudosContainer.innerHTML = "<p class='mini'>Erro ao carregar escudos</p>";
        console.error(err);
    }
}

// valida se nick e avatar foram escolhidos
function validateEntry(){
    enterBtn.disabled = !(nickInput.value.trim().length > 0 && chosenAvatar);
}

// on input change
nickInput.addEventListener("input", validateEntry);

// when enter
enterBtn.addEventListener("click", () => {
    const nick = nickInput.value.trim();
    if(!nick || !chosenAvatar) return;
    // envia join para o servidor
    socket.emit("join", { nick, avatar: chosenAvatar });
    // esconde overlay
    welcomeOverlay.style.display = "none";
});

// listen for users_update (lista atual)
socket.on("users_update", (users) => {
    usersList.innerHTML = "";
    users.forEach(u => {
        const li = document.createElement("li");
        li.className = "userItem";
        const img = document.createElement("img");
        img.className = "userAvatar";
        img.src = u.avatar || "/static/default-avatar.png";
        const span = document.createElement("div");
        span.className = "userNick";
        span.innerText = u.nick || "Anon";
        li.appendChild(img);
        li.appendChild(span);
        usersList.appendChild(li);
    });
});

// quando o servidor informar para atualizar texto
socket.on("receber_atualizacao", data => {
    const el = document.getElementById(data.id);
    if(!el) return;
    // não sobrescreve se o usuário estiver digitando na caixa (activeElement)
    if (document.activeElement !== el) {
        el.value = data.valor;
    }
});

// envia atualizações ao digitar
caixas.forEach(caixa => {
    caixa.addEventListener("input", () => {
        socket.emit("atualizar_texto", {
            id: caixa.id,
            valor: caixa.value
        });
    });
});

// inicializa
loadEscudos();
