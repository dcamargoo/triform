 # Triform

O **Triform** é uma aplicação web criada para reconstrução tridimensional (3D) de objetos reais a partir de imagens capturadas com dispositivos comuns, como smartphones. O sistema automatiza todo o pipeline de fotogrametria, desde o upload das imagens até a geração, otimização, visualização e exportação de modelos 3D.

A ideia do projeto surgiu da dificuldade existente na geração de modelos 3D a partir de imagens, processo que tradicionalmente exige equipamentos especializados e conhecimento técnico avançado, limitando seu acesso a usuários não especialistas.

A aplicação utiliza técnicas de Visão Computacional, como Structure from Motion (SfM) e Multi-View Stereo (MVS), permitindo a criação de modelos tridimensionais de forma automatizada, sem a necessidade de equipamentos especializados ou conhecimento profundo na área por parte do usuário.

O projeto foi desenvolvido como Trabalho de Conclusão de Curso (TCC) pela Universidade Presbiteriana Mackenzie em conjunto com meu colega **Cláudio Dias Alves**, obtendo uma avaliação **EXCELENTE** pela banca, o que evidencia a qualidade técnica e a consistência dos resultados alcançados.

---

## Objetivos

- Desenvolver uma aplicação web para reconstrução 3D de objetos reais  
- Automatizar o pipeline completo de fotogrametria  
- Permitir o uso de imagens capturadas por celulares comuns  
- Gerar nuvens de pontos esparsas e densas  
- Reconstruir e otimizar malhas 3D  
- Permitir a visualização e exportação dos modelos gerados  
- Avaliar a qualidade dos modelos reconstruídos  

---

## Pipeline de Reconstrução

1. Pré-processamento opcional das imagens (CLAHE, balanço de branco, filtro bilateral e remoção de fundo)  
2. Structure from Motion (SfM) para geração da nuvem de pontos esparsa (PyCOLMAP)  
3. Multi-View Stereo (MVS) para densificação da nuvem de pontos (PyCOLMAP)  
4. Reconstrução de malha 3D via Poisson Surface Reconstruction (Open3D)  
5. Otimização e exportação em múltiplos formatos (PLY, OBJ, STL e GLB) (Open3D)  

---

## Testes Realizados

Foram realizados testes qualitativos e quantitativos com o objetivo de avaliar a qualidade dos modelos 3D gerados pelo sistema Triform, considerando diferentes condições de captura e processamento das imagens.

---

## Testes Qualitativos

Os testes qualitativos consistem na análise visual dos modelos 3D gerados sob diferentes configurações. Um mesmo objeto foi reconstruído em diferentes cenários, variando os parâmetros de entrada e processamento.

Os experimentos variaram em relação a:

- Uso de remoção de fundo
- Aplicação de pré-processamento de imagem
- Quantidade de imagens utilizadas
- Resolução das imagens
- Tipos de objetos

A avaliação foi baseada nos seguintes critérios:

- **Integridade:** continuidade da malha gerada  
- **Reconhecimento do objeto:** facilidade de identificação do objeto real no modelo  
- **Formato geométrico:** fidelidade da geometria em relação ao objeto real  
- **Ruído:** presença de elementos espúrios na reconstrução  

Os resultados foram classificados em uma escala de 0 a 10, variando de “Péssimo” a “Excelente”.

<img width="134" height="130" alt="image" src="https://github.com/user-attachments/assets/bd981c48-2912-4c21-96fd-9a0d850fff81" />

---

## Testes Quantitativos

Os testes quantitativos consistem na comparação entre dimensões reais dos objetos físicos e as medidas obtidas nos modelos 3D reconstruídos.

Para isso, foi utilizada medição manual das dimensões reais e comparação com distâncias extraídas diretamente dos modelos 3D, permitindo estimar a precisão geométrica e o erro de escala das reconstruções.

---

## Principais Observações nos Testes Realizados

- Objetos com alta textura apresentam melhores resultados
- Objetos com baixa textura apresentam limitações
- A quantidade de imagens impacta diretamente a qualidade
- A resolução das imagens influencia o nível de detalhe
- Erros geométricos entre 0% e ~10%

---

## Resultados

- Pipeline completo implementado e automatizado  
- Aplicação web funcional com suporte a upload de imagens, acompanhamento em tempo real da execução, visualização e exportação de modelos 3D  
- Geração de modelos 3D com boa qualidade geométrica

---

## Principais Fontes Consultadas

- SZELISKI, R. – Computer Vision: Algorithms and Applications
- HARTLEY, R.; ZISSERMAN, A. – Multiple View Geometry in Computer Vision
- SCHÖNBERGER, J. – COLMAP
- LOWE, D. G. – SIFT
- FISCHLER, M.; BOLLES, R. – RANSAC
- FURUKAWA, Y.; HERNÁNDEZ, C. – Multi-View Stereo
- KAZHDAN, M.; HOPPE, H. – Poisson Surface Reconstruction
- ZHOU, Q.-Y.; PARK, J.; KOLTUN, V. – Open3D

---

## Tecnologias Utilizadas

### Frontend

- **HTML**
- **CSS**
- **JavaScript**


### Backend

- **Python 3.10**
- **Flask**


### Reconstrução 3D

- **PyCOLMAP**
- **Open3D**


### Processamento de Imagem

- **OpenCV**
- **NumPy**
- **Pillow (PIL)**
- **rembg**


### Manipulação 3D

- **Open3D**
- **Trimesh**

<img width="438" height="420" alt="image" src="https://github.com/user-attachments/assets/e35cf57b-73f8-4c25-ac50-b0908e90f625" />

---

## Como Executar (Sistema Operacional usado: Linux - Ubuntu)

1. Certifique-se de ter o Python 3.10 instalado

2. Clone o repositório e acesse-o:

```bash
git clone https://github.com/dcamargoo/triform.git
cd triform
```

3. Crie o ambiente virtual (venv) e acesse-o:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Instale os requisitos:

```bash
pip install -r requirements.txt
```

5. Execute a aplicação:

```bash
flask run
```

---

## Imagens da Aplicação Web

### 1. Interface Inicial

<img width="1861" height="1047" alt="image" src="https://github.com/user-attachments/assets/0584f051-37d9-413a-a849-3d92ac40125f" />

### 2. Upload das Imagens

<img width="1861" height="1047" alt="image" src="https://github.com/user-attachments/assets/78095fe2-8a91-40ee-930c-a4f70a3f4e8c" />

### 3. Acompanhamento em Tempo Real

<img width="1861" height="1047" alt="image" src="https://github.com/user-attachments/assets/56e68545-2039-4369-b08c-2120b8fd456f" />

### 4. Visualização do Modelo 3D Gerado

<img width="1861" height="1047" alt="image" src="https://github.com/user-attachments/assets/8f7e1ecf-896a-41ea-b89e-6b27e505720b" /> 
