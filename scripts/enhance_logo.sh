#!/usr/bin/env bash
set -euo pipefail

# enhance_logo.sh – Tasteful logo enhancement for elegance + pop
# Usage: enhance_logo.sh INPUT_IMAGE [OUTPUT_PREFIX]
# Requires: ImageMagick (magick or convert)

if [[ $# -lt 1 ]]; then
	echo "Usage: $(basename "$0") INPUT_IMAGE [OUTPUT_PREFIX]" >&2
	exit 1
fi

INPUT="$1"
if [[ ! -f "$INPUT" ]]; then
	echo "Input file not found: $INPUT" >&2
	exit 1
fi

BASENAME_NOEXT=$(basename "${INPUT%.*}")
DIRNAME=$(dirname "$INPUT")
PREFIX_DEFAULT="${DIRNAME}/${BASENAME_NOEXT}"
PREFIX="${2:-$PREFIX_DEFAULT}"

# Prefer IM7's 'magick' if available; fallback to 'convert'
if command -v magick >/dev/null 2>&1; then
	IM_BIN="magick"
else
	IM_BIN="convert"
fi

main_out="${PREFIX}_enhanced.png"
vivid_out="${PREFIX}_vivid.png"
subtle_out="${PREFIX}_subtle.png"

# Core enhancement: local contrast, gentle sharpen, warm bronze pop, soft highlight glow
# - Resize up slightly for cleaner sharpening then scale back
# - Sigmoidal contrast avoids clipping; CLAHE adds local contrast
# - Modulate bumps brightness/saturation mildly
# - Screened blurred clone adds a tasteful glow
"$IM_BIN" "$INPUT" \
	-colorspace sRGB \
	-filter Lanczos -resize 160% \
	-clahe 25x25+128+2 \
	-sigmoidal-contrast 6,50% \
	-unsharp 0x1.2+0.8+0.02 \
	-channel RGB -modulate 102,118,100 +channel \
	( +clone -fill "#f6d890" -colorize 12 -blur 0x5 -level 15%,85% ) \
	-compose screen -composite \
	-filter Lanczos -resize 100% \
	-strip "$main_out"

echo "Wrote: $main_out"

# Vivid option: a touch more saturation/contrast and stronger glow for eye-catching thumbnails
"$IM_BIN" "$INPUT" \
	-colorspace sRGB \
	-filter Lanczos -resize 170% \
	-clahe 20x20+128+2 \
	-sigmoidal-contrast 8,50% \
	-unsharp 0x1.4+1.0+0.02 \
	-channel RGB -modulate 103,128,100 +channel \
	( +clone -fill "#ffd47a" -colorize 16 -blur 0x6 -level 10%,90% ) \
	-compose screen -composite \
	-filter Lanczos -resize 100% \
	-strip "$vivid_out"

echo "Wrote: $vivid_out"

# Subtle option: minimal changes for maximum elegance
"$IM_BIN" "$INPUT" \
	-colorspace sRGB \
	-filter Lanczos -resize 150% \
	-sigmoidal-contrast 4,50% \
	-unsharp 0x1.0+0.6+0.01 \
	-channel RGB -modulate 101,108,100 +channel \
	-filter Lanczos -resize 100% \
	-strip "$subtle_out"

echo "Wrote: $subtle_out"

cat <<'INFO'

Tips:
- Use "_subtle" for print or formal contexts; "_vivid" for thumbnails/social; "_enhanced" is a balanced default.
- For a transparent background version (if your input is on white), try:
    magick INPUT -fuzz 6% -alpha off -transparent white OUTPUT_transparent.png
- To tweak warmth: increase/decrease the second value in -modulate (saturation).
INFO