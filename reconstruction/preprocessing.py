import cv2
import numpy as np
from PIL import Image
import rembg
from pathlib import Path

# reduzir resolução da imagem se necessário
def resize_if_needed(image, max_dimension=1600):
    h, w = image.shape[:2]

    max_current = max(h, w)

    if max_current > max_dimension:
        scale = max_dimension / max_current
        resized = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )
        return resized

    return image.copy()

# aplicar correção de branco usando o espaço de cor LAB
def apply_white_balance(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)

    avg_a = np.mean(A)
    avg_b = np.mean(B)

    A = A - (avg_a - 128) * (L / 255.0)
    B = B - (avg_b - 128) * (L / 255.0)

    corrected = cv2.merge((L, A, B))
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)

    return cv2.cvtColor(corrected, cv2.COLOR_LAB2BGR)

# aplicar filtro bilateral para suavizar a imagem sem perder detalhes
def apply_bilateral_filter(image):
    return cv2.bilateralFilter(image, d=9, sigmaColor=25, sigmaSpace=25)

# aplicar CLAHE para melhorar o contraste local da imagem
def apply_color_clahe(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)

    merged = cv2.merge((l_enhanced, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

# usar rembg para remover o fundo da imagem
def remove_background(input_path, output_path):
    image = Image.open(input_path)
    result = rembg.remove(image)
    result.save(output_path)

VALID_STRATEGIES = {
    "com_fundo",
    "com_fundo_cinza",
    "sem_fundo",
    "sem_fundo_cinza"
}

# função principal de preprocessamento que aplica as transformações e salva a imagem resultante
def preprocess_image(input_path, output_base_dir, strategy):

    if strategy not in VALID_STRATEGIES:
        raise ValueError("Estratégia de preprocessamento inválida")

    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Não foi possível carregar a imagem: {input_path}")

    base_output_dir = Path(output_base_dir)
    strategy_dir = base_output_dir / strategy
    strategy_dir.mkdir(parents=True, exist_ok=True)

    file_stem = Path(input_path).stem
    png_name = file_stem + ".png"

    resized = resize_if_needed(image)
    white_balanced = apply_white_balance(resized)
    filtered = apply_bilateral_filter(white_balanced)
    enhanced = apply_color_clahe(filtered)

    if strategy == "com_fundo":

        output_path = strategy_dir / png_name
        cv2.imwrite(str(output_path), enhanced)

    elif strategy == "com_fundo_cinza":

        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        output_path = strategy_dir / f"{file_stem}_cinza.png"
        cv2.imwrite(str(output_path), gray)

    elif strategy == "sem_fundo":

        temp_path = strategy_dir / f"{file_stem}_temp.png"
        cv2.imwrite(str(temp_path), enhanced)

        output_path = strategy_dir / f"{file_stem}_sem_fundo.png"
        remove_background(str(temp_path), str(output_path))

        temp_path.unlink()

    elif strategy == "sem_fundo_cinza":

        temp_path = strategy_dir / f"{file_stem}_temp.png"
        cv2.imwrite(str(temp_path), enhanced)

        nobg_path = strategy_dir / f"{file_stem}_sem_fundo.png"
        remove_background(str(temp_path), str(nobg_path))

        nobg_img = cv2.imread(str(nobg_path), cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(nobg_img, cv2.COLOR_BGR2GRAY)

        output_path = strategy_dir / f"{file_stem}_cinza_sem_fundo.png"
        cv2.imwrite(str(output_path), gray)

        temp_path.unlink()
        nobg_path.unlink()

    print(f"[PREPROCESSAMENTO] {strategy} → {output_path}")