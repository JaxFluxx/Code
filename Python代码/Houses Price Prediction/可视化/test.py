#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render equations found in an image (PNG/JPG/HEIC) into clean PNGs, or from a text list.

Usage:
  # OCR from image
  python render_equations_from_image.py --image /path/to/IMG.png --outdir formulas_out

  # Directly from a text file (one formula per line, LaTeX snippets allowed)
  python render_equations_from_image.py --formulas-txt formulas.txt --outdir formulas_out

Notes:
- HEIC support requires either `pillow-heif` or `pyheif`. If those aren't installed,
  please convert HEIC to PNG/JPG first (e.g., using your Photos app or `magick convert`).
- OCR uses `pytesseract`; if it's not installed, the script will fall back to placeholder formulas.
- Rendering uses matplotlib's mathtext, so inline LaTeX is supported inside $...$ (this script wraps for you).
"""

import argparse
from pathlib import Path

FALLBACK_FORMULAS = [
    r"C_{final} = U \cdot \min(C_{peak}, B \cdot OI) \cdot \left(1 - \frac{T_{overhead}}{T_{total}}\right)",
    r"R(t) = 1 - P_{\mathrm{TERMINAL}}(t)"
]

def load_image(image_path: Path):
    """Try several backends to load PNG/JPG/HEIC into a PIL.Image.Image."""
    from PIL import Image
    # Try pillow_heif
    try:
        import pillow_heif
        heif_file = pillow_heif.read_heif(str(image_path))
        return Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
    except Exception:
        pass
    # Try pyheif
    try:
        import pyheif
        heif_file = pyheif.read(str(image_path))
        return Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode)
    except Exception:
        pass
    # Try imageio
    try:
        import imageio.v3 as iio
        arr = iio.imread(str(image_path))
        return Image.fromarray(arr)
    except Exception:
        pass
    # Fallback to PIL open (works for png/jpg)
    try:
        return Image.open(str(image_path))
    except Exception as e:
        raise RuntimeError(f"Failed to open image: {e}")

def is_formula_like(line: str) -> bool:
    """Heuristic filter: keep lines that 'look like' equations."""
    line_norm = (line or "").strip()
    if not line_norm:
        return False
    tokens = ["=", "≈", "~", "∝", "≤", "≥", "→", "←", "∑", "∫", "d/dt", "min(", "max(", "/", "λ", "μ"]
    return any(tok in line_norm for tok in tokens)

def normalize_for_latex(s: str) -> str:
    """Normalize common unicode/math OCR artifacts for matplotlib mathtext."""
    if not s:
        return s
    s = s.replace("−", "-").replace("—", "-")
    s = s.replace("·", "*").replace("×", "*").replace("⋅", "*").replace("∗", "*")
    s = s.replace("≤", r"\le").replace("≥", r"\ge")
    s = s.replace("∑", r"\sum").replace("∫", r"\int")
    s = s.replace("∞", r"\infty")
    s = s.replace("→", r"\to").replace("←", r"\leftarrow")
    # Greek letters
    s = s.replace("λ", r"\lambda").replace("μ", r"\mu")
    # Common functions
    s = s.replace("min(", r"\min(").replace("max(", r"\max(")
    # Trim
    return s.strip()

def render_formulas_to_png(formulas, out_dir: Path, dpi=220, fontsize=22, transparent=True):
    """Render each formula to PNG, and also create a stacked sheet."""
    from matplotlib import pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    rendered_paths = []

    # Per-formula images
    for i, eq in enumerate(formulas, start=1):
        tex = f"${eq}$"
        fig = plt.figure(figsize=(8, 2), dpi=dpi)
        if transparent:
            fig.patch.set_alpha(0.0)
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.5, tex, ha="center", va="center", fontsize=fontsize)
        out_path = out_dir / f"equation_{i:02d}.png"
        plt.savefig(out_path, bbox_inches="tight", pad_inches=0.2, transparent=transparent)
        plt.close(fig)
        rendered_paths.append(out_path)

    # Stacked sheet
    if formulas:
        fig = plt.figure(figsize=(10, max(2, 2 * len(formulas))), dpi=dpi)
        if transparent:
            fig.patch.set_alpha(0.0)
        ax = fig.add_subplot(111)
        ax.axis("off")
        y_positions = list(reversed([(i + 1) / (len(formulas) + 1) for i in range(len(formulas))]))
        for y, eq in zip(y_positions, formulas):
            tex = f"${eq}$"
            ax.text(0.5, y, tex, ha="center", va="center", fontsize=fontsize)
        sheet_path = out_dir / "equation_sheet.png"
        plt.savefig(sheet_path, bbox_inches="tight", pad_inches=0.5, transparent=transparent)
        plt.close(fig)
    else:
        sheet_path = None

    return rendered_paths, (out_dir / "equation_sheet.png" if formulas else None)

def read_formulas_from_txt(txt_path: Path):
    """Read formulas (one per line). Lines starting with # are treated as comments."""
    lines = txt_path.read_text(encoding="utf-8").splitlines()
    items = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        items.append(ln)
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", help="Path to image containing equations (PNG/JPG/HEIC)")
    ap.add_argument("--formulas-txt", help="Path to a text file: one formula per line (LaTeX snippets allowed)")
    ap.add_argument("--outdir", default="formulas_out", help="Output directory")
    ap.add_argument("--dpi", type=int, default=220, help="PNG DPI")
    ap.add_argument("--fontsize", type=int, default=22, help="Font size for mathtext rendering")
    ap.add_argument("--no-transparent", action="store_true", help="Disable transparent background")
    args = ap.parse_args()

    out_dir = Path(args.outdir)
    transparent = not args.no_transparent

    formulas = []

    if args.formulas_txt:
        # Directly from txt (skip OCR)
        txt_path = Path(args.formulas_txt)
        if not txt_path.exists():
            raise FileNotFoundError(f"Formulas file not found: {txt_path}")
        raw = read_formulas_from_txt(txt_path)
        formulas = [normalize_for_latex(s) for s in raw if s.strip()]
    elif args.image:
        # OCR from image
        img_path = Path(args.image)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {img_path}")

        try:
            img = load_image(img_path)
        except Exception as e:
            print(f"[WARN] Image load failed: {e}")
            img = None

        ocr_text = ""
        if img is not None:
            try:
                import pytesseract
                # You can tune lang / psm / oem if needed:
                # config = "--psm 6"
                # ocr_text = pytesseract.image_to_string(img, lang="eng", config=config)
                ocr_text = pytesseract.image_to_string(img, lang="eng")
            except Exception as e:
                print(f"[WARN] pytesseract not available or OCR failed: {e}")

        if ocr_text:
            lines = ocr_text.splitlines()
            eq_lines = [ln for ln in lines if is_formula_like(ln)]
            formulas = [normalize_for_latex(ln) for ln in eq_lines if ln.strip()]

            # Save a record
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "recognized_formulas.txt").write_text(
                "# Original OCR lines (equation-like)\n" +
                "\n".join(eq_lines) +
                "\n\n# Normalized LaTeX-like formulas\n" +
                "\n".join(formulas),
                encoding="utf-8"
            )
        else:
            print("[INFO] No OCR text produced. Using FALLBACK_FORMULAS.")
            formulas = FALLBACK_FORMULAS[:]
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "recognized_formulas.txt").write_text(
                "# OCR failed or found no formulas. Using FALLBACK_FORMULAS.\n\n" +
                "\n".join(formulas),
                encoding="utf-8"
            )
    else:
        raise ValueError("Please provide either --image or --formulas-txt.")

    # Render
    rendered_paths, sheet_path = render_formulas_to_png(
        formulas, out_dir, dpi=args.dpi, fontsize=args.fontsize, transparent=transparent
    )

    print("\nDone. Outputs saved to:", out_dir)
    print("Per-formula PNGs:")
    for p in rendered_paths:
        print(" -", p)
    if sheet_path and sheet_path.exists():
        print("Equation sheet:", sheet_path)

if __name__ == "__main__":
    main()
