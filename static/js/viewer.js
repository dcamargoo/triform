// responsável por carregar a malha gerada pelo meshing e permitir interação (zoom, rotação e movimentação)
import * as THREE from "three";
import { PLYLoader } from "https://cdn.jsdelivr.net/npm/three@0.156.0/examples/jsm/loaders/PLYLoader.js";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.156.0/examples/jsm/controls/OrbitControls.js";

// aguarda o carregamento completo do modelo antes de iniciar a configuração da cena e renderização
window.addEventListener("mesh-ready", () => {
  // captura o elemento canvas onde o modelo será renderizado
  const canvas = document.getElementById("viewer-canvas");
  if (!canvas) {
    console.error("Canvas #viewer-canvas não encontrado!");
    return;
  }

  // criação da cena principal (ambiente 3D)
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x111111);

  // define o eixo Z como "para cima" para compatibilidade com modelos gerados pelo COLMAP/Open3D
  THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

  // configuração da câmera em perspectiva responsável por definir o campo de visão e a posição inicial do observador
  const container = canvas.parentElement;
  const camera = new THREE.PerspectiveCamera(
    60,
    container.clientWidth / container.clientHeight,
    0.1,
    10000,
  );
  camera.position.set(0, 0, 10);

  // criação do renderer WebGL que desenha a cena no canvas
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    canvas: canvas,
  });
  renderer.setSize(container.clientWidth, container.clientHeight);

  // controles interativos de navegação (OrbitControls) permite rotacionar, dar zoom e mover a câmera com o mouse
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; // movimento suave
  controls.dampingFactor = 0.05;

  controls.enableZoom = true;
  controls.enablePan = true;
  controls.enableRotate = true;

  // limites de aproximação e afastamento da câmera
  controls.minDistance = 0.5;
  controls.maxDistance = 1000;

  // iluminação ambiente suave para evitar áreas totalmente escuras
  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambient);

  // luz direcional simulando uma fonte de luz principal
  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(5, 10, 7);
  scene.add(light);

  // criação do loader responsável por ler arquivos .PLY
  const loader = new PLYLoader();

  // carregamento da malha gerada pelo pipeline (meshing.py)
  loader.load(
    "/static/models/mesh.ply",
    (geometry) => {
      // cálculo das normais para melhorar a iluminação da superfície
      geometry.computeVertexNormals();

      // material padrão para renderização da malha
      const material = new THREE.MeshStandardMaterial({
        color: 0xdddddd,
        metalness: 0.1,
        roughness: 0.8,
      });

      // criação do objeto 3D a partir da geometria carregada
      const mesh = new THREE.Mesh(geometry, material);

      // ajuste de orientação para alinhar o modelo gerado pelo COLMAP com o sistema de eixos do Three.js
      mesh.rotation.x = -Math.PI / 2;

      // cálculo da bounding box para centralizar o modelo na cena
      const box = new THREE.Box3().setFromObject(mesh);
      const center = box.getCenter(new THREE.Vector3());
      mesh.position.sub(center);

      // adiciona o modelo à cena
      scene.add(mesh);

      // ajuste automático da distância da câmera baseado no tamanho do modelo
      const size = new THREE.Vector3();
      box.getSize(size);
      const maxDim = Math.max(size.x, size.y, size.z);

      camera.position.set(0, 0, maxDim * 2);

      // define o ponto de foco da câmera no centro do modelo
      controls.target.set(0, 0, 0);
      controls.update();

      // inicia o loop de renderização contínua
      animate();
    },
    undefined,
    (error) => console.error("Erro no loader:", error),
  );

  // loop principal de renderização responsável por atualizar os controles e redesenhar a cena a cada frame
  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }

  // ajuste automático ao redimensionar a janela mantém a proporção correta da câmera e do canvas
  window.addEventListener("resize", () => {
    const container = canvas.parentElement;

    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(container.clientWidth, container.clientHeight);
  });
});
