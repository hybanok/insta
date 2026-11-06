import math, os, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
LOGO = "/mnt/user-data/uploads/LOGOPEQUEÑO.png"
OUT = "/mnt/user-data/outputs"
HANDLE = "@wod.cada.dia"
rng = np.random.default_rng(7)


def vgrad(w, h, top, bot):
    t = np.linspace(0, 1, max(h, 1))[:, None, None]
    arr = (np.array(top)[None, None, :] + (np.array(bot) - np.array(top))[None, None, :] * t) * np.ones((h, w, 1))
    return Image.fromarray(arr.astype("uint8"), "RGB")


def diag_grad(w, h, c1, c2):
    y, x = np.mgrid[0:h, 0:w]
    t = (((x / w) + (y / h)) / 2)[..., None]
    arr = np.array(c1) * (1 - t) + np.array(c2) * t
    return Image.fromarray(arr.astype("uint8"), "RGB")


def grain(img_rgb, sd=9):
    a = np.array(img_rgb).astype(float) + rng.normal(0, sd, (img_rgb.size[1], img_rgb.size[0], 1))
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"), "RGB")


def background():
    base = np.clip(np.full((H, W, 3), 14.0) + rng.normal(0, 7, (H, W, 1)), 0, 255)
    img = Image.fromarray(base.astype("uint8"), "RGB").convert("RGBA")
    streaks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(streaks)
    for _ in range(7):
        x0 = int(rng.integers(-200, W))
        d.line([(x0, 0), (x0 + H * 0.6, H)], fill=(255, 255, 255, int(rng.integers(5, 16))), width=int(rng.integers(3, 16)))
    return Image.alpha_composite(img, streaks.filter(ImageFilter.GaussianBlur(3)))


def bezier(p0, p1, p2, p3, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def gold_from_mask(mask, c1=(150, 108, 24), c2=(224, 178, 66)):
    fill = grain(diag_grad(W, H, c1, c2), 9).convert("RGBA")
    fill.putalpha(mask)
    return fill


def poly_mask(poly):
    S = 2
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in poly], fill=255)
    return m.resize((W, H), Image.LANCZOS)


def brush_blob_mask(cx, cy, rx, ry):
    S = 2
    m = Image.new("L", (W * S, H * S), 0)
    ph = rng.uniform(0, 6.28, 4)
    pts = []
    n = 260
    for i in range(n):
        th = 2 * math.pi * i / n
        r = 1 + 0.10 * math.sin(3 * th + ph[0]) + 0.07 * math.sin(5 * th + ph[1]) + 0.05 * math.sin(9 * th + ph[2]) + rng.normal(0, 0.02)
        edge = abs(math.cos(th))
        r += edge * 0.06 * math.sin(23 * th + ph[3]) + edge * rng.normal(0, 0.035)
        pts.append(((cx + rx * r * math.cos(th)) * S, (cy + ry * r * math.sin(th)) * S))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.resize((W, H), Image.LANCZOS)


def logo_cut(height):
    """Devuelve (tinta RGBA sin zonas blancas, silueta L) del logo, escalados a 'height'."""
    if not os.path.exists(LOGO):  # original no disponible: usar el recuperado (330 px de alto)
        return Image.open("/home/claude/brand/logo_ink.png"), Image.open("/home/claude/brand/logo_sil.png")
    im = Image.open(LOGO).convert("RGB")
    a = np.array(im).astype(float)
    near_white = a.min(axis=2) > 205
    try:
        from scipy import ndimage
        lab, _ = ndimage.label(near_white)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bg = np.isin(lab, list(border))
    except Exception:
        m = Image.fromarray((near_white * 255).astype("uint8"), "L")
        h, w = near_white.shape
        seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 40)] + [(x, h - 1) for x in range(0, w, 40)] + [(0, y) for y in range(0, h, 40)] + [(w - 1, y) for y in range(0, h, 40)]
        for sd in seeds:
            if m.getpixel(sd) == 255:
                ImageDraw.floodfill(m, sd, 128)
        bg = np.array(m) == 128
    sil = Image.fromarray(((~bg) * 255).astype("uint8"), "L")

    mn, mx, lum = a.min(axis=2), a.max(axis=2), a.mean(axis=2)
    neutral = (mx - mn) < 28
    # negros/grises -> tinta negra con transparencia proporcional; blanco -> transparente
    alpha = np.where(neutral, np.clip((205 - lum) / 105, 0, 1), np.clip((225 - mn) / 115, 0, 1))
    al = np.clip(alpha, 0.05, 1)[..., None]
    unm = np.clip((a - (1 - al) * 239) / al, 0, 255)
    rgb = np.where(neutral[..., None], 0, unm)
    ink = Image.fromarray(np.dstack([rgb, alpha * 255]).astype("uint8"), "RGBA")

    s_ = height / ink.size[1]
    size = (int(ink.size[0] * s_), height)
    return ink.resize(size, Image.LANCZOS), sil.resize(size, Image.LANCZOS).filter(ImageFilter.MaxFilter(5))


