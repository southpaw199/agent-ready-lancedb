"""Create the sample images for task T4 of the LanceDB agent task review.

Usage: python make_sample_images.py TARGET_FOLDER

Creates TARGET_FOLDER/images/ with 12 shapes (circle, square, triangle in
red, green, blue, yellow) and TARGET_FOLDER/query.png, a smaller red circle
in a different position. Requires Pillow (pip install pillow).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 224
COLORS = {
    "red": (220, 30, 30),
    "green": (30, 160, 60),
    "blue": (30, 80, 220),
    "yellow": (240, 200, 20),
}


def draw(shape: str, color: tuple, box: tuple) -> Image.Image:
    image = Image.new("RGB", (SIZE, SIZE), "white")
    pen = ImageDraw.Draw(image)
    left, top, right, bottom = box
    if shape == "circle":
        pen.ellipse(box, fill=color)
    elif shape == "square":
        pen.rectangle(box, fill=color)
    elif shape == "triangle":
        pen.polygon([((left + right) / 2, top), (right, bottom), (left, bottom)], fill=color)
    return image


def main(target: Path) -> None:
    folder = target / "images"
    folder.mkdir(parents=True, exist_ok=True)
    for color_name, color in COLORS.items():
        for shape in ("circle", "square", "triangle"):
            draw(shape, color, (40, 40, 184, 184)).save(folder / f"{color_name}_{shape}.png")
    draw("circle", COLORS["red"], (70, 60, 170, 160)).save(target / "query.png")
    print(f"Created 12 images in {folder} and {target / 'query.png'}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
