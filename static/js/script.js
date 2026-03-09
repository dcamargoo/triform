// ===== Configuração inicial e captura de elementos DOM =====
const dropzone = document.querySelector("#drop-zone");          // área de drag & drop
const label = document.querySelector("label.file-input");       // label do input de arquivo
const input = document.querySelector("input[type='file']");     // input de seleção de arquivos
const cancelBtn = document.getElementById("cancel-btn");        // botão de cancelar upload
const downloadBtn = document.getElementById("download-btn");    // botão de download
const downloadOptions = document.getElementById("download-options"); // opções de download

// conjunto para evitar imagens duplicadas
const addedImages = new Set();

// limite máximo de imagens permitidas para o SfM
const maxImages = 100;

// ===== Funções auxiliares =====
// Ativa ou desativa o botão "GERAR" dependendo da presença de imagens
function updateButtonState() {
  const boxZone = document.querySelector(".box-zone");
  const button = document.querySelector("input[type='submit']");
  if (!button) return;

  const hasImages = boxZone && boxZone.querySelectorAll("img").length > 0;

  if (hasImages) {
    button.classList.add("button-enabled");
    button.classList.remove("button-disabled");
    button.disabled = false;
  } else {
    button.classList.add("button-disabled");
    button.classList.remove("button-enabled");
    button.disabled = true;
  }
}

// Atualiza o texto do progresso com base no estágio atual
function setStageLabel(stage){
  const label = document.getElementById("progress-text");
  const bar = document.getElementById("progress-bar");

  const stages = {
    idle: "Aguardando envio...",
    preprocessamento: "Pré-processamento",
    sfm: "Executando SfM",
    mvs: "Gerando nuvem densa (MVS)",
    mesh: "Gerando malha 3D",
    done: "Modelo pronto"
  };

  label.innerText = stages[stage] || stage;

  // atualiza a barra de progresso
  const percent = getProgressPercentage(stage);
  bar.style.width = percent + "%";
}

// Converte estágio em percentual de progresso
function getProgressPercentage(stage) {
  const stages = {
    idle: 0,
    preprocessamento: 10,
    sfm: 30,
    mvs: 70,
    mesh: 90,
    done: 100
  };
  return stages[stage] || 0;
}

// Mostra mensagem de erro para o usuário
function showMessage(text) {
  let msg = document.querySelector(".msg-erro");
  const form = document.querySelector("#generate form .file-input");
  if (!form) return;

  if (!msg) {
    msg = document.createElement("p");
    msg.classList.add("msg-erro");
    msg.style.color = "red";
    msg.style.marginLeft = "-400px";
    form.insertAdjacentElement("beforebegin", msg);
  }

  msg.textContent = text;
}

// Cria botão "REMOVER TUDO" caso não exista
function createClearButton() {
  if (document.querySelector(".clear-all-btn")) return;

  const btn = document.createElement("button");
  btn.innerText = "REMOVER TUDO";
  btn.classList.add("clear-all-btn");

  btn.style.display = "block";
  btn.style.fontSize = "16px";
  btn.style.fontWeight = "bold";
  btn.style.margin = "20px auto";
  btn.style.padding = "18px 36px";
  btn.style.borderRadius = "15px";
  btn.style.border = "none";
  btn.style.background = "#ff3434";
  btn.style.color = "white";
  btn.style.cursor = "pointer";

  btn.addEventListener("click", (e) => {
    e.preventDefault();
    const boxZone = document.querySelector(".box-zone");
    if (boxZone) boxZone.innerHTML = "";

    addedImages.clear();
    updateButtonState();
    btn.remove(); // remove o botão do DOM
  });

  const form = document.querySelector("#generate form");
  form.appendChild(btn);
}

// Marca um passo como concluído (visual)
function completeStep(stepName) {
  const el = document.getElementById("step-" + stepName);
  if (el) {
    el.classList.remove("active");
    el.classList.add("done");
  }
}

// ===== Eventos de drag & drop =====
function onEnter() { label.classList.add("active"); }
function onLeave() { label.classList.remove("active"); }

label.addEventListener("dragenter", onEnter);
label.addEventListener("dragleave", onLeave);
label.addEventListener("dragend", onLeave);

label.addEventListener("dragover", (e) => {
  e.preventDefault();
  label.classList.add("active");
});

label.addEventListener("drop", (e) => {
  e.preventDefault();
  onLeave();

  const files = Array.from(e.dataTransfer.files);

  if (!document.querySelector(".box-zone")) {
    const boxZone = document.createElement("div");
    boxZone.classList.add("box-zone");
    boxZone.style.marginTop = "10px";
    boxZone.style.display = "flex";
    boxZone.style.flexWrap = "wrap";
    boxZone.style.justifyContent = "center";
    boxZone.style.gap = "20px";
    dropzone.insertAdjacentElement("afterend", boxZone);
  }

  input.files = e.dataTransfer.files;
  input.dispatchEvent(new Event("change"));
});

