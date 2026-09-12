#!/usr/bin/env python3
"""Compose a minimal paper-acrylic cover: photo + hand-drawn illustration on cream paper.

Two layouts:
  land (横图): full-width photo band at top (~47%), smaller feathered illustration
                 centered below on cream paper, title at bottom.
                   port (竖图): full cream canvas, un-cropped portrait photo centered near top,
                                  smaller illustration centered below, title at bottom.

                                  Usage:
                                    python3 compose.py --photo IN.jpg --ill ILL.jpg --out OUT.jpg \
      --layout auto --cn "中文标题" --en "english title."
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1440
PHOTO_H = 680           # land: upper photo band height
ILL_MAXW, ILL_MAXH = 820, 340   # land: illustration size cap
PORT_PHOTO_MAXW, PORT_PHOTO_MAXH = 860, 800
PORT_ILL_MAXW, PORT_ILL_MAXH = 560, 330

CN_COLOR = (60, 56, 50)
EN_COLOR = (176, 90, 53)

CN_FONT_CANDIDATES = [
      "/System/Library/Fonts/Songti.ttc",
      "/Library/Fonts/Songti.ttc",
      "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
EN_FONT_CANDIDATES = [
      "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
      "/System/Library/Fonts/SnellRoundhand.ttc",
]

def load_font(candidates, size):
      for p in candidates:
                if os.path.exists(p):
                              try:
                                                return ImageFont.truetype(p, size, index=2) if "Songti" in p else ImageFont.truetype(p, size)
except Exception:
                try: return ImageFont.truetype(p, size)
except Exception: pass
      return ImageFont.load_default()

def cover(im, tw, th):
      iw, ih = im.size; tr = tw/th; ir = iw/ih
      if ir > tr:
                nw = int(ih*tr); x0 = (iw-nw)//2
                im = im.crop((x0,0,x0+nw,ih))
else:
        nh = int(iw/tr); y0 = (ih-nh)//2
          im = im.crop((0,y0,iw,y0+nh))
    return im.resize((tw, th), Image.LANCZOS)

def fit(im, mw, mh):
      w, h = im.size; s = min(mw/w, mh/h)
    return im.resize((int(w*s), int(h*s)), Image.LANCZOS)

def softmask(w, h, feather=42):
      m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle([12,12,w-12,h-12], fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather))

def main():
      ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--ill", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--layout", choices=["auto","land","port"], default="auto")
    ap.add_argument("--cn", default="")
    ap.add_argument("--en", default="")
    a = ap.parse_args()

    photo = Image.open(a.photo).convert("RGB")
    ill = Image.open(a.ill).convert("RGB")
    paper = ill.getpixel((8, 8))
    canvas = Image.new("RGB", (W, H), paper)

    layout = a.layout
    if layout == "auto":
              layout = "port" if photo.size[1] > photo.size[0] else "land"

    if layout == "land":
              canvas.paste(cover(photo, W, PHOTO_H), (0, 0))
              i = fit(ill, ILL_MAXW, ILL_MAXH); iw, ih = i.size
              canvas.paste(i, ((W-iw)//2, 820), softmask(iw, ih))
else:
        p = fit(photo, PORT_PHOTO_MAXW, PORT_PHOTO_MAXH); pw, ph = p.size
        canvas.paste(p, ((W-pw)//2, 36))
        i = fit(ill, PORT_ILL_MAXW, PORT_ILL_MAXH); iw, ih = i.size
        canvas.paste(i, ((W-iw)//2, 36+ph+55))

    d = ImageDraw.Draw(canvas)
    f_cn = load_font(CN_FONT_CANDIDATES, 34)
    f_en = load_font(EN_FONT_CANDIDATES, 30)
    if a.cn:
              cw = d.textlength(a.cn, font=f_cn)
              d.text((W//2-cw/2, H-150), a.cn, font=f_cn, fill=CN_COLOR)
          if a.en:
                    ew = d.textlength(a.en, font=f_en)
                    d.text((W//2-ew/2, H-106), a.en, font=f_en, fill=EN_COLOR)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    canvas.save(a.out, "JPEG", quality=92)
    print("saved", a.out, f"({layout})")

if __name__ == "__main__":
      main()
