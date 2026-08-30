#!/usr/bin/env python3
"""Generate all profile SVGs from live GitHub contribution data."""
import json
import urllib.request
import math
import random
import os
from datetime import datetime, timedelta

USERNAME = os.environ.get("GITHUB_USER", "AHSANMOHAMMED")

def fetch_contributions(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read()).get("contributions", [])

def lerp(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

def get_contrib_colors(count, mx):
    if count == 0: return "#161b22","#0d1117","#0a0e14"
    t = min(count/max(mx,1),1.0)
    if t < 0.5:
        return lerp("#0e4429","#26a641",t*2), lerp("#1a5c35","#39d353",t*2), lerp("#0a3020","#1a7a30",t*2)
    return lerp("#26a641","#06b6d4",(t-0.5)*2), lerp("#39d353","#22d3ee",(t-0.5)*2), lerp("#1a7a30","#0891b2",(t-0.5)*2)

def get_building_colors(count, mx):
    return get_contrib_colors(count, mx)

# ===== 1. CONTRIBUTION CALENDAR SVG =====
def gen_contrib_calendar(contributions, username):
    weeks = {}
    for c in contributions:
        d = datetime.strptime(c["date"], "%Y-%m-%d")
        wk = (d.year, d.isocalendar()[1])
        if wk not in weeks: weeks[wk] = {}
        weeks[wk][d.weekday()] = c.get("count", 0)
    sorted_weeks = sorted(weeks.keys())[-52:]
    mx = max((weeks.get(w,{}).get(d,0) for w in sorted_weeks for d in range(7)), default=1)

    cw, ch, dep, gap = 11, 11, 6, 2
    nw = len(sorted_weeks)
    gw = nw * (cw + gap)
    svg_w, svg_h = gw + 200, 7*(ch+gap) + 140
    total = sum(c.get("count",0) for c in contributions)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">']
    s.append('<defs>')
    s.append('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#161b22"/></linearGradient>')
    s.append('<filter id="glow-sm"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('<filter id="glow-lg"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('<filter id="pulse"><feGaussianBlur stdDeviation="2" result="b"><animate attributeName="stdDeviation" values="2;4;2" dur="3s" repeatCount="indefinite"/></feGaussianBlur><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('<linearGradient id="shimmer" x1="0" y1="0" x2="1" y2="1">')
    s.append('<stop offset="0%" stop-color="rgba(255,255,255,0)"><animate attributeName="offset" values="-0.5;1.5" dur="4s" repeatCount="indefinite"/></stop>')
    s.append('<stop offset="20%" stop-color="rgba(255,255,255,0.15)"><animate attributeName="offset" values="-0.3;1.7" dur="4s" repeatCount="indefinite"/></stop>')
    s.append('<stop offset="40%" stop-color="rgba(255,255,255,0)"><animate attributeName="offset" values="0;2" dur="4s" repeatCount="indefinite"/></stop>')
    s.append('</linearGradient></defs>')

    s.append(f'<rect width="{svg_w}" height="{svg_h}" fill="url(#bg)" rx="12"/>')
    s.append(f'<text x="{svg_w//2}" y="28" text-anchor="middle" fill="#58a6ff" font-family="Verdana,sans-serif" font-size="16" font-weight="bold">📊 Contribution Calendar<animate attributeName="opacity" values="1;0.7;1" dur="3s" repeatCount="indefinite"/></text>')
    s.append(f'<text x="{svg_w//2}" y="46" text-anchor="middle" fill="#8b949e" font-family="Verdana,sans-serif" font-size="11">{username} — {total} contributions</text>')

    sx, sy = 40, 65
    for i, l in enumerate(["","Mon","","Wed","","Fri",""]):
        if l: s.append(f'<text x="{sx-5}" y="{sy+i*(ch+gap)+ch//2+4}" text-anchor="end" fill="#8b949e" font-family="Verdana,sans-serif" font-size="9">{l}</text>')

    mn = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    lm = -1
    for wi, wk in enumerate(sorted_weeks):
        dt = datetime(wk[0],1,4) + timedelta(weeks=wk[1]-1, days=-datetime(wk[0],1,4).weekday())
        m = dt.month
        if m != lm and wi % 4 == 0:
            s.append(f'<text x="{sx+wi*(cw+gap)+cw//2}" y="{sy-5}" text-anchor="middle" fill="#8b949e" font-family="Verdana,sans-serif" font-size="9">{mn[m]}</text>')
            lm = m

    random.seed(42); ac = []; ad = 0
    for wi, wk in enumerate(sorted_weeks):
        for day in range(7):
            cnt = weeks.get(wk,{}).get(day,0)
            f2,t2,s2 = get_contrib_colors(cnt, mx)
            x = sx + wi*(cw+gap); y = sy + day*(ch+gap)
            filt = ' filter="url(#pulse)"' if cnt>=mx else (' filter="url(#glow-lg)"' if cnt>mx*0.6 else (' filter="url(#glow-sm)"' if cnt>0 else ''))
            if cnt > mx*0.6: ac.append((x,y,cnt,ad)); ad=(ad+0.7)%5
            tp = f"{x},{y} {x+cw},{y} {x+cw+dep},{y-dep} {x+dep},{y-dep}"
            s.append(f'<polygon points="{tp}" fill="{t2}" stroke="#30363d" stroke-width="0.5"/>')
            if cnt>mx*0.3: s.append(f'<polygon points="{tp}" fill="url(#shimmer)" opacity="0.4"/>')
            rp = f"{x+cw},{y} {x+cw+dep},{y-dep} {x+cw+dep},{y+ch-dep} {x+cw},{y+ch}"
            s.append(f'<polygon points="{rp}" fill="{s2}" stroke="#30363d" stroke-width="0.5"/>')
            s.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{f2}" stroke="#30363d" stroke-width="0.5" rx="1"{filt}/>')

    for x,y,cnt,d in ac[:15]:
        px,py = x+cw//2, y-5
        pc = "#39d353" if cnt<mx*0.8 else "#22d3ee"
        s.append(f'<circle cx="{px}" cy="{py}" r="1.5" fill="{pc}" opacity="0"><animate attributeName="cy" values="{py};{py-15};{py}" dur="2.5s" begin="{d:.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.8;0" dur="2.5s" begin="{d:.1f}s" repeatCount="indefinite"/></circle>')

    ly = sy + 7*(ch+gap) + 20
    s.append(f'<text x="{sx}" y="{ly}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="10">Less</text>')
    for i,c in enumerate(["#161b22","#0e4429","#006d32","#26a641","#39d353"]):
        s.append(f'<rect x="{sx+35+i*16}" y="{ly-10}" width="12" height="12" fill="{c}" rx="2" stroke="#30363d" stroke-width="0.5"/>')
    s.append(f'<text x="{sx+120}" y="{ly}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="10">More</text>')
    s.append(f'<text x="{svg_w-20}" y="{ly}" text-anchor="end" fill="#06b6d4" font-family="Verdana,sans-serif" font-size="9" opacity="0.7">● live<animate attributeName="opacity" values="0.7;0.3;0.7" dur="2s" repeatCount="indefinite"/></text>')
    s.append('</svg>')
    return '\n'.join(s)

# ===== 2. SKYLINE SVG =====
def gen_skyline(contributions, username):
    weeks = {}
    for c in contributions:
        d = datetime.strptime(c["date"], "%Y-%m-%d")
        wk = (d.year, d.isocalendar()[1])
        if wk not in weeks: weeks[wk] = {}
        weeks[wk][d.weekday()] = c.get("count", 0)
    sorted_weeks = sorted(weeks.keys())[-52:]
    mx = max((weeks.get(w,{}).get(d,0) for w in sorted_weeks for d in range(7)), default=1)

    cw, gap, mh, dep = 13, 3, 60, 7
    nw = len(sorted_weeks)
    gw = nw*(cw+gap)
    svg_w, svg_h = gw+160, mh+180
    total = sum(c.get("count",0) for c in contributions)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">']
    s.append('<defs>')
    s.append('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0a0e14"/><stop offset="60%" stop-color="#0d1117"/><stop offset="100%" stop-color="#161b22"/></linearGradient>')
    s.append('<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#21262d"/><stop offset="100%" stop-color="#161b22"/></linearGradient>')
    s.append('<filter id="glow"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('<filter id="glow-lg"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('<filter id="pulse"><feGaussianBlur stdDeviation="2" result="b"><animate attributeName="stdDeviation" values="2;5;2" dur="2.5s" repeatCount="indefinite"/></feGaussianBlur><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('<linearGradient id="shimmer" x1="0" y1="0" x2="1" y2="0">')
    s.append('<stop offset="0%" stop-color="rgba(255,255,255,0)"><animate attributeName="offset" values="-0.5;1.5" dur="3s" repeatCount="indefinite"/></stop>')
    s.append('<stop offset="15%" stop-color="rgba(255,255,255,0.2)"><animate attributeName="offset" values="-0.35;1.65" dur="3s" repeatCount="indefinite"/></stop>')
    s.append('<stop offset="30%" stop-color="rgba(255,255,255,0)"><animate attributeName="offset" values="-0.2;1.8" dur="3s" repeatCount="indefinite"/></stop>')
    s.append('</linearGradient></defs>')

    s.append(f'<rect width="{svg_w}" height="{svg_h}" fill="url(#sky)" rx="12"/>')
    random.seed(42)
    for _ in range(35):
        sx2,sy2,sr = random.randint(10,svg_w-10), random.randint(5,55), random.uniform(0.3,1.2)
        s.append(f'<circle cx="{sx2}" cy="{sy2}" r="{sr}" fill="#ffffff" opacity="0.5"><animate attributeName="opacity" values="0.2;0.9;0.2" dur="{random.uniform(2,5):.1f}s" begin="{random.uniform(0,3):.1f}s" repeatCount="indefinite"/></circle>')

    s.append(f'<text x="{svg_w//2}" y="28" text-anchor="middle" fill="#58a6ff" font-family="Verdana,sans-serif" font-size="16" font-weight="bold">🏙️ GitHub Skyline — {username}<animate attributeName="opacity" values="1;0.75;1" dur="4s" repeatCount="indefinite"/></text>')
    s.append(f'<text x="{svg_w//2}" y="46" text-anchor="middle" fill="#8b949e" font-family="Verdana,sans-serif" font-size="11">{total} contributions — Each building is a day</text>')

    stx, gy = 60, svg_h-60
    gp = f"{stx},{gy} {stx+gw+dep+20},{gy} {stx+gw+dep+20+dep},{gy-dep} {stx+dep},{gy-dep}"
    s.append(f'<polygon points="{gp}" fill="url(#ground)" stroke="#30363d" stroke-width="0.5"/>')

    pk = []
    for wi, wk in enumerate(sorted_weeks):
        for day in range(6,-1,-1):
            cnt = weeks.get(wk,{}).get(day,0)
            h = 2 if cnt==0 else max(8, int(cnt/mx*mh))
            x = stx+wi*(cw+gap); yb = gy-day*1; yt = yb-h
            f2,t2,s2 = get_building_colors(cnt, mx)
            fa = ' filter="url(#pulse)"' if cnt>=mx else (' filter="url(#glow-lg)"' if cnt>mx*0.6 else (' filter="url(#glow)"' if cnt>0 else ''))
            if cnt>=mx: pk.append((x,yt))
            sp = f"{x+cw},{yb} {x+cw+dep},{yb-dep} {x+cw+dep},{yt-dep} {x+cw},{yt}"
            s.append(f'<polygon points="{sp}" fill="{s2}" stroke="#30363d" stroke-width="0.3"/>')
            tp = f"{x},{yt} {x+cw},{yt} {x+cw+dep},{yt-dep} {x+dep},{yt-dep}"
            s.append(f'<polygon points="{tp}" fill="{t2}" stroke="#30363d" stroke-width="0.3"/>')
            if cnt>mx*0.3: s.append(f'<polygon points="{tp}" fill="url(#shimmer)" opacity="0.35"/>')
            s.append(f'<rect x="{x}" y="{yt}" width="{cw}" height="{h}" fill="{f2}" stroke="#30363d" stroke-width="0.3" rx="1"{fa}/>')

    for i,(bx,byt) in enumerate(pk[:5]):
        d=i*0.8; px=bx+cw//2
        s.append(f'<circle cx="{px}" cy="{byt}" r="1.5" fill="#22d3ee" opacity="0"><animate attributeName="cy" values="{byt};{byt-20};{byt}" dur="3s" begin="{d:.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" dur="3s" begin="{d:.1f}s" repeatCount="indefinite"/></circle>')

    for bx,byt in pk[:3]:
        cx=bx+cw//2
        s.append(f'<circle cx="{cx}" cy="{byt}" r="3" fill="none" stroke="#22d3ee" stroke-width="0.8" opacity="0"><animate attributeName="r" values="3;15;3" dur="2.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.7;0;0.7" dur="2.5s" repeatCount="indefinite"/></circle>')

    s.append(f'<line x1="{stx}" y1="{gy}" x2="{stx}" y2="{gy-mh-10}" stroke="#06b6d4" stroke-width="1" opacity="0"><animate attributeName="x1" values="{stx};{stx+gw};{stx}" dur="10s" repeatCount="indefinite"/><animate attributeName="x2" values="{stx};{stx+gw};{stx}" dur="10s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.4;0" dur="10s" repeatCount="indefinite"/></line>')

    for i,l in enumerate(["","Mon","","Wed","","Fri",""]):
        if l: s.append(f'<text x="{stx-8}" y="{gy-i*1-3}" text-anchor="end" fill="#8b949e" font-family="Verdana,sans-serif" font-size="8">{l}</text>')

    mnn = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    lm=-1
    for wi,wk in enumerate(sorted_weeks):
        dt=datetime(wk[0],1,4)+timedelta(weeks=wk[1]-1,days=-datetime(wk[0],1,4).weekday())
        m=dt.month
        if m!=lm and wi%4==0:
            s.append(f'<text x="{stx+wi*(cw+gap)+cw//2}" y="{gy+16}" text-anchor="middle" fill="#8b949e" font-family="Verdana,sans-serif" font-size="8">{mnn[m]}</text>')
            lm=m

    ly=gy+35
    s.append(f'<text x="{stx}" y="{ly}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="9">Less</text>')
    for i,c in enumerate(["#161b22","#0e4429","#006d32","#26a641","#39d353","#06b6d4"]):
        s.append(f'<rect x="{stx+30+i*15}" y="{ly-9}" width="11" height="11" fill="{c}" rx="2" stroke="#30363d" stroke-width="0.3"/>')
    s.append(f'<text x="{stx+125}" y="{ly}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="9">More</text>')
    s.append(f'<text x="{svg_w-20}" y="{ly}" text-anchor="end" fill="#06b6d4" font-family="Verdana,sans-serif" font-size="9">● live<animate attributeName="opacity" values="0.8;0.3;0.8" dur="2s" repeatCount="indefinite"/></text>')
    s.append('</svg>')
    return '\n'.join(s)

# ===== MAIN =====
if __name__ == "__main__":
    print(f"Fetching contributions for {USERNAME}...")
    contributions = fetch_contributions(USERNAME)
    print(f"Got {len(contributions)} days of data")

    out_dir = "profile-3d-contrib"
    os.makedirs(out_dir, exist_ok=True)

    # Generate contribution calendar
    svg1 = gen_contrib_calendar(contributions, USERNAME)
    with open(f"{out_dir}/profile-season-animate.svg", "w") as f: f.write(svg1)
    print(f"✅ contribution calendar ({len(svg1)} bytes)")

    # Generate skyline
    svg2 = gen_skyline(contributions, USERNAME)
    with open(f"{out_dir}/github-skyline.svg", "w") as f: f.write(svg2)
    print(f"✅ skyline ({len(svg2)} bytes)")

    print("All SVGs generated successfully!")
