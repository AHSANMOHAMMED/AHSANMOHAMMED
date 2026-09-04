#!/usr/bin/env python3
"""Generate a 3D isometric GitHub Skyline city with glassmorphism styling."""
import json, math, random, urllib.request
from datetime import datetime, timedelta

USERNAME = "AHSANMOHAMMED"

def fetch_contributions(username):
    try:
        end = datetime.now()
        url = f"https://github-contributions-api.jogruber.de/v4/{username}?y={end.year}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        return data.get("contributions", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

contributions = fetch_contributions(USERNAME)
if not contributions:
    exit(1)

total = sum(c["count"] for c in contributions)
max_count = max(c["count"] for c in contributions) if contributions else 1
print(f"📊 {USERNAME} — {total} contributions, max {max_count}/day")

def iso(x, y, z):
    return (x - y) * 0.866, (x + y) * 0.5 - z

svg_w, svg_h = 700, 420
cols, rows = 52, 7
cell_w, cell_h = 10, 10
max_bh = 40
offset_x = svg_w // 2 + 60
offset_y = 220

base_colors = [(13,17,23),(6,78,59),(4,120,87),(16,185,129),(6,182,212),(139,92,246),(245,158,11),(239,68,68)]
top_colors = [(20,30,40),(10,100,75),(8,150,105),(30,210,155),(30,200,235),(170,130,255),(255,185,50),(255,100,100)]
right_colors = [(8,12,18),(4,55,42),(3,90,65),(12,140,100),(5,140,170),(110,70,200),(200,125,10),(200,50,50)]

def get_cidx(count, mc):
    if count == 0: return 0
    r = count / max(mc, 1)
    if r < 0.1: return 1
    if r < 0.25: return 2
    if r < 0.45: return 3
    if r < 0.65: return 4
    if r < 0.8: return 5
    if r < 0.95: return 6
    return 7

