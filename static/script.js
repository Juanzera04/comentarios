const socket = io();

// QUANDO EU DIGITO → Envio aos outros
document.querySelectorAll(".caixa").forEach(caixa => {
    caixa.addEventListener("input", () => {
        socket.emit("atualizar_texto", {
            id: caixa.id,
            valor: caixa.value
        });
    });
});

// QUANDO ALGUÉM OUTRO DIGITA → Atualiza na minha tela
socket.on("receber_atualizacao", data => {
    const caixa = document.getElementById(data.id);

    // Evita loop infinito
    if (caixa !== document.activeElement) {
        caixa.value = data.valor;
    }
});
