#!/usr/bin/env python3
"""Catalogue Photo of an Impossible Gadget — make.fun entry.

Renders the winning concept to /output/entry.png (1024x1024, <=1 MiB).
Dual-candidate record: A = COLDWAVE (a microwave that makes things colder),
B = SOCKHOLE (a portable black hole for lost socks). Both were rendered
in-session and harsh-judged against the published brief; A won (see
MAKEFUN_ELITE_REPORT). Run `python3 main.py B` to render the loser.

Stdlib + Pillow where available; without Pillow, copies the prebuilt
entry.png shipped beside this file (byte-identical). Deterministic:
fixed seed, no clocks, no network. Supersampled 2x, LANCZOS downscale.
"""
import os
import random
import shutil
import sys

S = 2                      # supersample factor
W = 1024 * S
H = 1024 * S
SEED = 20261121


def X(v):
    return int(round(v * S))


def vgrad(size, top, bottom):
    """Vertical gradient image, light `top` -> dark `bottom`."""
    from PIL import Image
    mask = Image.linear_gradient("L").resize(size)
    a = Image.new("RGB", size, top)
    b = Image.new("RGB", size, bottom)
    return Image.composite(b, a, mask)


def rgrad(size, center, inner, outer):
    """Radial gradient image, `inner` at centre -> `outer` at edge."""
    from PIL import Image
    mask = Image.radial_gradient("L").resize(size)
    a = Image.new("RGB", size, inner)
    b = Image.new("RGB", size, outer)
    return Image.composite(a, b, mask)


def soft_shadow(base, box, radius, alpha=110):
    """Blurred black shape on `base` (RGBA). box in 1024 coords."""
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


def font(path, size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(path, X(size))
    except Exception:
        return ImageFont.load_default()


BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def text(d, xy, s, fnt, size, fill):
    d.text((X(xy[0]), X(xy[1])), s, font=font(fnt, size), fill=fill,
           anchor="mm")


def spaced_text(d, xy, s, fnt, size, fill, gap=6):
    """Letterspaced centred text (brand names)."""
    from PIL import ImageFont
    f = font(fnt, size)
    widths = [d.textlength(ch, font=f) for ch in s]
    total = sum(widths) + gap * (len(s) - 1) * S
    x = X(xy[0]) - total // 2
    y = X(xy[1])
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor="lm")
        x += int(w) + gap * S


def studio_back(img, top, bottom, light_xy, light_col, floor_y=770):
    """Seamless studio sweep: gradient + radial key light + floor line."""
    from PIL import Image, ImageDraw, ImageFilter
    bg = vgrad((W, H), top, bottom)
    img.paste(bg, (0, 0))
    glow_spot(img, light_xy[0], light_xy[1], 430, 330, light_col, 70, 130)


