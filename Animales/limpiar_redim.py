from pathlib import Path
from PIL import Image, UnidentifiedImageError
import argparse
import sys


def process_and_save(src: Path, dest: Path, target_size):
    """Abrir `src`, convertir/resize y guardar en `dest`. Devuelve (True, None) o (False, err)."""
    try:
        with Image.open(src) as im:
            im = im.convert('RGB')
            if im.size != target_size:
                im = im.resize(target_size, Image.LANCZOS)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # intentar mantener formato razonable
            try:
                if dest.suffix.lower() in ('.jpg', '.jpeg'):
                    im.save(dest, quality=95)
                else:
                    im.save(dest)
            except Exception:
                im.save(dest)
        return True, None
    except UnidentifiedImageError as e:
        return False, f"UnidentifiedImageError: {e}"
    except Exception as e:
        return False, str(e)


def parse_args():
    p = argparse.ArgumentParser(description='Limpiar y normalizar imágenes (escribe en carpeta limpia)')
    p.add_argument('--data-dir', type=str, default=None, help='Directorio raíz con subcarpetas por clase. Si se omite, busca "redimencionDataset" junto al script.')
    p.add_argument('--output-dir', type=str, default=None, help='Directorio donde se escribirán los datos limpios (por defecto <script>/redimencionDataset_clean)')
    p.add_argument('--width', type=int, default=28, help='Ancho objetivo (px).')
    p.add_argument('--height', type=int, default=28, help='Alto objetivo (px).')
    p.add_argument('--dry-run', action='store_true', help='No escribir archivos; solo listar acciones.')
    p.add_argument('--delete-corrupt', action='store_true', help='Eliminar archivos corruptos del dataset original si se detectan.')
    p.add_argument('--verbose', action='store_true', help='Mostrar mensajes detallados durante la ejecución.')
    p.add_argument('--exts', type=str, default='.jpg,.jpeg,.png,.bmp,.tiff,.webp', help='Extensiones a procesar, separadas por coma')
    return p.parse_args()


def main():
    args = parse_args()
    script_dir = Path(__file__).parent

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = script_dir.joinpath('redimencionDataset')

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = script_dir.joinpath(data_dir.name + '_limpio')

    exts = {e.strip().lower() if e.strip().startswith('.') else f'.{e.strip().lower()}' for e in args.exts.split(',')}
    target = (args.width, args.height)

    if args.verbose:
        print(f"Dataset origen: {data_dir}")
        print(f"Salida (limpios): {output_dir}")
        print(f"Tamaño objetivo: {target}; dry_run={args.dry_run}; delete_corrupt={args.delete_corrupt}")

    stats = {'checked': 0, 'processed': 0, 'skipped': 0, 'removed': 0, 'errors': 0}

    if not data_dir.exists() or not data_dir.is_dir():
        print(f"Error: data_dir {data_dir} no existe o no es un directorio.")
        return

    # recorrer clases y archivos, escribir en output_dir manteniendo la estructura
    for class_dir in sorted(data_dir.iterdir()):
        if not class_dir.is_dir():
            continue
        if args.verbose:
            print(f"Procesando clase: {class_dir.name}")
        for f in sorted(class_dir.iterdir()):
            if not f.is_file():
                continue
            if f.suffix.lower() not in exts:
                stats['skipped'] += 1
                continue

            stats['checked'] += 1
            rel = f.relative_to(data_dir)
            dest_path = output_dir.joinpath(rel)

            if args.dry_run:
                if args.verbose:
                    print(f"[DRY] Procesar: {f} -> {dest_path}")
                continue

            ok, err = process_and_save(f, dest_path, target)
            if ok:
                stats['processed'] += 1
            else:
                stats['errors'] += 1
                print(f" ERROR procesando {f}: {err}")
                if args.delete_corrupt:
                    try:
                        f.unlink()
                        stats['removed'] += 1
                        if args.verbose:
                            print(f"  Eliminado corrupto original: {f}")
                    except Exception as e:
                        print(f"  No se pudo eliminar {f}: {e}")

    print('\nResumen:')
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