def gtext(text, size, top, bot, squeeze=0.80, tracking=0, maxw=None):
    font = ImageFont.truetype(FONT, size)
    ref = font.getbbox("ÍHg")
    pad = 10
    tmp = Image.new("L", (int(size * len(text) * 1.2) + 40, int(size * 2)), 0)
    d = ImageDraw.Draw(tmp)
    x = pad
    for ch in text:
        d.text((x, pad), ch, font=font, fill=255)
        x += d.textlength(ch, font=font) + tracking
    bb = tmp.getbbox()
    tmp = tmp.crop((bb[0], pad + ref[1], bb[2], pad + ref[3]))
    tmp = tmp.resize((max(1, int(tmp.size[0] * squeeze)), tmp.size[1]), Image.LANCZOS)
    if maxw and tmp.size[0] > maxw:
        s = maxw / tmp.size[0]
        tmp = tmp.resize((maxw, max(1, int(tmp.size[1] * s))), Image.LANCZOS)
    g = vgrad(tmp.size[0], tmp.size[1], top, bot).convert("RGBA")
    g.putalpha(tmp)
    return g


def paste_center(img, tx, y):
    img.alpha_composite(tx, ((W - tx.size[0]) // 2, int(y)))


CREAM = ((248, 228, 170), (232, 192, 112))
BRONZE = ((214, 156, 66), (176, 116, 40))
TITLE = ((247, 220, 142), (186, 122, 36))


def left_limit(mask, y0, y1):
    rows = mask[max(0, y0):min(H, y1), :]
    cols = np.where(rows.any(axis=0))[0]
    return int(cols.max()) if len(cols) else -1


def make_slide(tag, title, subtitle, lines, out):
    global rng
    rng = np.random.default_rng(7)  # misma decoración en todas las imágenes
    img = background()
    tr = [(W, 0), (690, 0)] + bezier((690, 0), (900, 40), (900, 330), (1080, 560))
    bl = bezier((0, 850), (30, 1060), (160, 1160), (330, 1350)) + [(0, H)]
    bl_mask = np.array(poly_mask(bl)) > 128
    img = Image.alpha_composite(img, gold_from_mask(poly_mask(tr)))
    img = Image.alpha_composite(img, gold_from_mask(poly_mask(bl), (140, 100, 20), (210, 164, 56)))

    # pincelada dorada + logo
    blob = brush_blob_mask(540, 205, 290, 150)
    logo_ink, logo_sil = logo_cut(330)
    lx, ly = (W - logo_ink.size[0]) // 2, 40
    sil_canvas = Image.new("L", (W, H), 0)
    sil_canvas.paste(logo_sil, (lx, ly))
    blob = ImageChops.lighter(blob, sil_canvas)  # el dorado cubre todo el logo: sin huecos blancos
    blob_fill = grain(vgrad(W, H, (232, 198, 104), (168, 118, 30)), 8).convert("RGBA")
    blob_fill.putalpha(blob)
    img = Image.alpha_composite(img, blob_fill)
    img.alpha_composite(logo_ink, (lx, ly))

    # destellos
    d = ImageDraw.Draw(img)
    for _ in range(26):
        if rng.random() < 0.6:
            x, y = int(rng.integers(930, 1075)), int(rng.integers(250, 1050))
        else:
            x, y = int(rng.integers(5, 140)), int(rng.integers(650, 1100))
        r = int(rng.integers(2, 6))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(244, 200, 40, 255))

    # textos
    paste_center(img, gtext(tag, 34, *BRONZE, squeeze=0.85, tracking=7), 398)
    paste_center(img, gtext(title, 140, *TITLE, squeeze=0.80, maxw=900), 440)
    paste_center(img, gtext(subtitle, 50, *BRONZE, squeeze=0.82, tracking=3, maxw=900), 624)

    n = len(lines)
    step = min(80, 495 / n)
    size = int(step / 1.30)
    y = 725 + max(0, (495 - step * n) / 2)  # centra el bloque si hay pocas líneas
    for text, kind in lines:
        cols = CREAM if kind == "k" else BRONZE
        tx = gtext(text, size, *cols, squeeze=0.80, maxw=940)
        yi = int(y)
        bx = left_limit(bl_mask, yi, yi + tx.size[1])
        allowed = W - 2 * (bx + 28) if bx >= 0 else 940
        if tx.size[0] > allowed:
            tx = gtext(text, size, *cols, squeeze=0.80, maxw=max(300, allowed))
        paste_center(img, tx, y)
        y += step
    paste_center(img, gtext(HANDLE, 34, *BRONZE, squeeze=0.85, tracking=2), 1272)

    path = out if os.path.isabs(out) else os.path.join(OUT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.convert("RGB").save(path, optimize=True)
    return path


if __name__ == "__main__":
    tag = "HALTEROFILIA"
    make_slide(tag, "WARM UP", "ESPECÍFICO PARA SNATCH", [
        ("3' row o bike suave", "k"),
        ("2 rondas (PVC y barra vacía)", "m"),
        ("10 pass-through con PVC", "k"),
        ("10 overhead squat con PVC", "k"),
        ("8 snatch grip good morning", "k"),
        ("6 muscle snatch", "k"),
        ("6 hang power snatch", "k"),
    ], "halterofilia_1_warmup.png")
    make_slide(tag, "STRENGTH", "SNATCH", [
        ("6 series de 2 reps", "k"),
        ("Series 1-2 al 60% del 1RM", "k"),
        ("Series 3-4 al 70% del 1RM", "k"),
        ("Series 5-6 al 75% del 1RM", "k"),
        ("Descanso 90 seg entre series", "m"),
        ("Técnica antes que carga", "m"),
    ], "halterofilia_2_strength.png")
    make_slide(tag, "FOR TIME", "TIME CAP 12'", [
        ("21-15-9", "m"),
        ("Power snatch (40/30 kg)", "k"),
        ("Burpees over the bar", "k"),
        ("Escala la carga a tu nivel", "m"),
    ], "halterofilia_3_wod.png")
    print("ok")