// ===== Clique na área de upload cria container para miniaturas =====
dropzone.addEventListener("click", () => {
  if (!document.querySelector(".box-zone")) {
    const boxZone = document.createElement("div");
    boxZone.classList.add("box-zone");
    boxZone.style.marginTop = "10px";
    boxZone.style.display = "flex";
    boxZone.style.flexWrap = "wrap";
    boxZone.style.justifyContent = "center";
    boxZone.style.gap = "20px";
    boxZone.style.gridArea = "auto";
    dropzone.insertAdjacentElement("afterend", boxZone);
  }
});

// ===== Processamento de imagens selecionadas =====
input.addEventListener("change", () => {
  const files = Array.from(input.files);
  const boxZone = document.querySelector(".box-zone");
  if (!boxZone) return;

  const currentImages = boxZone.querySelectorAll("img").length;
  const spacesLeft = maxImages - currentImages;
  if (spacesLeft <= 0) return;

  const validFormats = ["image/png", "image/jpg", "image/jpeg", "image/webp"];

  files.slice(0, spacesLeft).forEach((file) => {
    const fileID = `${file.name}-${file.size}`;

    if (addedImages.has(fileID)) {
      showMessage("* Essa imagem já foi selecionada anteriormente.");
      return;
    }

    if (!validFormats.includes(file.type)) return;

    addedImages.add(fileID);

    // wrapper da miniatura
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    wrapper.style.width = "128px";
    wrapper.style.height = "128px";
    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.justifyContent = "center";

    // miniatura
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "cover";
    img.style.borderRadius = "15px";

    // botão de remover
    const removeBtn = document.createElement("button");
    removeBtn.innerText = "X";
    removeBtn.style.position = "absolute";
    removeBtn.style.top = "5px";
    removeBtn.style.right = "5px";
    removeBtn.style.width = "25px";
    removeBtn.style.height = "25px";
    removeBtn.style.borderRadius = "15px";
    removeBtn.style.background = "#2B2B2B";
    removeBtn.style.color = "#D7D7D7";
    removeBtn.style.cursor = "pointer";

    removeBtn.addEventListener("click", (e) => {
      e.preventDefault();
      wrapper.remove();
      addedImages.delete(fileID);
      updateButtonState();
    });

    wrapper.appendChild(img);
    wrapper.appendChild(removeBtn);
    boxZone.appendChild(wrapper);

    createClearButton();
  });

  input.value = "";
  updateButtonState();
});

// ===== Cancelamento do upload / processamento =====
cancelBtn.addEventListener("click", async () => {
  try {
    await fetch("/cancel", { method: "POST" });
  } catch (e) {
    console.error("Erro ao cancelar:", e);
  }

  clearInterval(progressInterval);

  document.getElementById("progress-bar").style.width = "0%";
  document.getElementById("progress-text").innerText = "Cancelado";

  document.getElementById("progress-section").style.display = "none";
  document.getElementById("generate").style.display = "inline";

  const boxZone = document.querySelector(".box-zone");
  if (boxZone) boxZone.innerHTML = "";

  const clearBtn = document.querySelector(".clear-all-btn");
  if (clearBtn) {
    clearBtn.style.display = "none";
  }

  addedImages.clear();
  updateButtonState();

  createClearButton();
});

// ===== Envio das imagens para o backend Flask =====
document.querySelector("input[type='submit']").addEventListener("click", async (e) => {
  e.preventDefault();

  const boxZone = document.querySelector(".box-zone");
  if (!boxZone) return;

  const wrappers = boxZone.querySelectorAll("div");
  const formData = new FormData();

  const promises = Array.from(wrappers).map(async (wrapper, i) => {
    const img = wrapper.querySelector("img");
    const res = await fetch(img.src);
    const blob = await res.blob();
    formData.append("file", new File([blob], `image${i}.png`, { type: blob.type }));
  });

  await Promise.all(promises);

  setTimeout(async () => {
    document.querySelector("#generate").style.display = "none";
    document.querySelector("#progress-section").style.display = "flex";

    startProgressMonitoring();

    try {
      await fetch("/upload", { method: "POST", body: formData });
    } catch (e) {
      console.log("Erro na reconstrução:", e);
    }
  }, 500);
});

// ===== Monitoramento do progresso =====
let progressInterval;

async function checkProgress() {
  const res = await fetch("/status");
  const data = await res.json();
  const stage = data.stage;

  setStageLabel(stage);

  if (stage === "done") {
    document.querySelector("#progress-section").style.display = "flex";
    document.querySelector("#viewer-section").style.display = "flex";
    clearInterval(progressInterval);
  }
}

function startProgressMonitoring() {
  progressInterval = setInterval(checkProgress, 2000);
}

// ===== Download do modelo gerado =====
downloadBtn.addEventListener("click", () => {
  downloadOptions.style.display = downloadOptions.style.display === "flex" ? "none" : "flex";
});

document.querySelectorAll(".download-options button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const format = btn.dataset.format;
    if (format === "ply") {
      window.location.href = "/static/models/mesh.ply";
    } else {
      alert("Esse formato ainda não está disponível.");
    }
  });
});