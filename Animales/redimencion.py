import argparse
from pathlib import Path
from PIL import Image
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Redimensiona imágenes y preserva árbol de carpetas")
    p.add_argument("--src", default=str(Path(__file__).resolve().parent / "AnimalesDataset"),
                   help="Directorio origen")
    p.add_argument("--dst", default=str(Path(__file__).resolve().parent / "redimencionDataset"),
                   help="Directorio destino")
    p.add_argument("--height", type=int, default=28, help="Alto objetivo (px)")
    p.add_argument("--width", type=int, default=28, help="Ancho objetivo (px)")
    p.add_argument("--ext", default="jpg,jpeg,png,bmp,tiff,webp", help="Extensiones a procesar")
    p.add_argument("--overwrite", action="store_true", help="Sobrescribir archivos existentes en destino")
    return p.parse_args()


def ensure_dir(p: Path):
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)


def process_image(src_path: Path, dst_path: Path, size):
    try:
        with Image.open(src_path) as im:
            # convertir a RGB (grises -> RGB, RGBA -> RGB descartando alpha)
            im = im.convert("RGB")
            # Pillow resize recibe (width, height)
            im_resized = im.resize((size[1], size[0]), Image.LANCZOS)
            ensure_dir(dst_path.parent)
            # guardar con la misma extensión
            im_resized.save(dst_path)
            return True
    except Exception as e:
        print(f"ERROR procesando {src_path}: {e}")
        return False


def main():
    args = parse_args()
    src = Path(args.src)
    dst = Path(args.dst)
    h = int(args.height)
    w = int(args.width)
    exts = [e.strip().lower() for e in args.ext.split(",") if e.strip()]

    if not src.exists():
        print(f"Directorio fuente no existe: {src}")
        sys.exit(1)

    total = 0
    processed = 0
    skipped = 0
    failed = 0

    # Iterar por subcarpetas (clases) y renombrar archivos según la clase: <clase>_<i>.<ext>
    for class_dir in sorted([p for p in src.iterdir() if p.is_dir()]):
        class_name = class_dir.name
        counter = 0
        for file in sorted(class_dir.iterdir()):
            if not file.is_file():
                continue
            if file.suffix.lower().lstrip(".") not in exts:
                skipped += 1
                continue

            total += 1
            suffix = file.suffix.lower()
            # construir nuevo nombre: clase_indice.ext
            new_name = f"{class_name}_{counter}{suffix}"
            target_file = dst / class_name / new_name

            if target_file.exists() and not args.overwrite:
                skipped += 1
                counter += 1
                continue

            ensure_dir(target_file.parent)
            ok = process_image(file, target_file, (h, w))
            if ok:
                processed += 1
            else:
                failed += 1
            counter += 1

    # También procesar archivos sueltos en la raíz de src (si los hay)
    for file in sorted(src.iterdir()):
        if file.is_file() and file.suffix.lower().lstrip('.') in exts:
            total += 1
            # usar nombre basado en archivo original
            target_file = dst / file.name
            if target_file.exists() and not args.overwrite:
                skipped += 1
                continue
            ensure_dir(target_file.parent)
            ok = process_image(file, target_file, (h, w))
            if ok:
                processed += 1
            else:
                failed += 1

    print("\nResumen:")
    print(f"Total encontrados: {total}")
    print(f"Procesados: {processed}")
    print(f"Saltados (existente): {skipped}")
    print(f"Fallidos: {failed}")
    print(f"Salida en: {dst}")


if __name__ == '__main__':
    main()
