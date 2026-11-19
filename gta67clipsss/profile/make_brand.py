import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
def font(sz):
    try: return ImageFont.truetype(F, sz)
    except OSError: return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", sz)
STOPS = [(0.0, (40, 10, 80)), (0.45, (190, 30, 140)), (0.75, (255, 90, 90)), (1.0, (255, 170, 60))]
def grad(w, h):
    img = Image.new("RGB", (w, h)); px = img.load()
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(STOPS) - 1):
            if STOPS[i][0] <= t <= STOPS[i + 1][0]:
                a, b = STOPS[i], STOPS[i + 1]; u = (t - a[0]) / (b[0] - a[0]); break
        c = tuple(int(a[1][k] + (b[1][k] - a[1][k]) * u) for k in range(3))
        for x in range(w): px[x, y] = c
    return img
def sun_and_grid(img, cx, cy, r, horizon):
    d = ImageDraw.Draw(img, "RGBA"); w, h = img.size
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 210, 90, 235))
    for k in range(6):  # retro sun stripes
        yy = cy + r * (0.15 + k * 0.15)
        d.rectangle([cx - r, yy, cx + r, yy + r * 0.05 * (k + 1)], fill=STOPS[2][1] + (255,))
    d.rectangle([0, horizon, w, h], fill=(25, 5, 50, 255))
    for k in range(1, 14):
        yy = horizon + (h - horizon) * (k / 13) ** 1.8
        d.line([0, yy, w, yy], fill=(255, 60, 200, 200), width=max(1, w // 400))
    for k in range(-12, 13):
        d.line([cx, horizon, cx + k * w / 6, h], fill=(255, 60, 200, 200), width=max(1, w // 400))
def text_c(img, xy, s, sz, fill=(255, 255, 255), stroke=0.06):
    d = ImageDraw.Draw(img); f = font(sz); sw = max(2, int(sz * stroke))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).text(xy, s, font=f, anchor="mm", fill=(255, 40, 180, 255), stroke_width=sw * 3, stroke_fill=(255, 40, 180, 255))
    img.paste(glow.filter(ImageFilter.GaussianBlur(sz / 10)), (0, 0), glow.filter(ImageFilter.GaussianBlur(sz / 10)))
    d.text(xy, s, font=f, anchor="mm", fill=fill, stroke_width=sw, stroke_fill=(20, 0, 40))
# avatar 1080x1080, everything inside the centre circle
A = grad(1080, 1080); sun_and_grid(A, 540, 520, 300, 700)
text_c(A, (540, 470), "67", 430); text_c(A, (540, 760), "CLIPS", 150, fill=(255, 235, 120))
A.save("/home/user/GTA-6/gta67clipsss/profile/avatar.png")
# YouTube banner 2560x1440, text inside the 1546x423 safe area
B = grad(2560, 1440); sun_and_grid(B, 1280, 640, 360, 860)
text_c(B, (1280, 670), "GTA67CLIPSSS", 165); text_c(B, (1280, 815), "GTA 6 streamer reactions · new clips daily", 64, fill=(255, 235, 120), stroke=0.08)
B.save("/home/user/GTA-6/gta67clipsss/profile/youtube_banner.png")
# preview with YouTube safe-area and circle crop marks (for checking only)
p = A.copy(); m = Image.new("L", p.size, 0); ImageDraw.Draw(m).ellipse([0, 0, 1080, 1080], fill=255)
bg = Image.new("RGB", p.size, (255, 255, 255)); bg.paste(p, (0, 0), m); bg.resize((360, 360)).save("/tmp/claude-0/avatar_circle.png")
q = B.copy(); ImageDraw.Draw(q).rectangle([507, 508, 2053, 931], outline=(0, 255, 0), width=6); q.resize((1280, 720)).save("/tmp/claude-0/banner_check.png")
