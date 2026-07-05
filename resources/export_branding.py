import math, os
from PIL import Image, ImageDraw, ImageFont

OUT = "resources/branding"
os.makedirs(OUT, exist_ok=True)

def draw_clock(size, border_ratio=0.08):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = size // 2
    r = size // 2 - max(2, int(size * border_ratio))
    lw = max(1, size // 22)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#cc0000", width=lw)
    draw.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], fill="#0f0000")
    for angle in range(0, 360, 30):
        rad = math.radians(angle - 90)
        outer = r - max(2, size // 28)
        thick = max(2, lw + 1) if angle % 90 == 0 else max(1, lw // 2)
        inner = r - max(6, size // 7) if angle % 90 == 0 else r - max(4, size // 12)
        x1 = cx + int(inner * math.cos(rad))
        y1 = cy + int(inner * math.sin(rad))
        x2 = cx + int(outer * math.cos(rad))
        y2 = cy + int(outer * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill="#cc0000", width=thick)
    ha = math.radians(-60)
    hl = r // 2
    draw.line([cx, cy, cx + int(hl * math.cos(ha)), cy + int(hl * math.sin(ha))], fill="#cc0000", width=max(2, size // 14))
    ma = math.radians(30)
    ml = int(r * 0.65)
    draw.line([cx, cy, cx + int(ml * math.cos(ma)), cy + int(ml * math.sin(ma))], fill="#cc0000", width=max(1, size // 20))
    dr = max(2, size // 24)
    draw.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill="#cc0000")
    return img

def draw_banner(w, h):
    img = Image.new("RGBA", (w, h), (10, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    cs = int(h * 0.6)
    clock = draw_clock(cs)
    ox = int(w * 0.15)
    oy = (h - cs) // 2
    img.paste(clock, (ox, oy), clock)
    try:
        font = ImageFont.truetype("segoeuib.ttf", int(h * 0.18))
    except:
        font = ImageFont.load_default()
    draw.text((int(w * 0.38), int(h * 0.30)), "DevTrack", fill="#cc0000", font=font)
    try:
        font2 = ImageFont.truetype("segoeui.ttf", int(h * 0.07))
    except:
        font2 = ImageFont.load_default()
    draw.text((int(w * 0.38), int(h * 0.55)), "Development Activity Tracker", fill="#884444", font=font2)
    draw.text((int(w * 0.38), int(h * 0.66)), "Track your focus. Own your time.", fill="#555555", font=font2)
    return img

for name, sz in {"logo_512.png":512,"logo_256.png":256,"logo_192.png":192,"logo_180.png":180,"logo_152.png":152,"logo_144.png":144,"logo_128.png":128,"logo_96.png":96,"logo_72.png":72,"logo_64.png":64,"logo_48.png":48,"logo_32.png":32,"logo_16.png":16}.items():
    draw_clock(sz).save(os.path.join(OUT, name))

for name, (w,h) in {"banner_social_1200x630.png":(1200,630),"banner_twitter_1024x500.png":(1024,500),"banner_presentation_800x600.png":(800,600),"banner_thumbnail_400x300.png":(400,300)}.items():
    draw_banner(w,h).save(os.path.join(OUT, name))

print(f"Assets saved to: {OUT}")
