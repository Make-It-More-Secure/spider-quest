# build_spider_quest_v3.py
# Generates TWO kid-optimized picture books (8.5x8.5 and 8x10) with LARGE text
# and simple, colorful illustrations for every page. Output goes to ./books.
#
# Requirements: Pillow (PIL)
#   pip install pillow

from PIL import Image, ImageDraw, ImageFont
import os, math, textwrap

ROOT = os.path.abspath(".")
BOOKS_DIR = os.path.join(ROOT, "books")
os.makedirs(BOOKS_DIR, exist_ok=True)

# ---------- Fonts ----------
def load_font(size, bold=False):
    # Try common macOS fonts first, then fall back.
    try_paths = [
        ("/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        ("/System/Library/Fonts/Supplemental/Helvetica.ttc"),
        ("/System/Library/Fonts/SFNS.ttf"),
    ]
    for p in try_paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

# ---------- Drawing Helpers ----------
def draw_centered_text(d, text, box, font, fill):
    x0,y0,x1,y1 = box
    w,h = d.textbbox((0,0), text, font=font)[2:]
    cx = x0 + (x1-x0 - w)//2
    cy = y0 + (y1-y0 - h)//2
    d.text((cx, cy), text, font=font, fill=fill)

def wrap_text_by_width(d, text, font, max_width_px):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=font) <= max_width_px:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_paragraph(d, text, x, y, width, font, line_gap=0, fill=(30,30,30)):
    lines = wrap_text_by_width(d, text, font, width)
    lh = int(font.size*1.15)
    cy = y
    for ln in lines:
        d.text((x, cy), ln, font=font, fill=fill)
        cy += lh + line_gap
    return cy

# ---------- Simple Illustrations (cute, high-contrast) ----------
def art_spider(d, cx, cy, scale=1.0):
    # body
    body_r = int(60*scale)
    d.ellipse((cx-body_r, cy-body_r, cx+body_r, cy+body_r), fill=(60,60,60))
    # eyes
    er = int(12*scale)
    d.ellipse((cx-24*scale-er, cy-10*scale-er, cx-24*scale+er, cy-10*scale+er), fill=(255,255,255))
    d.ellipse((cx+24*scale-er, cy-10*scale-er, cx+24*scale+er, cy-10*scale+er), fill=(255,255,255))
    d.ellipse((cx-24*scale-4, cy-10*scale-2, cx-24*scale+2, cy-10*scale+4), fill=(0,0,0))
    d.ellipse((cx+24*scale-4, cy-10*scale-2, cx+24*scale+2, cy-10*scale+4), fill=(0,0,0))
    # legs
    leg_len = int(100*scale)
    for i in range(4):
        # left
        y = cy - 30*scale + i*20*scale
        d.line((cx- body_r, y, cx- body_r - leg_len, y - 20*scale), fill=(60,60,60), width=int(8*scale))
        # right
        d.line((cx+ body_r, y, cx+ body_r + leg_len, y - 20*scale), fill=(60,60,60), width=int(8*scale))

def art_web(d, cx, cy, r, rings=5, spokes=12, color=(255,140,0)):
    d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=color, width=6)
    for k in range(1, rings):
        rr = int(r*k/rings)
        d.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), outline=color, width=3)
    for s in range(spokes):
        ang = 2*math.pi*s/spokes
        x = cx + int(r*math.cos(ang))
        y = cy + int(r*math.sin(ang))
        d.line((cx, cy, x, y), fill=color, width=3)

