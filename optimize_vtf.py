from io import BytesIO
from pathlib import Path

from PIL import Image
from srctools.vtf import ImageFormats, VTF

INPUT = Path("Input")
OUTPUT = Path("Output")

INPUT.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

for src in INPUT.glob("*.vtf"):
    src_vtf = VTF.read(BytesIO(src.read_bytes()))
    img = src_vtf.get().to_PIL().convert("RGBA")
    img = img.resize((max(1, img.width // 2), max(1, img.height // 2)), Image.Resampling.LANCZOS)

    if img.width % 4 or img.height % 4:
        fmt = ImageFormats.RGBA8888
    elif img.getchannel("A").getextrema() != (255, 255):
        fmt = ImageFormats.DXT5
    else:
        fmt = ImageFormats.DXT1

    thumb = ImageFormats.DXT1 if fmt != ImageFormats.RGBA8888 else ImageFormats.RGBA8888
    out = VTF(img.width, img.height, flags=src_vtf.flags, fmt=fmt, thumb_fmt=thumb)
    out.get().copy_from(img.tobytes(), ImageFormats.RGBA8888)

    dst = OUTPUT / src.name
    with dst.open("wb") as f:
        out.save(f)

    print(f"{src.name}: {src_vtf.width}x{src_vtf.height} -> {img.width}x{img.height} ({fmt.name})")
