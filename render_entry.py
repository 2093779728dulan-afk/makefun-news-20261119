import os
from PIL import Image, ImageDraw, ImageFont

S = 3
W = H = 1024

PAPER = "#F7F3E9"
INK = "#151A1F"
MUTED = "#6C706F"
RULE = "#C9C1B1"
RED = "#C62828"
ORANGE = "#F07427"
GREEN = "#76B900"
CYAN = "#63D2E8"
NAVY = "#0D1E2C"
SEA = "#0A2436"
LAND = "#143B4C"
COAST = "#3E7794"

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONTS = {
    ("sans", False): os.path.join(FONT_DIR, "DejaVuSans.ttf"),
    ("sans", True): os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),
    ("serif", True): os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf"),
    ("serif", False): os.path.join(FONT_DIR, "DejaVuSerif.ttf"),
}
_CACHE = {}


def f(size, bold=False, serif=False):
    key = (size, bold, serif)
    if key not in _CACHE:
        _CACHE[key] = ImageFont.truetype(FONTS[("serif" if serif else "sans", bold)], size * S)
    return _CACHE[key]


def s(v):
    return int(round(v * S))


def xyseq(seq):
    return [(s(a), s(b)) for a, b in seq]


class G:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    def width(self, text, font):
        return self.d.textlength(text, font=font) / S

    def line(self, points, fill, width=1, joint="curve"):
        self.d.line(xyseq(points), fill=fill, width=max(1, s(width)), joint=joint)

    def polygon(self, points, fill=None, outline=None, width=1):
        self.d.polygon(xyseq(points), fill=fill)
        if outline:
            self.line(list(points) + [points[0]], outline, width)

    def rectangle(self, box, fill=None, outline=None, width=1):
        self.d.rectangle([s(box[0]), s(box[1]), s(box[2]), s(box[3])], fill=fill, outline=outline, width=s(width))

    def rounded_rectangle(self, box, radius, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(
            [s(box[0]), s(box[1]), s(box[2]), s(box[3])],
            radius=s(radius), fill=fill, outline=outline, width=s(width),
        )

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse([s(box[0]), s(box[1]), s(box[2]), s(box[3])], fill=fill, outline=outline, width=s(width))

    def arc(self, box, start, end, fill, width=1):
        self.d.arc([s(box[0]), s(box[1]), s(box[2]), s(box[3])], start, end, fill=fill, width=s(width))

    def text(self, pos, text, font, fill, anchor=None, tracking=0):
        if not tracking:
            self.d.text((s(pos[0]), s(pos[1])), text, font=font, fill=fill, anchor=anchor)
            return
        x, y = pos
        widths = [self.width(ch, font) for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        horiz = anchor[0] if anchor else "l"
        if horiz == "m":
            x -= total / 2
        elif horiz == "r":
            x -= total
        vert = anchor[1] if anchor and len(anchor) > 1 else "a"
        bbox = self.d.textbbox((0, 0), text, font=font, anchor="la")
        height = bbox[3] - bbox[1]
        if vert == "t":
            y -= bbox[1]
        elif vert == "m":
            y -= bbox[1] + height / 2
        for ch, cw in zip(text, widths):
            self.d.text((s(x), s(y)), ch, font=font, fill=fill, anchor="la")
            x += cw + tracking

    def fit(self, text, pos, max_w, size, bold=False, serif=False, fill=INK, anchor=None, tracking=0, min_size=8):
        while size > min_size:
            font = f(size, bold, serif)
            w = sum(self.width(c, font) for c in text) + tracking * (len(text) - 1) if tracking else self.width(text, font)
            if w <= max_w:
                break
            size -= 1
        self.text(pos, text, f(size, bold, serif), fill, anchor=anchor, tracking=tracking)
        return size


def dashed(g, p0, p1, color, width=2, dash=7, gap=6):
    import math
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if not length:
        return
    ux, uy = dx / length, dy / length
    t = 0.0
    while t < length:
        e = min(t + dash, length)
        g.line([(p0[0] + ux * t, p0[1] + uy * t), (p0[0] + ux * e, p0[1] + uy * e)], color, width)
        t += dash + gap


def drone(g, x, y, color):
    g.line([(x - 7, y - 7), (x + 7, y + 7)], color, 2)
    g.line([(x - 7, y + 7), (x + 7, y - 7)], color, 2)
    for dx, dy in ((-7, -7), (7, -7), (-7, 7), (7, 7)):
        g.ellipse((x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2), fill=color)


def card(g, box, fill="#FFFFFF", accent=None, accent_side="top"):
    g.rectangle(box, fill=fill, outline=RULE, width=1)
    if accent:
        x0, y0, x1, y1 = box
        if accent_side == "top":
            g.rectangle((x0 + 1, y0 + 1, x1 - 1, y0 + 6), fill=accent)
        else:
            g.rectangle((x0 + 1, y0 + 1, x0 + 6, y1 - 1), fill=accent)


def cross(g, x, y, r, color, width=2):
    g.line([(x - r, y - r), (x + r, y + r)], color, width)
    g.line([(x - r, y + r), (x + r, y - r)], color, width)


def render():
    img = Image.new("RGB", (W * S, H * S), PAPER)
    g = G(img)

    g.rectangle((10, 10, 1014, 1014), outline=INK, width=2)

    g.text((28, 18), "GLOBAL EDITION  /  NO. 11·18", f(12, True), INK)
    g.text((996, 18), "06 STORIES  /  ONE PAGE", f(12, True), INK, anchor="ra")
    g.line([(28, 38), (996, 38)], INK, 1)

    g.fit("THE WORLD", (512, 58), 720, 84, True, True, INK, anchor="mt", tracking=1)
    g.line([(28, 140), (996, 140)], INK, 4)
    g.line([(28, 146), (996, 146)], INK, 1)
    g.text((512, 151), "WEDNESDAY, NOV. 18, 2026", f(19, True), INK, anchor="mt", tracking=2)
    g.line([(28, 180), (996, 180)], INK, 1)
    g.line([(28, 185), (996, 185)], INK, 3)

    # 01 - lead: Trump-Putin-Xi Trilateral Summit
    card(g, (28, 194, 660, 510), "#FFFDF7", "#B31B2C")
    g.text((48, 204), "01 / DIPLOMACY", f(11, True), MUTED, tracking=1)
    g.fit("TRUMP · PUTIN · XI", (48, 222), 580, 44, True, False, INK)
    g.text((48, 274), "TRILATERAL SUMMIT IN SHENZHEN", f(18, True), "#B31B2C")
    g.text((48, 298), "APEC 2026 · NOV 18–19", f(14, False), MUTED)

    # Three leader silhouettes
    for i, (cx, name, tone) in enumerate([
        (140, "TRUMP", "#C62828"),
        (330, "PUTIN", "#2C3A45"),
        (520, "XI", "#1B3A5C"),
    ]):
        g.ellipse((cx - 35, 330, cx + 35, 400), fill=tone)
        g.polygon([(cx - 55, 450), (cx - 50, 418), (cx - 35, 410),
                   (cx + 35, 410), (cx + 50, 418), (cx + 55, 450)], fill=tone)
        g.text((cx, 462), name, f(13, True), "#F7F3E9", anchor="mt", tracking=1)

    # Handshake in center
    g.ellipse((300, 380, 360, 440), fill="#D9A789", outline="#8C604B", width=2)
    g.line([(290, 410), (310, 400), (330, 390), (350, 380)], "#8C604B", 4)
    g.line([(370, 380), (390, 390), (410, 400), (430, 410)], "#8C604B", 4)

    g.text((330, 480), "FREE TRADE · SECURITY · TAIWAN", f(12, True), INK, anchor="mt", tracking=1)

    # Flags row
    flag_x = 48
    for flag_color, label in [
        ("#FF0000", "USA"),
        ("#FFFFFF", "RUS"),
        ("#DE2910", "CHN"),
    ]:
        g.rectangle((flag_x, 498, flag_x + 40, 518), fill=flag_color, outline=INK, width=1)
        g.text((flag_x + 20, 518), label, f(10, True), INK, anchor="mt")
        flag_x += 50

    # 02 - Gulf Strikes on Qeshm Island
    card(g, (676, 194, 996, 510), "#FFF8F5", RED, "top")
    g.text((696, 204), "02 / CONFLICT", f(11, True), MUTED, tracking=1)
    g.fit("GULF ESCALATION", (696, 222), 290, 28, True, False, INK)
    g.text((696, 258), "US STRIKE ON QESHM ISLAND", f(16, True), RED)
    g.text((696, 282), "IRANIAN DRONES HIT BAHRAIN", f(13, False), INK)
    g.text((696, 302), "KUWAIT REPELS ATTACK", f(13, False), INK)

    # Simple Gulf map
    mx0, my0, mx1, my1 = 696, 326, 976, 494
    g.rectangle((mx0, my0, mx1, my1), fill=SEA)
    for x in range(mx0 + 40, mx1, 40):
        g.line([(x, my0), (x, my1)], "#14374A", 1)
    for y in range(my0 + 30, my1, 30):
        g.line([(mx0, y), (mx1, y)], "#14374A", 1)

    # Iran coast
    iran_coast = [(696, 326), (976, 326), (976, 380), (940, 370), (900, 380), (860, 372),
                  (820, 384), (780, 374), (740, 362), (700, 350)]
    g.polygon(iran_coast, LAND, COAST, 2)

    # Arabian coast
    arabia_coast = [(696, 450), (730, 440), (780, 432), (840, 436), (890, 446),
                    (930, 464), (976, 480), (976, 494), (696, 494)]
    g.polygon(arabia_coast, LAND, COAST, 2)

    # Qeshm Island
    g.ellipse((880, 340, 930, 370), fill="#20566A", outline=CYAN, width=2)
    g.text((905, 320), "QESHM IS.", f(11, True), "#FFD0B8", anchor="mb")

    # Strike marker
    sx, sy = 905, 355
    g.ellipse((sx - 28, sy - 28, sx + 28, sy + 28), outline="#FF5A3C", width=3)
    g.ellipse((sx - 18, sy - 18, sx + 18, sy + 18), outline="#FFB347", width=2)
    for a in range(0, 360, 45):
        import math
        r = math.radians(a)
        g.line([(sx + 6 * math.cos(r), sy + 6 * math.sin(r)),
                (sx + 14 * math.cos(r), sy + 14 * math.sin(r))], "#FFD9A0", 2)
    g.ellipse((sx - 5, sy - 5, sx + 5, sy + 5), fill=RED)

    # Drone paths
    dashed(g, (800, 350), (720, 420), ORANGE, 2, 8, 5)
    drone(g, 750, 390, ORANGE)
    dashed(g, (820, 360), (780, 460), ORANGE, 2, 7, 6)
    drone(g, 800, 410, ORANGE)

    # Bahrain & Kuwait
    g.ellipse((760, 430, 780, 442), fill="#2A6076", outline=CYAN, width=2)
    g.text((788, 430), "BAHRAIN", f(10, True), "#BFE8F1")
    g.ellipse((710, 390, 730, 402), fill="#2A6076", outline=CYAN, width=2)
    g.text((738, 390), "KUWAIT", f(10, True), "#BFE8F1")
    cross(g, 770, 436, 5, CYAN, 2)
    cross(g, 720, 396, 5, CYAN, 2)

    g.text((840, 390), "STRAIT OF", f(11, True), CYAN)
    g.text((840, 408), "HORMUZ", f(11, True), CYAN)

    # 03 - Kerch Bridge Collapse
    card(g, (28, 524, 490, 706), "#FFF0F0", RED, "left")
    g.text((56, 534), "03 / UKRAINE", f(11, True), RED, tracking=1)
    g.fit("KERCH BRIDGE", (56, 554), 400, 28, True, False, INK)
    g.fit("PARTLY COLLAPSES", (56, 586), 400, 28, True, False, INK)
    g.text((56, 624), "UKRAINIAN STRIKE", f(16, True), RED)
    g.text((56, 648), "CRIMEA LINK SEVERED", f(14, False), MUTED)
    g.text((56, 670), "RAIL & ROAD SPANS DOWN", f(13, False), MUTED)

    # Bridge schematic
    bx, by = 380, 570
    g.line([(bx - 80, by + 20), (bx + 80, by + 20)], "#8B7355", 8)
    g.line([(bx - 80, by - 20), (bx + 80, by - 20)], "#8B7355", 8)
    for i in range(-70, 71, 20):
        g.line([(bx + i, by - 20), (bx + i, by + 20)], "#5D4E37", 3)
    # Broken section
    g.line([(bx - 10, by - 20), (bx + 10, by + 20)], RED, 5)
    g.line([(bx - 10, by + 20), (bx + 10, by - 20)], RED, 5)
    g.text((bx, by + 45), "COLLAPSED SPAN", f(10, True), RED, anchor="mt")

    # 04 - EU €45bn Ukraine Loan
    card(g, (506, 524, 996, 706), "#F0F8F0", GREEN, "top")
    g.text((526, 534), "04 / EUROPE", f(11, True), MUTED, tracking=1)
    g.fit("EU €45BN LOAN", (526, 554), 440, 36, True, False, INK)
    g.text((526, 596), "FOR UKRAINE 2027", f(20, True), GREEN)
    g.text((526, 624), "LARGEST AID PACKAGE YET", f(14, False), INK)
    g.text((526, 648), "MACRON · SCHOLZ · MELONI BACK", f(13, False), MUTED)
    g.text((526, 670), "PIPELINE FIGHTING NEAR KHARKIV", f(12, True), ORANGE)

    # Euro symbol with Ukraine colors
    ex, ey = 900, 600
    g.ellipse((ex - 40, ey - 40, ex + 40, ey + 40), fill="#0057B8", outline="#FFD700", width=3)
    g.ellipse((ex - 25, ey - 25, ex + 25, ey + 25), fill="#0057B8")
    g.line([(ex - 30, ey), (ex + 30, ey)], "#FFD700", 5)
    g.line([(ex - 22, ey - 22), (ex + 22, ey - 22)], "#FFD700", 3)
    g.line([(ex - 22, ey + 22), (ex + 22, ey + 22)], "#FFD700", 3)
    g.text((ex, ey + 55), "€45 BN", f(16, True), GREEN, anchor="mt")

    # 05 - US Loses Measles-Free Status
    card(g, (28, 720, 490, 900), "#FFFBEF", "#D98A00", "left")
    g.text((56, 730), "05 / HEALTH", f(11, True), "#A86800", tracking=1)
    g.fit("US LOSES MEASLES", (56, 750), 400, 22, True, False, INK)
    g.fit("ELIMINATION STATUS", (56, 776), 400, 22, True, False, INK)
    g.text((56, 808), "AFTER 26 YEARS", f(16, True), "#A86800")
    g.text((56, 834), "OUTBREAKS IN 30+ STATES", f(13, False), MUTED)
    g.text((56, 856), "VACCINATION RATES DROP", f(13, False), MUTED)
    g.text((56, 878), "CDC DECLARES END OF ERA", f(12, True), RED)

    # Measles virus icon
    hx, hy = 400, 810
    g.ellipse((hx - 35, hy - 35, hx + 35, hy + 35), outline="#D98A00", width=3)
    g.ellipse((hx - 20, hy - 20, hx + 20, hy + 20), outline="#F3D69B", width=2)
    for dx, dy in [(-40, -35), (42, -28), (-35, 35), (40, 32), (-20, -45), (45, 20)]:
        g.ellipse((hx + dx - 6, hy + dy - 6, hx + dx + 6, hy + dy + 6), fill="#C62828")
    g.text((hx, hy), "⚠", f(24, True), RED, anchor="mm")

    # 06 - Alaska Senate Flip
    card(g, (506, 720, 996, 900), "#F0F4FF", "#1E3A8A", "top")
    g.text((526, 730), "06 / POLITICS", f(11, True), MUTED, tracking=1)
    g.fit("ALASKA FLIPS BLUE", (526, 750), 440, 28, True, False, INK)
    g.text((526, 786), "PELTOLA WINS SENATE", f(20, True), "#1E3A8A")
    g.text((526, 814), "FIRST DEM SENATOR SINCE 2009", f(14, False), INK)
    g.text((526, 838), "JEFFRIES: 1ST BLACK SPEAKER", f(14, True), "#1E3A8A")
    g.text((526, 862), "HOUSE DEMS UNITE", f(13, False), MUTED)
    g.text((526, 882), "ANTHROPIC IPO · $40B VALUATION", f(12, True), GREEN)

    # Alaska outline
    ax, ay = 900, 810
    alaska = [(ax - 35, ay - 45), (ax - 20, ay - 55), (ax + 5, ay - 40),
              (ax + 30, ay - 20), (ax + 40, ay + 10), (ax + 25, ay + 35),
              (ax, ay + 50), (ax - 20, ay + 40), (ax - 40, ay + 15),
              (ax - 45, ay - 10)]
    g.polygon(alaska, fill="#1E3A8A", outline="#FFFFFF", width=2)
    g.ellipse((ax - 5, ay - 10, ax + 5, ay), fill="#FFD700")
    g.text((ax, ay + 55), "AK", f(12, True), "#FFFFFF", anchor="mt")

    # Footer
    g.line([(28, 916), (996, 916)], INK, 2)
    g.text((28, 928), "THE WORLD  ·  WEDNESDAY, NOV. 18, 2026", f(11, True), INK)
    g.text((996, 928), "SHENZHEN · QESHM · KERCH · EU45BN · MEASLES · ALASKA", f(10, False), MUTED, anchor="ra")
    g.line([(28, 962), (996, 962)], RULE, 1)
    g.text((28, 972), "WORLD DESK  /  EDITORIAL GRAPHIC", f(9, True), MUTED)
    g.text((996, 972), "06 / 06", f(9, True), MUTED, anchor="ra")

    return img.resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entry.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im = render()
    im.save(out, format="PNG", optimize=True, compress_level=9)
    print(out, os.path.getsize(out), "bytes")
    from PIL import Image as Img
    im2 = Img.open(out)
    print(f"Size: {im2.size}")