def brushed_steel(d, box, rng, base_top=(226, 226, 226), base_bot=(150, 150, 150)):
    """Steel body with vertical gradient + horizontal brush streaks."""
    from PIL import Image, ImageDraw
    grad = vgrad((X(box[2] - box[0]), X(box[3] - box[1])), base_top, base_bot)
    # streaks drawn on a temp layer then pasted under the frame
    tmp = Image.new("RGBA", grad.size, (0, 0, 0, 0))
    dt = ImageDraw.Draw(tmp)
    for _ in range(140):
        y = rng.randrange(0, grad.size[1])
        x0 = rng.randrange(0, grad.size[0] // 2)
        x1 = x0 + rng.randrange(grad.size[0] // 3, grad.size[0])
        col = (255, 255, 255, rng.randrange(6, 16)) if rng.random() < 0.5 \
            else (0, 0, 0, rng.randrange(5, 12))
        dt.line([(x0, y), (min(x1, grad.size[0]), y)], fill=col, width=1)
    return grad, tmp


def ice_cube(d, cx, cy, size, tilt=0):
    """One pale-blue ice cube, centred (cx, cy), side `size` (1024 units)."""
    from PIL import Image, ImageDraw
    side = X(size)
    layer = Image.new("RGBA", (side * 2, side * 2), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    g = vgrad((side, side), (214, 235, 246), (158, 196, 216))
    mask = Image.new("L", (side, side), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle([0, 0, side - 1, side - 1], radius=side // 5, fill=255)
    layer.paste(g, (side // 2, side // 2), mask)
    dl.rounded_rectangle([side // 2, side // 2, side // 2 + side - 1,
                          side // 2 + side - 1], radius=side // 5,
                         outline=(255, 255, 255, 200), width=max(2, side // 40))
    # top-left facet highlight (small triangle, reads as ice, not an envelope)
    dl.polygon([(side // 2 + side // 8, side // 2 + side // 8),
                (side // 2 + side // 2, side // 2 + side // 8),
                (side // 2 + side // 8, side // 2 + side // 2)],
               fill=(255, 255, 255, 190))
    # inner crack line
    dl.line([(side // 2 + side // 3, side // 2 + side // 2),
             (side // 2 + side * 2 // 3, side // 2 + side * 3 // 4)],
            fill=(255, 255, 255, 130), width=max(2, side // 50))
    if tilt:
        layer = layer.rotate(tilt, expand=True, resample=Image.BICUBIC)
    return layer, (X(cx) - layer.size[0] // 2, X(cy) - layer.size[1] // 2)


def render_a():
    """COLDWAVE — the microwave that makes things colder."""
    from PIL import Image, ImageDraw, ImageFilter
    rng = random.Random(SEED)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    studio_back(img, (236, 234, 230), (198, 195, 188), (520, 400),
                (255, 255, 255))
    d = ImageDraw.Draw(img, "RGBA")

    # contact shadow under the microwave
    soft_shadow(img, (230, 690, 700, 745), 16, 120)
    # accessory shadow (ice cube)
    soft_shadow(img, (775, 700, 890, 730), 10, 100)

    # ---- microwave body ----
    body = (190, 300, 710, 700)
    grad, streaks = brushed_steel(d, body, rng)
    bmask = Image.new("L", grad.size, 0)
    dbm = ImageDraw.Draw(bmask)
    dbm.rounded_rectangle([0, 0, grad.size[0] - 1, grad.size[1] - 1],
                          radius=X(26), fill=255)
    img.paste(grad, (X(body[0]), X(body[1])), bmask)
    streaks = Image.composite(streaks,
                              Image.new("RGBA", streaks.size, (0, 0, 0, 0)),
                              bmask)
    img.alpha_composite(streaks, (X(body[0]), X(body[1])))
    rr(d, body, 26, outline=(90, 90, 90, 255), width=X(3))
    # top edge key-light
    d.line([(X(205), X(306)), (X(695), X(306))], fill=(255, 255, 255, 200),
           width=X(3))
    # brand on the top front edge
    spaced_text(d, (450, 322), "COLDWAVE", BOLD, 26, (70, 70, 70, 255), gap=8)

    # ---- door window ----
    win = (215, 345, 560, 640)
    wgrad = vgrad((X(win[2] - win[0]), X(win[3] - win[1])),
                  (16, 22, 30), (38, 54, 72))
    wmask = Image.new("L", wgrad.size, 0)
    dw = ImageDraw.Draw(wmask)
    dw.rounded_rectangle([0, 0, wgrad.size[0] - 1, wgrad.size[1] - 1],
                         radius=X(16), fill=255)
    img.paste(wgrad, (X(win[0]), X(win[1])), wmask)
    rr(d, win, 16, outline=(40, 40, 40, 255), width=X(4))
    # cold glow inside the window
    glow_spot(img, 388, 495, 150, 105, (90, 190, 235), 110, 60)
    # glass turntable
    ell(d, (270, 545, 505, 590), fill=(120, 160, 190, 90),
        outline=(200, 225, 240, 160), width=X(2))
    # three ice cubes on the turntable
    for (cx, cy, sz, tilt) in [(330, 520, 62, 8), (410, 505, 70, -10),
                               (470, 525, 56, 14)]:
        layer, pos = ice_cube(d, cx, cy, sz, tilt)
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
    # display
    disp = (620, 360, 682, 412)
    rr(d, disp, 8, fill=(8, 20, 26, 255))
    text(d, (651, 386), "−18°C", BOLD, 16, (110, 230, 245, 255))
    # three buttons
    for i, y in enumerate((445, 500, 555)):
        rr(d, (628, y, 674, y + 34), 8,
           fill=(225, 225, 225, 255), outline=(100, 100, 100, 255),
           width=X(2))
    text(d, (651, 462), "❄", BOLD, 20, (60, 120, 150, 255))
    text(d, (651, 517), "−", BOLD, 24, (80, 80, 80, 255))
    text(d, (651, 572), "+", BOLD, 24, (80, 80, 80, 255))
    text(d, (651, 615), "CW-18", REG, 13, (90, 90, 90, 255))

    # ---- feet ----
    rect(d, (230, 700, 270, 716), fill=(40, 40, 40, 255))
    rect(d, (630, 700, 670, 716), fill=(40, 40, 40, 255))

    # ---- accessory: one ice cube on the counter ----
    layer, pos = ice_cube(d, 830, 668, 74, -12)
    img.alpha_composite(layer, pos)
    return img


def render_b():
    """SOCKHOLE — the portable black hole for lost socks."""
    from PIL import Image, ImageDraw, ImageFilter
    import math
    rng = random.Random(SEED + 1)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    studio_back(img, (64, 68, 78), (30, 32, 38), (512, 520),
                (120, 120, 150))
    d = ImageDraw.Draw(img, "RGBA")

    # violet rim glow behind the disc
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse([X(230), X(330), X(794), X(800)],
               fill=(123, 92, 255, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(X(26)))
    img.alpha_composite(glow)
    soft_shadow(img, (280, 700, 744, 760), 18, 130)

    # ---- the disc ----
    cx, cy, rx, ry = 512, 565, 272, 205
    disc = rgrad((X(rx * 2), X(ry * 2)), None, (4, 4, 8), (38, 38, 48))
    disc = disc.convert("RGBA")
    dmask = Image.new("L", (X(rx * 2), X(ry * 2)), 0)
    dm = ImageDraw.Draw(dmask)
    dm.ellipse([0, 0, X(rx * 2) - 1, X(ry * 2) - 1], fill=255)
    disc.putalpha(dmask)
    img.alpha_composite(disc, (X(cx - rx), X(cy - ry)))
    # spiral suction streaks
    for k, (a0, a1, rr_) in enumerate([(200, 330, 0.86), (20, 150, 0.68),
                                      (300, 420, 0.5)]):
        pts = []
        for t in range(41):
            a = math.radians(a0 + (a1 - a0) * t / 40)
            r = rr_ * (1 - 0.45 * t / 40)
            pts.append((X(cx + rx * r * math.cos(a)),
                        X(cy + ry * r * math.sin(a))))
        d.line(pts, fill=(150, 140, 220, 150), width=X(5))
    # specular arc on the upper-left rim
    arc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    da = ImageDraw.Draw(arc)
    da.arc([X(cx - rx), X(cy - ry), X(cx + rx), X(cy + ry)],
           start=150, end=215, fill=(255, 255, 255, 200), width=X(10))
    arc = arc.filter(ImageFilter.GaussianBlur(X(8)))
    img.alpha_composite(arc)
    # label on the disc
    spaced_text(d, (512, 720), "SOCKHOLE", BOLD, 24, (235, 235, 240, 255),
                gap=7)
    text(d, (512, 748), "MODEL SH-01", REG, 13, (170, 170, 180, 255))

    # ---- the sock being eaten ----
    # quadratic bezier from (860, 300) via (760, 430) to (540, 560)
    def bez(t):
        x = (1 - t) ** 2 * 860 + 2 * (1 - t) * t * 760 + t * t * 540
        y = (1 - t) ** 2 * 300 + 2 * (1 - t) * t * 430 + t * t * 560
        return x, y

    def tang(t):
        x = 2 * (1 - t) * (760 - 860) + 2 * t * (540 - 760)
        y = 2 * (1 - t) * (430 - 300) + 2 * t * (560 - 430)
        n = math.hypot(x, y)
        return x / n, y / n

    # sock body: overlapping discs along the path, tapering
    for i in range(60):
        t = i / 59
        x, y = bez(t)
        w = 34 - 20 * t
        ell(d, (x - w, y - w * 0.82, x + w, y + w * 0.82),
            fill=(238, 238, 235, 255))
    # red stripes across the sock
    for t in (0.12, 0.30, 0.48, 0.66):
        x, y = bez(t)
        tx, ty = tang(t)
        px, py = -ty, tx
        w = 34 - 20 * t
        d.line([(X(x - px * w * 0.82), X(y - py * w * 0.82)),
                (X(x + px * w * 0.82), X(y + py * w * 0.82))],
               fill=(192, 57, 43, 255), width=X(13))
    # heel patch near the top
    hx, hy = bez(0.06)
    ell(d, (hx - 26, hy - 8, hx + 26, hy + 22), fill=(192, 57, 43, 255))
    # stretched tip disappearing into the disc
    tx, ty = bez(0.97)
    ell(d, (tx - 12, ty - 8, tx + 12, ty + 8), fill=(220, 220, 218, 255))

    # ---- accessory: one lone folded sock ----
    soft_shadow(img, (800, 770, 930, 800), 8, 100)
    rr(d, (806, 700, 924, 770), 14, fill=(238, 238, 235, 255),
       outline=(150, 150, 150, 255), width=X(2))
    rect(d, (806, 726, 924, 744), fill=(192, 57, 43, 255))
    rect(d, (806, 752, 924, 766), fill=(192, 57, 43, 255))
    return img


def main():
    cand = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
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
    img = render_a() if cand == "A" else render_b()
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)


if __name__ == "__main__":
    main()
