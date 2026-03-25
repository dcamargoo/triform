// ===== ELEMENTOS =====
const dropzone = document.querySelector("#drop-zone");
const label = document.querySelector("label.file-input");
const input = document.querySelector("input[type='file']");
const cancelBtn = document.getElementById("cancel-btn");
const downloadBtn = document.getElementById("download-btn");
const downloadOptions = document.getElementById("download-options");

// ===== ESTADO =====
const addedImages = new Set();
const maxImages = 100;
let progressInterval;

// ===== UTIL =====
// Retorna ou cria a área de preview das imagens
function getOrCreateBoxZone() {
  let boxZone = document.querySelector(".box-zone");

  if (!boxZone) {
    boxZone = document.createElement("div");
    boxZone.classList.add("box-zone");

    Object.assign(boxZone.style, {
      marginTop: "10px",
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      gap: "20px",
    });

    dropzone.insertAdjacentElement("afterend", boxZone);
  }

  return boxZone;
}

// Atualiza estado do botão "GERAR"
function updateButtonState() {
  const boxZone = document.querySelector(".box-zone");
  const button = document.querySelector("input[type='submit']");
  const clearBtn = document.querySelector(".clear-all-btn");

  if (!button) return;

  const hasImages = boxZone && boxZone.querySelectorAll("img").length > 0;

  if (hasImages) {
    button.classList.add("button-enabled");
    button.classList.remove("button-disabled");
    button.disabled = false;

    createClearButton();
    if (clearBtn) clearBtn.style.display = "block";
  } else {
    button.classList.add("button-disabled");
    button.classList.remove("button-enabled");
    button.disabled = true;

    if (clearBtn) clearBtn.style.display = "none";
  }
}

// Exibe mensagem de erro (evita duplicação de elementos)
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

// ===== UPLOAD =====
// Cria botão "REMOVER TUDO"
function createClearButton() {
  if (document.querySelector(".clear-all-btn")) return;

  const btn = document.createElement("button");
  btn.innerText = "REMOVER TUDO";
  btn.classList.add("clear-all-btn");

  Object.assign(btn.style, {
    display: "block",
    width: "190px",
    fontSize: "16px",
    fontWeight: "bold",
    margin: "20px auto",
    padding: "14px 28px",
    borderRadius: "15px",
    border: "none",
    background: "#ff3434",
    color: "white",
    cursor: "pointer",
  });

  btn.addEventListener("click", (e) => {
    e.preventDefault();

    const boxZone = document.querySelector(".box-zone");
    if (boxZone) boxZone.innerHTML = "";

    addedImages.clear();
    updateButtonState();
    btn.remove();
  });

  document.querySelector("#generate form").appendChild(btn);
}

// Cria preview da imagem com botão de remoção
function createImagePreview(file, fileID) {
  const boxZone = getOrCreateBoxZone();

  const wrapper = document.createElement("div");
  Object.assign(wrapper.style, {
    position: "relative",
    width: "96px",
    height: "96px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  });

  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  Object.assign(img.style, {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    borderRadius: "15px",
  });

  const removeBtn = document.createElement("button");
  removeBtn.innerText = "✕";

  Object.assign(removeBtn.style, {
    position: "absolute",
    top: "5px",
    right: "5px",
    width: "20px",
    height: "20px",
    borderRadius: "15px",
    background: "#2B2B2B",
    color: "#D7D7D7",
    cursor: "pointer",
  });

  removeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    wrapper.remove();
    addedImages.delete(fileID);
    updateButtonState();
  });

  wrapper.appendChild(img);
  wrapper.appendChild(removeBtn);
  boxZone.appendChild(wrapper);
}

// Processa arquivos selecionados:
// - valida formato
// - evita duplicados
// - limita quantidade
// - cria previews
input.addEventListener("change", () => {
  const files = Array.from(input.files);
  const boxZone = getOrCreateBoxZone();

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
    createImagePreview(file, fileID);
  });

  input.value = "";
  createClearButton();
  updateButtonState();
});

// ===== DRAG & DROP =====
function onEnter() {
  label.classList.add("active");
}

function onLeave() {
  label.classList.remove("active");
}

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

  getOrCreateBoxZone();

  input.files = e.dataTransfer.files;

  // força disparo do evento change manualmente
  input.dispatchEvent(new Event("change"));
});

dropzone.addEventListener("click", () => {
  let boxZone = document.querySelector(".box-zone");

  if (!boxZone) {
    // cria container de pré-visualização
    boxZone = document.createElement("div");
    boxZone.classList.add("box-zone");

    // mantém o mesmo estilo que antes
    Object.assign(boxZone.style, {
      marginTop: "10px",
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      gap: "20px",
      width: "100%",
      gridArea: "auto",
    });

    // insere logo após o dropzone para aparecer abaixo
    dropzone.parentNode.insertBefore(boxZone, dropzone.nextSibling);
  }
});

