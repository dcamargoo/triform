/* ===== OPEN 3D ===== */
import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";

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
    new THREE.MeshNormalMaterial()
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

window.addEventListener("DOMContentLoaded", () => {
  initViewer();
  updateButtonState();
});

/* ===== UPLOAD ===== */
const dropzone = document.querySelector("#drop-zone");
const label = document.querySelector("label.file-input");
const input = document.querySelector("input[type='file']");
const addedImages = new Set();
const maxImages = 10;

function updateButtonState() {
  const boxZone = document.querySelector(".box-zone");
  const button = document.querySelector(".button-gerar");
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
  input.files = e.dataTransfer.files;
  input.dispatchEvent(new Event("change"));
});

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

input.addEventListener("change", () => {
  const files = Array.from(input.files);
  const boxZone = document.querySelector(".box-zone");
  if (!boxZone) return;

  const currentImages = boxZone.querySelectorAll("img").length;
  const spacesLeft = maxImages - currentImages;
  if (spacesLeft <= 0) return;

  const validFormats = ["image/png", "image/jpg", "image/jpeg", "image/webp"];

  files.slice(0, spacesLeft).forEach(file => {
    const fileID = `${file.name}-${file.size}`;

    if (addedImages.has(fileID)) {
      showMessage("* Essa imagem já foi selecionada anteriormente.");
      return;
    }

    if (!validFormats.includes(file.type)) return;

    addedImages.add(fileID);

    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    wrapper.style.width = "128px";
    wrapper.style.height = "128px";
    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.justifyContent = "center";

    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "cover";
    img.style.borderRadius = "15px";

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
  });

  input.value = ""; 
  updateButtonState();
});

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

document.querySelector(".button-gerar").addEventListener("click", async (e) => {
  e.preventDefault();
  const boxZone = document.querySelector(".box-zone");
  if (!boxZone) return;

  const wrappers = boxZone.querySelectorAll("div");
  const formData = new FormData();

  wrappers.forEach((wrapper, i) => {
    const img = wrapper.querySelector("img");
    fetch(img.src)
      .then(res => res.blob())
      .then(blob => {
        formData.append("file", new File([blob], `image${i}.png`, { type: blob.type }));
      });
  });

  setTimeout(async () => {
    await fetch("/upload", { method: "POST", body: formData });
    window.location.reload();
  }, 500);
});
