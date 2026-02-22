import cv2
import numpy as np
from PIL import Image
import rembg
from pathlib import Path

# Correção de Balanço de Branco
def white_balance(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)
    avg_a = np.mean(A)
    avg_b = np.mean(B)
    A = A - (avg_a - 128) * (L / 255.0)
    B = B - (avg_b - 128) * (L / 255.0)
    lab_corrigido = cv2.merge((L, A, B))
    lab_corrigido = np.clip(lab_corrigido, 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab_corrigido, cv2.COLOR_LAB2BGR)

# Filtro bilateral
def aplicar_bilateral(img):
    return cv2.bilateralFilter(img, d=15, sigmaColor=50, sigmaSpace=50)

# CLAHE colorido
def aplicar_clahe_colorido(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    lab_clahe = cv2.merge((l2, a, b))
    return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

# Remover fundo
def remover_fundo(caminho_entrada, caminho_saida):
    img = Image.open(caminho_entrada)
    resultado = rembg.remove(img)
    resultado.save(caminho_saida)

def preprocess_image(input_path, output_base_dir):
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Não foi possível abrir a imagem: {input_path}")

    output_base = Path(output_base_dir)
    dir_com_fundo = output_base / "com_fundo"
    dir_com_fundo_gray = output_base / "com_fundo_cinza"
    dir_sem_fundo = output_base / "sem_fundo"
    dir_sem_fundo_gray = output_base / "sem_fundo_cinza"

    # cria pastas, se não existirem
    dir_com_fundo.mkdir(parents=True, exist_ok=True)
    dir_com_fundo_gray.mkdir(parents=True, exist_ok=True)
    dir_sem_fundo.mkdir(parents=True, exist_ok=True)
    dir_sem_fundo_gray.mkdir(parents=True, exist_ok=True)

    filename = Path(input_path).stem + ".png"

    # 1) Processamento de cor
    wb = white_balance(img)
    bilateral = aplicar_bilateral(wb)
    clahe = aplicar_clahe_colorido(bilateral)

    # salva com fundo original
    out_color = dir_com_fundo / filename
    cv2.imwrite(str(out_color), clahe)

    # converte para cinza com fundo original
    out_gray = dir_com_fundo_gray / filename
    gray = cv2.cvtColor(clahe, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(out_gray), gray)

    # 2) Remover fundo
    out_color_nofg = dir_sem_fundo / filename
    remover_fundo(str(out_color), str(out_color_nofg))

    # 3) Converte para cinza sem fundo
    out_gray_nofg = dir_sem_fundo_gray / filename
    img_final = cv2.imread(str(out_color_nofg))
    if img_final is not None:
        img_final_gray = cv2.cvtColor(img_final, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(str(out_gray_nofg), img_final_gray)

    print("[PREPROCESS] Arquivos gerados:")
    print(f" - Com fundo: {out_color}")
    print(f" - Com fundo cinza: {out_gray}")
    print(f" - Sem fundo: {out_color_nofg}")
    print(f" - Sem fundo cinza: {out_gray_nofg}")