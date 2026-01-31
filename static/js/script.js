import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";

// Three.js (cubo para teste)
function initViewer() {
  const canvas = document.getElementById("viewer-canvas");
  if (!canvas) return;

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 1000);
  camera.position.set(0, 0, 2.5);

  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(2, 2, 2);
  scene.add(light);

  const cube = new THREE.Mesh(
    new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshNormalMaterial(),
  );
  scene.add(cube);

  function resize() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (w === 0 || h === 0) return;

    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }

  function animate() {
    resize();
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  window.addEventListener("resize", resize);
  animate();
}

// Roda o viewer assim que a página carrega (UMA vez)
window.addEventListener("DOMContentLoaded", initViewer);

// Upload de imagens com drag and drop
const label = document.querySelector("label");
const input = document.querySelector("input");
const dropzone = document.querySelector("#drop-zone");
const fileinput = document.querySelector(".upload-card");

const msg = document.createElement("span");
fileinput.appendChild(msg);

const selectedFIles = new Set();

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

input.addEventListener("change", () => {
  msg.textContent = "";

  const formats = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  const files = Array.from(input.files).slice(0, 10);

  const placeholder = dropzone.querySelector(".placeholder");
  if (placeholder) placeholder.remove();

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
    remove.src = "./static/images/icon_delete.png";
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
        icon.src = "./static/images/icon_add_photo.png";

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
});
