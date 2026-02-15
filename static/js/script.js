// captura dos elementos principais da interface
const dropzone = document.querySelector("#drop-zone");
const label = document.querySelector("label.file-input");
const input = document.querySelector("input[type='file']");

// estrutura para evitar adicionar imagens duplicadas
const addedImages = new Set();

// limite máximo de imagens permitido para o SfM
const maxImages = 10;

// função responsável por ativar/desativar o botão GERAR ele só é habilitado quando existir pelo menos uma imagem selecionada
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

// efeitos visuais ao arrastar arquivos sobre a área de upload
function onEnter() {
  label.classList.add("active");
}

function onLeave() {
  label.classList.remove("active");
}

// eventos de drag and drop
label.addEventListener("dragenter", onEnter);
label.addEventListener("dragleave", onLeave);
label.addEventListener("dragend", onLeave);
label.addEventListener("dragover", (e) => {
  e.preventDefault();
  label.classList.add("active");
});

// quando o usuário solta arquivos na área os arquivos são transferidos para o input e tratados normalmente
label.addEventListener("drop", (e) => {
  e.preventDefault();
  onLeave();

  const files = Array.from(e.dataTransfer.files);

  input.files = e.dataTransfer.files;
  input.dispatchEvent(new Event("change"));
});

// ao clicar na área de upload, cria dinamicamente o container onde as miniaturas das imagens serão exibidas
dropzone.addEventListener("click", () => {
  if (!document.querySelector(".box-zone")) {
    const boxZone = document.createElement("div");
    boxZone.classList.add("box-zone");

    // estilos da área onde ficam as imagens selecionadas
    boxZone.style.marginTop = "10px";
    boxZone.style.display = "flex";
    boxZone.style.flexWrap = "wrap";
    boxZone.style.justifyContent = "center";
    boxZone.style.gap = "20px";
    boxZone.style.gridArea = "auto";

    dropzone.insertAdjacentElement("afterend", boxZone);
  }
});

// quando novas imagens são selecionadas cria miniaturas + botão de remover
input.addEventListener("change", () => {

  const files = Array.from(input.files);
  const boxZone = document.querySelector(".box-zone");
  if (!boxZone) return;

  const currentImages = boxZone.querySelectorAll("img").length;
  const spacesLeft = maxImages - currentImages;
  if (spacesLeft <= 0) return;

  // formatos aceitos pelo pipeline SfM
  const validFormats = ["image/png", "image/jpg", "image/jpeg", "image/webp"];

  files.slice(0, spacesLeft).forEach((file) => {

    const fileID = `${file.name}-${file.size}`;

    // impede adicionar a mesma imagem duas vezes
    if (addedImages.has(fileID)) {
      showMessage("* Essa imagem já foi selecionada anteriormente.");
      return;
    }

    if (!validFormats.includes(file.type)) return;

    addedImages.add(fileID);

    // container individual da imagem
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    wrapper.style.width = "128px";
    wrapper.style.height = "128px";
    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.justifyContent = "center";

    // criação da miniatura
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "cover";
    img.style.borderRadius = "15px";

    // botão para remover imagem da lista
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

    // remove a imagem selecionada
    removeBtn.addEventListener("click", (e) => {
      e.preventDefault();
      wrapper.remove();
      addedImages.delete(fileID);
      updateButtonState();
    });

    wrapper.appendChild(img);
    wrapper.appendChild(removeBtn);
    boxZone.appendChild(wrapper);
  });

  input.value = "";
  updateButtonState();
});

// exibe mensagens de erro ao usuário
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

// envio das imagens para o backend Flask cria um FormData com todas as imagens e chama a rota /upload
document.querySelector("input[type='submit']").addEventListener("click", async (e) => {
  e.preventDefault();

  const boxZone = document.querySelector(".box-zone");
  if (!boxZone) return;

  const wrappers = boxZone.querySelectorAll("div");
  const formData = new FormData();

  // converte as miniaturas em arquivos novamente
  wrappers.forEach((wrapper, i) => {
    const img = wrapper.querySelector("img");

    fetch(img.src)
      .then((res) => res.blob())
      .then((blob) => {
        formData.append(
          "file",
          new File([blob], `image${i}.png`, { type: blob.type }),
        );
      });
  });

  // pequena espera para garantir que os blobs foram adicionados
  setTimeout(async () => {
    await fetch("/upload", { method: "POST", body: formData });
    window.location.reload();
  }, 500);
});