import math
from PIL import Image, ImageDraw

SIZES = [16, 32, 48, 64, 128, 256]

def draw_clock(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = size // 2
    r = size // 2 - 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#cc0000", width=max(1, size // 20))
    draw.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], fill="#0f0000")
    for angle in range(0, 360, 30):
        rad = math.radians(angle - 90)
        outer = r - max(2, size // 24)
        thick = 3 if angle % 90 == 0 else 1
        inner = r - max(6, size // 8) if angle % 90 == 0 else r - max(4, size // 14)
        x1 = cx + int(inner * math.cos(rad))
        y1 = cy + int(inner * math.sin(rad))
        x2 = cx + int(outer * math.cos(rad))
        y2 = cy + int(outer * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill="#cc0000", width=thick)
    ha = math.radians(-60)
    hl = r // 2
    draw.line([cx, cy, cx + int(hl * math.cos(ha)), cy + int(hl * math.sin(ha))], fill="#cc0000", width=max(2, size // 12))
    ma = math.radians(30)
    ml = int(r * 0.65)
    draw.line([cx, cy, cx + int(ml * math.cos(ma)), cy + int(ml * math.sin(ma))], fill="#cc0000", width=max(1, size // 18))
    dr = max(2, size // 22)
    draw.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill="#cc0000")
    return img

frames = [draw_clock(s) for s in SIZES]
frames[0].save("resources/clock.ico", format="ICO", sizes=[(s, s) for s in SIZES], append_images=frames[1:])
frames[-1].save("resources/clock.png", format="PNG")
print("Saved clock.ico and clock.png")