L = []
L.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
L.append('<defs>')
L.append('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0a0e14"/><stop offset="40%" stop-color="#111820"/><stop offset="100%" stop-color="#0d1117"/></linearGradient>')
L.append('<linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>')
L.append('<filter id="glow"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
L.append('<filter id="soft-glow"><feGaussianBlur stdDeviation="3.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
L.append('<filter id="bglow"><feGaussianBlur stdDeviation="1.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
L.append('<filter id="shadow"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.5"/></filter>')
L.append('<linearGradient id="ground" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="rgba(6,182,212,0.08)"/><stop offset="100%" stop-color="rgba(139,92,246,0.05)"/></linearGradient>')
L.append('</defs>')

L.append(f'<rect width="{svg_w}" height="{svg_h}" fill="url(#sky)" rx="16"/>')
L.append(f'<circle cx="150" cy="100" r="140" fill="#06b6d4" opacity="0.03"><animate attributeName="cx" values="150;180;150" dur="10s" repeatCount="indefinite"/></circle>')
L.append(f'<circle cx="{svg_w-150}" cy="{svg_h-100}" r="120" fill="#8b5cf6" opacity="0.03"><animate attributeName="cy" values="{svg_h-100};{svg_h-130};{svg_h-100}" dur="12s" repeatCount="indefinite"/></circle>')
L.append(f'<circle cx="{svg_w//2}" cy="80" r="100" fill="#f59e0b" opacity="0.02"><animate attributeName="r" values="100;130;100" dur="8s" repeatCount="indefinite"/></circle>')
L.append(f'<rect x="0" y="0" width="{svg_w}" height="3" rx="1.5" fill="url(#accent)" filter="url(#soft-glow)"/>')
L.append(f'<text x="{svg_w//2}" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="bold" fill="#06b6d4" filter="url(#glow)">🏙️ GitHub Skyline — {USERNAME}</text>')
L.append(f'<text x="{svg_w//2}" y="48" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#64748b">{total} contributions this year — Each building is a day</text>')

random.seed(42)
for _ in range(40):
    sx, sy = random.randint(20, svg_w-20), random.randint(55, 100)
    sr = random.uniform(0.5, 1.5)
    op = random.uniform(0.2, 0.7)
    dur = random.uniform(2, 6)
    L.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#fff" opacity="{op}"><animate attributeName="opacity" values="{op};0.1;{op}" dur="{dur:.1f}s" repeatCount="indefinite"/></circle>')

gp = []
for x in range(0, cols+2):
    px, py = iso((x - cols/2) * cell_w, (rows/2 + 1) * cell_h, 0)
    gp.append(f"{offset_x + px:.1f},{offset_y + py:.1f}")
for x in range(cols+1, -1, -1):
    px, py = iso((x - cols/2) * cell_w, (-rows/2 - 1) * cell_h, 0)
    gp.append(f"{offset_x + px:.1f},{offset_y + py:.1f}")
L.append(f'<polygon points="{" ".join(gp)}" fill="url(#ground)" stroke="rgba(6,182,212,0.1)" stroke-width="0.5"/>')

for g in range(0, cols+1, 4):
    x1, y1 = iso((g - cols/2) * cell_w, (-rows/2 - 1) * cell_h, 0)
    x2, y2 = iso((g - cols/2) * cell_w, (rows/2 + 1) * cell_h, 0)
    L.append(f'<line x1="{offset_x+x1:.1f}" y1="{offset_y+y1:.1f}" x2="{offset_x+x2:.1f}" y2="{offset_y+y2:.1f}" stroke="rgba(6,182,212,0.06)" stroke-width="0.5"/>')
for g in range(0, rows+2):
    x1, y1 = iso((-cols/2 - 1) * cell_w, g * cell_h, 0)
    x2, y2 = iso((cols/2 + 1) * cell_w, g * cell_h, 0)
    L.append(f'<line x1="{offset_x+x1:.1f}" y1="{offset_y+y1:.1f}" x2="{offset_x+x2:.1f}" y2="{offset_y+y2:.1f}" stroke="rgba(6,182,212,0.06)" stroke-width="0.5"/>')

mnames = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
shown = set()
for wi in range(0, cols, 4):
    gi = wi * 7
    if gi < len(contributions):
        month = int(contributions[gi]["date"].split("-")[1])
        if month > 0 and month not in shown:
            shown.add(month)
            mx, my = iso((wi - cols/2) * cell_w, (rows/2 + 2) * cell_h, 0)
            L.append(f'<text x="{offset_x+mx:.1f}" y="{offset_y+my+8:.1f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="8" fill="#475569">{mnames[month]}</text>')

dlabels = ["","Mon","","Wed","","Fri",""]
for d in range(rows):
    if dlabels[d]:
        dx, dy = iso((-cols/2 - 2) * cell_w, d * cell_h, 0)
        L.append(f'<text x="{offset_x+dx:.1f}" y="{offset_y+dy+4:.1f}" text-anchor="end" font-family="Arial,sans-serif" font-size="7" fill="#475569">{dlabels[d]}</text>')

bgeoms = []
for wi in range(cols):
    for di in range(rows):
        gi = wi * 7 + di
        if gi >= len(contributions): break
        c = contributions[gi]["count"]
        h = max(1, int((c / max(max_count, 1)) * max_bh)) if c > 0 else 0
        bx = (wi - cols/2) * cell_w
        by = (di - rows/2) * cell_h
        bgeoms.append((wi, di, bx, by, h, get_cidx(c, max_count), c))

bgeoms.sort(key=lambda b: b[1] + b[0])
hw, hh = cell_w * 0.45, cell_h * 0.45

for wi, di, bx, by, ht, ci, cnt in bgeoms:
    if ht <= 0: continue
    fc, tc, rc = base_colors[ci], top_colors[ci], right_colors[ci]
    t1 = iso(bx-hw, by-hh, ht)
    t2 = iso(bx+hw, by-hh, ht)
    t3 = iso(bx+hw, by+hh, ht)
    t4 = iso(bx-hw, by+hh, ht)
    l1 = iso(bx-hw, by+hh, ht)
    l4 = iso(bx-hw, by+hh, 0)
    r1 = iso(bx+hw, by-hh, ht)
    r2 = iso(bx+hw, by+hh, ht)
    r3 = iso(bx+hw, by+hh, 0)
    r4 = iso(bx+hw, by-hh, 0)
    ox, oy = offset_x, offset_y
    L.append(f'<polygon points="{ox+t1[0]:.1f},{oy+t1[1]:.1f} {ox+t4[0]:.1f},{oy+t4[1]:.1f} {ox+l4[0]:.1f},{oy+l4[1]:.1f} {ox+l1[0]:.1f},{oy+l1[1]:.1f}" fill="rgb{fc}" stroke="rgba(255,255,255,0.04)" stroke-width="0.3"/>')
    L.append(f'<polygon points="{ox+r1[0]:.1f},{oy+r1[1]:.1f} {ox+r2[0]:.1f},{oy+r2[1]:.1f} {ox+r3[0]:.1f},{oy+r3[1]:.1f} {ox+r4[0]:.1f},{oy+r4[1]:.1f}" fill="rgb{rc}" stroke="rgba(255,255,255,0.04)" stroke-width="0.3"/>')
    L.append(f'<polygon points="{ox+t1[0]:.1f},{oy+t1[1]:.1f} {ox+t2[0]:.1f},{oy+t2[1]:.1f} {ox+t3[0]:.1f},{oy+t3[1]:.1f} {ox+t4[0]:.1f},{oy+t4[1]:.1f}" fill="rgb{tc}" stroke="rgba(255,255,255,0.08)" stroke-width="0.5"/>')
    if cnt >= max_count * 0.6:
        L.append(f'<polygon points="{ox+t1[0]:.1f},{oy+t1[1]:.1f} {ox+t2[0]:.1f},{oy+t2[1]:.1f} {ox+t3[0]:.1f},{oy+t3[1]:.1f} {ox+t4[0]:.1f},{oy+t4[1]:.1f}" fill="rgba(255,255,255,0.12)"/>')
    if cnt >= max_count * 0.7:
        gcx = (t1[0]+t3[0])/2
        gcy = (t1[1]+t3[1])/2
        L.append(f'<circle cx="{ox+gcx:.1f}" cy="{oy+gcy:.1f}" r="3" fill="rgb{tc}" opacity="0.3" filter="url(#bglow)"/>')

lx, ly = svg_w-130, svg_h-65
L.append(f'<rect x="{lx}" y="{ly}" width="120" height="55" rx="8" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.06)" stroke-width="1" filter="url(#shadow)"/>')
L.append(f'<text x="{lx+60}" y="{ly+16}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" font-weight="bold" fill="#94a3b8">Activity Level</text>')
for i, (c, lb) in enumerate([(base_colors[1],"Low"),(base_colors[3],"Med"),(base_colors[5],"High"),(base_colors[7],"Peak")]):
    lxx = lx + 10 + i * 28
    L.append(f'<rect x="{lxx}" y="{ly+28}" width="14" height="14" rx="3" fill="rgb{c}" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/>')
    L.append(f'<text x="{lxx+7}" y="{ly+50}" text-anchor="middle" font-family="Arial,sans-serif" font-size="7" fill="#64748b">{lb}</text>')

L.append(f'<text x="{svg_w//2}" y="{svg_h-8}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="#475569">Each building height = daily contributions · Glassmorphism 3D ✨</text>')
L.append('</svg>')

with open("/Users/ahsan/Documents/AHSANMOHAMMED-main/profile-3d-contrib/github-skyline.svg", 'w') as f:
    f.write('\n'.join(L))
print(f"✅ Glassmorphism GitHub Skyline — {total} contributions, {len(bgeoms)} buildings")