// ===== PROGRESSO =====
// Converte estágio em percentual
function getProgressPercentage(stage) {
  const stages = {
    idle: 0,
    preprocessamento: 10,
    sfm: 30,
    mvs: 70,
    mesh: 90,
    done: 100,
  };
  return stages[stage] || 0;
}

// Atualiza UI de progresso
function setStageLabel(stage) {
  const label = document.getElementById("progress-text");
  const bar = document.getElementById("progress-bar");

  const stages = {
    idle: "Aguardando envio...",
    preprocessamento: "Pré-processamento",
    sfm: "Executando SfM",
    mvs: "Executando MVS",
    mesh: "Gerando a malha",
    done: "Modelo pronto",
  };

  label.innerText = stages[stage] || stage;
  bar.style.width = getProgressPercentage(stage) + "%";
}

// Consulta backend e atualiza status
async function checkProgress() {
  const res = await fetch("/status");
  const data = await res.json();

  setStageLabel(data.stage);

  if (data.stage === "done") {
    clearInterval(progressInterval);

    document.querySelector("#progress-section").style.display = "none";
    document.querySelector("#viewer-section").style.display = "flex";

    window.dispatchEvent(new Event("mesh-ready"));
  }
}

function startProgressMonitoring() {
  progressInterval = setInterval(checkProgress, 2000);
}

// ===== CANCELAMENTO =====
cancelBtn.addEventListener("click", async () => {
  try {
    await fetch("/cancel", { method: "POST" });
  } catch (e) {
    console.error("Erro ao cancelar:", e);
  }

  clearInterval(progressInterval);

  document.getElementById("progress-bar").style.width = "0%";
  document.getElementById("progress-text").innerText = "Cancelado";

  setTimeout(() => {
    document.getElementById("progress-section").style.display = "none";
    document.getElementById("generate").style.display = "inline";

    const boxZone = document.querySelector(".box-zone");
    if (boxZone) boxZone.innerHTML = "";

    addedImages.clear();
    updateButtonState();
  }, 3000);
});

// ===== ENVIO =====
// Converte imagens preview em arquivos e envia pro backend
document
  .querySelector("input[type='submit']")
  .addEventListener("click", async (e) => {
    e.preventDefault();

    const boxZone = document.querySelector(".box-zone");
    if (!boxZone) return;

    const wrappers = boxZone.querySelectorAll("div");
    const formData = new FormData();

    const depthValue = document.getElementById("depth").value;

    const semFundo = document.getElementById("sem_fundo").checked;
    const invertNormals = document.getElementById("invertNormals").checked;

    const strategyValue = semFundo ? "sem_fundo" : "com_fundo";

    formData.append("depth", depthValue);
    formData.append("strategy", strategyValue);
    formData.append("invertNormals", invertNormals);

    const promises = Array.from(wrappers).map(async (wrapper, i) => {
      const img = wrapper.querySelector("img");
      const res = await fetch(img.src);
      const blob = await res.blob();

      formData.append(
        "file",
        new File([blob], `image${i}.png`, { type: blob.type })
      );
    });

    await Promise.all(promises);

    setTimeout(async () => {
      document.querySelector("#generate").style.display = "none";
      document.querySelector("#progress-section").style.display = "flex";

      window.dispatchEvent(new Event("resize"));

      startProgressMonitoring();

      try {
        await fetch("/upload", { method: "POST", body: formData });
      } catch (e) {
        console.log("Erro na reconstrução:", e);
      }
    }, 500);
  });

// ===== DOWNLOAD =====
downloadBtn.addEventListener("click", () => {
  downloadOptions.style.display =
    downloadOptions.style.display === "flex" ? "none" : "flex";
});

document.querySelectorAll(".download-options button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const format = btn.dataset.format;

    const formats = {
      ply: "/static/models/mesh.ply",
      obj: "/static/models/mesh.obj",
      stl: "/static/models/mesh.stl",
      glb: "/static/models/mesh.glb",
    };

    if (formats[format]) {
      window.location.href = formats[format];
    } else {
      alert("Formato não disponível.");
    }
  });
});

const depthSlider = document.getElementById("depth");
const depthValue = document.getElementById("depth-value");

if (depthSlider && depthValue) {
  depthSlider.addEventListener("input", () => {
    depthValue.innerText = depthSlider.value;
  });
}