#!/usr/bin/env python3
import sys
import os
from typing import Tuple

try:
	import cv2
	import numpy as np
	from PIL import Image, ImageEnhance, ImageFilter
except Exception as exc:
	print("Missing dependencies. Install with: pip install pillow opencv-python numpy", file=sys.stderr)
	raise


def _save(image: Image.Image, path: str) -> None:
	image.save(path, format="PNG", optimize=True)
	print(f"Wrote: {path}")


def _to_pil(arr: np.ndarray) -> Image.Image:
	# BGR to RGB
	rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
	return Image.fromarray(rgb)


def _to_cv(img: Image.Image) -> np.ndarray:
	arr = np.array(img.convert("RGB"))
	return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _apply_glow(pil_img: Image.Image, color=(246, 216, 144), strength: float = 0.35, blur_radius: int = 6) -> Image.Image:
	glow = pil_img.convert("RGB").copy()
	# colorize by overlay
	overlay = Image.new("RGB", glow.size, color)
	glow = Image.blend(glow, overlay, 0.18)
	glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
	return Image.blend(pil_img, glow, strength)


def enhance(input_path: str, prefix: str) -> None:
	orig_cv = cv2.imread(input_path, cv2.IMREAD_COLOR)
	if orig_cv is None:
		raise FileNotFoundError(f"Cannot read image: {input_path}")

	# Core pipeline: upscale slightly for cleaner ops
	h, w = orig_cv.shape[:2]
	scale = 1.6
	resized = cv2.resize(orig_cv, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)

	# Local contrast via CLAHE
	lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
	l, a, b = cv2.split(lab)
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
	l = clahe.apply(l)
	lab = cv2.merge([l, a, b])
	resized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

	# Gentle global contrast with sigmoid-like curve using LUT
	x = np.arange(256, dtype=np.float32)
	lut = (1 / (1 + np.exp(-0.06 * (x - 128))) - 1 / (1 + np.exp(0.06 * 128)))
	lut = lut / (lut.max() - lut.min()) * 255.0
	lut = lut.clip(0, 255).astype(np.uint8)
	resized = cv2.LUT(resized, lut)

	# Unsharp masking
	blur = cv2.GaussianBlur(resized, (0, 0), sigmaX=1.2)
	sharpened = cv2.addWeighted(resized, 1.0 + 0.8, blur, -0.8, 0)

	# Convert to PIL for color warmth/saturation and glow
	pil = _to_pil(sharpened)
	pil = ImageEnhance.Color(pil).enhance(1.18)
	pil = ImageEnhance.Brightness(pil).enhance(1.02)
	enhanced = _apply_glow(pil, color=(246, 216, 144), strength=0.30, blur_radius=5)

	# Downscale back
	enhanced = enhanced.resize((w, h), Image.LANCZOS)
	_save(enhanced, f"{prefix}_enhanced.png")

	# Vivid variant
	pil_vivid = ImageEnhance.Color(pil).enhance(1.08)
	vivid = _apply_glow(pil_vivid, color=(255, 212, 122), strength=0.40, blur_radius=6)
	vivid = vivid.resize((w, h), Image.LANCZOS)
	_save(vivid, f"{prefix}_vivid.png")

	# Subtle variant
	pil_subtle = ImageEnhance.Color(pil).enhance(1.08)
	subtle = pil_subtle.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=2))
	subtle = subtle.resize((w, h), Image.LANCZOS)
	_save(subtle, f"{prefix}_subtle.png")


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print(f"Usage: {os.path.basename(sys.argv[0])} INPUT_IMAGE [OUTPUT_PREFIX]", file=sys.stderr)
		sys.exit(1)
	input_image = sys.argv[1]
	if not os.path.isfile(input_image):
		raise SystemExit(f"Input file not found: {input_image}")
	base = os.path.splitext(os.path.basename(input_image))[0]
	out_prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(input_image), base)
	enhance(input_image, out_prefix)