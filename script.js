const label = document.querySelector("label");

function onEnter() {
  label.classList.add("active");
}

function onLeave() {
  label.classList.remove("active");
}

label.addEventListener("dragenter", onEnter);
label.addEventListener("drop", onLeave);
label.addEventListener("dragend", onLeave);
label.addEventListener("dragleave", onLeave);
label.addEventListener("dragover", (e) => {
  e.preventDefault();
  label.classList.add("active");
});
label.addEventListener("drop", (e) => {
  e.preventDefault();

  const files = e.dataTransfer.files;

  input.files = files;

  input.dispatchEvent(new Event("change"));
});

const input = document.querySelector("input");
const dropzone = document.querySelector("#drop-zone");
const fileinput = document.querySelector(".upload-card");
const msg = document.createElement("span");

fileinput.appendChild(msg);

const selectedFIles = new Set();

input.addEventListener("change", () => {
  msg.textContent = "";

  const formats = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  const files = Array.from(input.files).slice(0, 10);
  const placeholder = dropzone.querySelector(".placeholder");

  if (placeholder) placeholder.remove();

  document.querySelector("#drop-zone");

  files.forEach((file) => {
    if (!formats.includes(file.type)) return;

    if (selectedFIles.has(file.name)) {
      msg.textContent = "* Essa imagem já foi selecionada anteriormente.";
      return;
    }

    selectedFIles.add(file.name);

    const wrapper = document.createElement("div");
    wrapper.classList.add("cover-wrapper");

    const img = document.createElement("img");
    img.id = "cover";
    img.src = URL.createObjectURL(file);

    const remove = document.createElement("img");
    remove.src = "./images/delete.png";
    remove.classList.add("remove-btn");

    remove.onclick = function (e) {
      e.preventDefault();
      e.stopPropagation();

      selectedFIles.delete(file.name);

      wrapper.remove();

      if (dropzone.querySelectorAll(".cover-wrapper").length === 0) {
        const placeholder = document.createElement("div");
        placeholder.classList.add("placeholder");

        const icon = document.createElement("img");
        icon.src = "./images/add_photo.png";

        const text = document.createElement("p");
        text.textContent = "Selecione até 10 imagens ou solte elas aqui";

        placeholder.appendChild(icon);
        placeholder.appendChild(text);

        dropzone.appendChild(placeholder);
      }
    };

    wrapper.appendChild(img);
    wrapper.appendChild(remove);
    dropzone.appendChild(wrapper);
  });

  input.value = "";
});