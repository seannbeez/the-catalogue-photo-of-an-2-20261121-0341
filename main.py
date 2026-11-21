#!/usr/bin/env python3
"""COLDWAVE — a catalogue photograph of an impossible gadget.

A brushed-steel countertop microwave that runs backwards: it makes things
colder. The shot catches it mid-use — three ice cubes turning on the glass
turntable inside a frost-rimmed window, the display reading -18C, a
snowflake button on the panel — with exactly one accessory, a single ice
cube waiting on the counter beside it. The joke reads from the picture
alone: a microwave, full of ice, proudly freezing.

Renders to /output/entry.png (1024x1024, under the 1 MiB cap). Standard
library + Pillow where available; without Pillow it copies the prebuilt
entry.png shipped beside this file (byte-identical). Deterministic: fixed
seed, no clocks, no network. Supersampled 2x, LANCZOS downscale.

A second concept (SOCKHOLE, a portable black hole for lost socks) was
designed, rendered and harsh-judged against the same five published
criteria in-session; COLDWAVE won because the job reads at a glance (the
sock read as a striped stick, and the black disc did not look
manufactured). That comparison lives in the campaign report, not here.
"""
import os
import random
import shutil
import sys

S = 2
W = 1024 * S
H = 1024 * S
SEED = 20261121
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def X(v):
    return int(round(v * S))


def vgrad(size, top, bottom):
    """Vertical gradient, light `top` colour to darker `bottom`."""
    from PIL import Image
    mask = Image.linear_gradient("L").resize(size)
    a = Image.new("RGB", size, top)
    b = Image.new("RGB", size, bottom)
    return Image.composite(b, a, mask)


def soft_shadow(base, box, radius, alpha=110):
    """Blurred black ellipse under a product. Box in 1024 coords."""
    from PIL import Image, ImageDraw, ImageFilter
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([X(box[0]), X(box[1]), X(box[2]), X(box[3])],
              fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(X(radius)))
    base.alpha_composite(layer)


def glow_spot(base, cx, cy, rx, ry, color, alpha, blur):
    """Soft elliptical light: solid ellipse + heavy blur, fades to zero."""
    from PIL import Image, ImageDraw, ImageFilter
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([X(cx - rx), X(cy - ry), X(cx + rx), X(cy + ry)],
              fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(X(blur)))
    base.alpha_composite(layer)


def rr(d, box, radius, **kw):
    d.rounded_rectangle([X(box[0]), X(box[1]), X(box[2]), X(box[3])],
                        radius=X(radius), **kw)


def rect(d, box, **kw):
    d.rectangle([X(box[0]), X(box[1]), X(box[2]), X(box[3])], **kw)


def ell(d, box, **kw):
    d.ellipse([X(box[0]), X(box[1]), X(box[2]), X(box[3])], **kw)


def load_font(path, size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(path, X(size))
    except Exception:
        return ImageFont.load_default()


def text(d, xy, s, fnt, size, fill):
    d.text((X(xy[0]), X(xy[1])), s, font=load_font(fnt, size), fill=fill,
           anchor="mm")


def spaced_text(d, xy, s, fnt, size, fill, gap=6):
    """Letterspaced centred text for brand names."""
    f = load_font(fnt, size)
    widths = [d.textlength(ch, font=f) for ch in s]
    total = sum(widths) + gap * (len(s) - 1) * S
    x = X(xy[0]) - total // 2
    y = X(xy[1])
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor="lm")
        x += int(w) + gap * S