def art_world(d, box):
    x0,y0,x1,y1 = box
    w = x1-x0; h = y1-y0
    r = min(w,h)//2 - 8
    cx = x0 + w//2; cy = y0 + h//2
    d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(190,235,255), outline=(0,120,200), width=6)
    # Simple "landmasses"
    d.polygon([(cx- r//2, cy-10), (cx- r//3, cy-40), (cx, cy-20), (cx- r//4, cy+20)], fill=(120,200,120))
    d.polygon([(cx+ r//3, cy+10), (cx+ r//2, cy+30), (cx+ r//4, cy+50), (cx+ r//5, cy+10)], fill=(120,200,120))
    # Antarctica "brr!"
    d.arc((cx-r, cy-r, cx+r, cy+r), 180, 360, fill=(255,255,255), width=10)

def art_bug_scene(d, box):
    x0,y0,x1,y1 = box
    # background panel
    d.rectangle(box, fill=(255,240,246))
    # draw a bunch of bugs (good/avoid)
    import random
    for _ in range(12):
        x = random.randint(x0+20, x1-20)
        y = random.randint(y0+20, y1-20)
        good = random.random() < 0.7
        color = (85,239,196) if good else (253,121,168)
        d.ellipse((x-14, y-14, x+14, y+14), fill=color)
        # eyes
        d.ellipse((x-6, y-4, x-2, y), fill=(20,20,20))
        d.ellipse((x+2, y-4, x+6, y), fill=(20,20,20))

def art_spinnerets(d, cx, cy, scale=1.0):
    # abdomen end
    w = int(220*scale); h = int(140*scale)
    d.ellipse((cx-w//2, cy-h//2, cx+w//2, cy+h//2), fill=(80,80,80))
    # spinnerets
    for dx in (-40, 0, 40):
        d.rectangle((cx+dx-8, cy+ h//2-40, cx+dx+8, cy+h//2+20), fill=(120,120,120))
        d.line((cx+dx, cy+h//2+20, cx+dx+120, cy+h//2+60), fill=(240,200,120), width=6)

def art_baby_ballooning(d, box):
    x0,y0,x1,y1 = box
    d.rectangle(box, fill=(230,255,255))
    # spiderlings + silk lines
    for i in range(6):
        sx = x0 + 40 + i*((x1-x0-80)//5)
        sy = y0 + 40 + (i%3)*40
        d.line((sx, sy, sx, sy+140), fill=(220,220,220), width=3)
        art_spider(d, sx, sy+170, scale=0.35)

def art_size_compare(d, box):
    x0,y0,x1,y1 = box
    d.rectangle(box, fill=(255,255,240))
    # plate
    d.ellipse((x0+30, y0+30, x0+230, y0+230), outline=(120,120,120), width=6)
    art_spider(d, x0+130, y0+130, scale=0.9)
    # sprinkle + tiny spider
    d.rectangle((x1-180, y0+60, x1-40, y0+200), outline=(200,200,200), width=6)
    d.ellipse((x1-120-6, y0+130-6, x1-120+6, y0+130+6), fill=(255,99,132))
    art_spider(d, x1-120, y0+160, scale=0.25)

def art_camouflage(d, box):
    x0,y0,x1,y1 = box
    d.rectangle(box, fill=(245,255,245))
    # flower
    cx = x0 + (x1-x0)//4; cy = y0 + (y1-y0)//2
    for ang in range(0,360,30):
        r=80
        x=cx+int(r*math.cos(math.radians(ang)))
        y=cy+int(r*math.sin(math.radians(ang)))
        d.ellipse((x-30,y-30,x+30,y+30), fill=(255,200,210))
    d.ellipse((cx-25,cy-25,cx+25,cy+25), fill=(255,220,120))
    # crab spider blended as petal
    art_spider(d, cx+10, cy-10, scale=0.35)
    # leaf blend
    d.polygon([(x1-240,y0+80),(x1-40,y0+140),(x1-240,y0+200)], fill=(170,220,140))
    art_spider(d, x1-140, y0+150, scale=0.35)

def art_quiz_show(d, box):
    x0,y0,x1,y1 = box
    d.rectangle(box, fill=(235,245,255))
    # stage arch
    d.arc((x0+20,y0+20,x1-20,y1-20), 180, 360, fill=(150,150,255), width=14)
    # podiums
    for i in range(3):
        px = x0 + 60 + i*((x1-x0-180)//2)
        d.rectangle((px, y1-140, px+140, y1-40), fill=(255,200,130), outline=(120,60,0), width=4)
    # host
    art_spider(d, x0+ (x1-x0)//2, y0+140, scale=0.6)

def art_web_types(d, box):
    x0,y0,x1,y1 = box
    w = (x1-x0)//3 - 20
    h = (y1-y0) - 20
    panels = [
        (x0+10, y0+10, x0+10+w, y0+10+h),
        (x0+20+w, y0+10, x0+20+2*w, y0+10+h),
        (x0+30+2*w, y0+10, x0+30+3*w, y0+10+h),
    ]
    fills = [(230,255,250),(250,240,255),(255,250,230)]
    for i,p in enumerate(panels):
        d.rectangle(p, fill=fills[i])
    # orb
    bx = panels[0]
    cx = (bx[0]+bx[2])//2; cy = (bx[1]+bx[3])//2
    art_web(d, cx, cy, min(bx[2]-bx[0], bx[3]-bx[1])//2 - 16, 5, 10, color=(0,150,220))
    # funnel
    bx = panels[1]
    d.rectangle(bx, outline=(200,140,0), width=6)
    d.polygon([(bx[0]+20, bx[1]+20), (bx[2]-20, bx[1]+20), (bx[2]-80, bx[3]-20), (bx[0]+80, bx[3]-20)], outline=(200,140,0), width=4)
    # sheet
    bx = panels[2]
    d.rectangle(bx, outline=(120,180,120), width=6)
    for y in range(bx[1]+20, bx[3]-10, 16):
        d.line((bx[0]+20, y, bx[2]-20, y), fill=(120,180,120), width=3)

# Map page index -> art function
def draw_art_for_page(d, box, idx):
    # default: friendly spider
    mapping = {
        1: lambda: (art_web(d, (box[0]+box[2])//2, (box[1]+box[3])//2, min(box[2]-box[0], box[3]-box[1])//2 - 20, color=(255,140,0))),
        2: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        3: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        4: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.1),
        5: lambda: art_spinnerets(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        6: lambda: art_web_types(d, box),
        7: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2 - 40, 0.8),
        8: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.2),
        9: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        10: lambda: art_spider(d, (box[0]+box[2])//2 - 80, (box[1]+box[3])//2, 0.7),
        11: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        12: lambda: art_spider(d, (box[0]+box[2])//2 - 120, (box[1]+box[3])//2, 0.7),
        13: lambda: art_web(d, (box[0]+box[2])//2, (box[1]+box[3])//2, min(box[2]-box[0], box[3]-box[1])//2 - 20, color=(0,120,200)),
        14: lambda: art_web(d, (box[0]+box[2])//2 - 60, (box[1]+box[3])//2, 120, color=(200,160,60)),
        15: lambda: art_spider(d, (box[0]+box[2])//2 + 40, (box[1]+box[3])//2, 0.9),
        16: lambda: art_baby_ballooning(d, box),
        17: lambda: art_bug_scene(d, box),
        18: lambda: art_size_compare(d, box),
        19: lambda: art_camouflage(d, box),
        20: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        21: lambda: art_world(d, box),
        22: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 0.9),
        23: lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0),
        24: lambda: art_quiz_show(d, box),
        25: lambda: art_web(d, (box[0]+box[2])//2, (box[1]+box[3])//2, min(box[2]-box[0], box[3]-box[1])//2 - 20, color=(255,200,60)),
    }
    (mapping.get(idx) or (lambda: art_spider(d, (box[0]+box[2])//2, (box[1]+box[3])//2, 1.0)))()

# ---------- Book Content (same topics; friendlier, shorter body lines) ----------
PAGES = [
    ("Cover", "Spiders! Eight Legs of Awesome.\nTagline: Eight legs. Endless surprises."),
    ("Introduction", "Some people say “Eek!” at spiders. Not you! You’re about to discover how amazing they really are."),
    ("Body Parts", "Two body parts: cephalothorax (head+chest) and abdomen (tummy)."),
    ("Eight Legs", "Eight legs help spiders move fast, climb, and hang upside-down!"),
    ("Silk Factory", "Silk comes from tiny nozzles called spinnerets at the tip of the abdomen."),
    ("Web Wonders", "Orb webs, funnel webs, sheet webs—each spider has a style."),
    ("Jumping Spiders", "Daredevils! Some jump 50× their body length."),
    ("Tarantulas", "Big and fluffy. Gentle to people, fierce to bugs."),
    ("Black Widow", "Red hourglass = danger. Look, don’t touch."),
    ("Daddy Longlegs", "Surprise: not true spiders—still arachnids!"),
    ("Spider Vision", "Many have eight eyes. Some see great, others… not so much."),
    ("Hunters vs Trappers", "Hunters chase prey. Trappers wait in webs."),
    ("Spider Senses", "They feel tiny vibrations through their legs—like a phone buzz."),
    ("Super Silk Uses", "Silk makes egg sacs, sleeping bags, and safety ropes."),
    ("Baby Spiders", "Spiderlings hatch—and sometimes balloon on silk!"),
    ("Helpful, Not Harmful", "Most spiders are harmless helpers that eat pests."),
    ("Record Breakers", "Biggest: Goliath birdeater. Smallest: Samoan moss spider."),
    ("Camouflage Masters", "Some look like flowers, leaves, or sticks."),
    ("Super Strong Silk", "Stronger than steel of the same thickness—and stretchy!"),
    ("Spiders Everywhere", "They live almost everywhere… except Antarctica."),
    ("Myth Busting", "Myth: Spiders crawl into your mouth at night. Truth: Nope!"),
    ("Famous Spiders", "Charlotte, Anansi, and more—spiders star in stories."),
    ("You + Spiders", "Pause and watch a web. You might be amazed."),
    ("Quiz Time", "1) Do all spiders make webs?\n2) How many legs?\n3) What makes silk?"),
    ("The End", "Small creatures, big jobs. You’re a spider expert now!")
]

# ---------- Layout + Render ----------
def make_book(path, size_px):
    W, H = size_px
    DPI = 300

    # Kid-friendly sizes (scaled by page size)
    titleF = load_font(int(0.09*min(W,H)), bold=True)   # ~90–110 pt
    bodyF  = load_font(int(0.055*min(W,H)))            # ~48–56 pt
    smallF = load_font(int(0.035*min(W,H)))            # ~30–36 pt

    margin = int(0.07 * min(W,H))  # safe margin
    gutter = int(0.03 * min(W,H))

    pages = []
    for idx, (p_title, p_body) in enumerate(PAGES, start=1):
        img = Image.new("RGB", (W, H), (255,255,255))
        d = ImageDraw.Draw(img)

        # Header
        d.text((margin, margin), p_title, font=titleF, fill=(20,20,20))

        # Art area: LARGE right panel
        art_left   = int(W*0.48)
        art_top    = int(margin*1.2)
        art_right  = W - margin
        art_bottom = H - margin
        # soft panel bg
        d.rectangle((art_left, art_top, art_right, art_bottom), fill=(255,248,230), outline=(255,160,0), width=6)

        # Draw art by page index
        draw_art_for_page(d, (art_left+14, art_top+14, art_right-14, art_bottom-14), idx)

        # Body text: left column, BIG letters
        col_x = margin
        col_y = int(margin*2.0)
        col_w = int(W*0.46) - margin
        draw_paragraph(d, p_body, col_x, col_y, col_w, bodyF, line_gap=int(bodyF.size*0.15))

        # Footer
        d.text((margin, H - margin - smallF.size), f"Page {idx}", font=smallF, fill=(120,120,120))

        pages.append(img)

    pages[0].save(path, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    print("Wrote", path)

if __name__ == "__main__":
    # 8.5" x 8.5" @ 300DPI -> 2550 x 2550
    make_book(os.path.join(BOOKS_DIR, "Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf"), (2550,2550))
    # 8" x 10" @ 300DPI -> 2400 x 3000
    make_book(os.path.join(BOOKS_DIR, "Spiders_Eight_Legs_of_Awesome_8x10.pdf"), (2400,3000))
    print("All done. Replace the PDFs in /books and refresh your site.")