def ice_cube(cx, cy, size, tilt=0):
    """One pale-blue ice cube as a small RGBA layer + paste position."""
    from PIL import Image, ImageDraw
    side = X(size)
    layer = Image.new("RGBA", (side * 2, side * 2), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    g = vgrad((side, side), (214, 235, 246), (158, 196, 216))
    mask = Image.new("L", (side, side), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle([0, 0, side - 1, side - 1], radius=side // 5,
                         fill=255)
    layer.paste(g, (side // 2, side // 2), mask)
    dl.rounded_rectangle([side // 2, side // 2, side // 2 + side - 1,
                          side // 2 + side - 1], radius=side // 5,
                         outline=(255, 255, 255, 200),
                         width=max(2, side // 40))
    # small white triangle at the top-left corner: the ice facet
    dl.polygon([(side // 2 + side // 8, side // 2 + side // 8),
                (side // 2 + side // 2, side // 2 + side // 8),
                (side // 2 + side // 8, side // 2 + side // 2)],
               fill=(255, 255, 255, 190))
    # faint inner crack
    dl.line([(side // 2 + side // 3, side // 2 + side // 2),
             (side // 2 + side * 2 // 3, side // 2 + side * 3 // 4)],
            fill=(255, 255, 255, 130), width=max(2, side // 50))
    if tilt:
        layer = layer.rotate(tilt, expand=True, resample=Image.BICUBIC)
    return layer, (X(cx) - layer.size[0] // 2, X(cy) - layer.size[1] // 2)


def render():
    """The COLDWAVE studio shot, drawn at 2x supersampling."""
    from PIL import Image, ImageDraw, ImageFilter
    rng = random.Random(SEED)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # seamless studio sweep: light gradient + soft key light
    img.paste(vgrad((W, H), (236, 234, 230), (198, 195, 188)), (0, 0))
    glow_spot(img, 520, 400, 430, 330, (255, 255, 255), 70, 130)
    d = ImageDraw.Draw(img, "RGBA")

    soft_shadow(img, (230, 690, 700, 745), 16, 120)
    soft_shadow(img, (775, 700, 890, 730), 10, 100)

    # ---- microwave body: brushed steel ----
    body = (190, 300, 710, 700)
    grad = vgrad((X(body[2] - body[0]), X(body[3] - body[1])),
                 (226, 226, 226), (150, 150, 150))
    bmask = Image.new("L", grad.size, 0)
    dbm = ImageDraw.Draw(bmask)
    dbm.rounded_rectangle([0, 0, grad.size[0] - 1, grad.size[1] - 1],
                          radius=X(26), fill=255)
    img.paste(grad, (X(body[0]), X(body[1])), bmask)
    # horizontal brush streaks, clipped to the body shape
    streaks = Image.new("RGBA", grad.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(streaks)
    for _ in range(140):
        y = rng.randrange(0, grad.size[1])
        x0 = rng.randrange(0, grad.size[0] // 2)
        x1 = x0 + rng.randrange(grad.size[0] // 3, grad.size[0])
        col = (255, 255, 255, rng.randrange(6, 16)) if rng.random() < 0.5 \
            else (0, 0, 0, rng.randrange(5, 12))
        ds.line([(x0, y), (min(x1, grad.size[0]), y)], fill=col, width=1)
    streaks = Image.composite(streaks,
                              Image.new("RGBA", streaks.size, (0, 0, 0, 0)),
                              bmask)
    img.alpha_composite(streaks, (X(body[0]), X(body[1])))
    rr(d, body, 26, outline=(90, 90, 90, 255), width=X(3))
    d.line([(X(205), X(306)), (X(695), X(306))],
           fill=(255, 255, 255, 200), width=X(3))
    spaced_text(d, (450, 322), "COLDWAVE", BOLD, 26, (70, 70, 70, 255),
                gap=8)

    # ---- door window: dark glass, cold glow, ice on the turntable ----
    win = (215, 345, 560, 640)
    wgrad = vgrad((X(win[2] - win[0]), X(win[3] - win[1])),
                  (16, 22, 30), (38, 54, 72))
    wmask = Image.new("L", wgrad.size, 0)
    dw = ImageDraw.Draw(wmask)
    dw.rounded_rectangle([0, 0, wgrad.size[0] - 1, wgrad.size[1] - 1],
                         radius=X(16), fill=255)
    img.paste(wgrad, (X(win[0]), X(win[1])), wmask)
    rr(d, win, 16, outline=(40, 40, 40, 255), width=X(4))
    glow_spot(img, 388, 495, 150, 105, (90, 190, 235), 110, 60)
    ell(d, (270, 545, 505, 590), fill=(120, 160, 190, 90),
        outline=(200, 225, 240, 160), width=X(2))
    for (cx, cy, sz, tilt) in [(330, 520, 62, 8), (410, 505, 70, -10),
                               (470, 525, 56, 14)]:
        layer, pos = ice_cube(cx, cy, sz, tilt)
        img.alpha_composite(layer, pos)
    # frost speckles along the window's bottom edge
    for _ in range(46):
        fx = rng.uniform(win[0] + 8, win[2] - 8)
        fy = rng.uniform(win[3] - 22, win[3] - 4)
        r = rng.uniform(1.5, 3.5)
        ell(d, (fx - r, fy - r, fx + r, fy + r),
            fill=(255, 255, 255, rng.randrange(120, 210)))

    # ---- handle ----
    hgrad = vgrad((X(26), X(310)), (235, 235, 235), (140, 140, 140))
    hmask = Image.new("L", hgrad.size, 0)
    dh = ImageDraw.Draw(hmask)
    dh.rounded_rectangle([0, 0, hgrad.size[0] - 1, hgrad.size[1] - 1],
                         radius=X(12), fill=255)
    img.paste(hgrad, (X(572), X(345)), hmask)
    rr(d, (572, 345, 598, 640), 12, outline=(80, 80, 80, 255), width=X(2))

    # ---- control panel ----
    panel = (612, 345, 690, 640)
    pgrad = vgrad((X(panel[2] - panel[0]), X(panel[3] - panel[1])),
                  (200, 200, 200), (130, 130, 130))
    pmask = Image.new("L", pgrad.size, 0)
    dp = ImageDraw.Draw(pmask)
    dp.rounded_rectangle([0, 0, pgrad.size[0] - 1, pgrad.size[1] - 1],
                         radius=X(12), fill=255)
    img.paste(pgrad, (X(panel[0]), X(panel[1])), pmask)
    rr(d, panel, 12, outline=(90, 90, 90, 255), width=X(2))
    rr(d, (620, 360, 682, 412), 8, fill=(8, 20, 26, 255))
    text(d, (651, 386), "-18°C", BOLD, 16, (110, 230, 245, 255))
    for y in (445, 500, 555):
        rr(d, (628, y, 674, y + 34), 8, fill=(225, 225, 225, 255),
           outline=(100, 100, 100, 255), width=X(2))
    text(d, (651, 462), "❄", BOLD, 20, (60, 120, 150, 255))
    text(d, (651, 517), "−", BOLD, 24, (80, 80, 80, 255))
    text(d, (651, 572), "+", BOLD, 24, (80, 80, 80, 255))
    text(d, (651, 615), "CW-18", REG, 13, (90, 90, 90, 255))

    # ---- feet ----
    rect(d, (230, 700, 270, 716), fill=(40, 40, 40, 255))
    rect(d, (630, 700, 670, 716), fill=(40, 40, 40, 255))

    # ---- accessory: one ice cube on the counter ----
    layer, pos = ice_cube(830, 668, 74, -12)
    img.alpha_composite(layer, pos)
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    try:
        from PIL import Image
    except Exception:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry.png")
        shutil.copyfile(src, out)
        return
    img = render()
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)


if __name__ == "__main__":
    main()
