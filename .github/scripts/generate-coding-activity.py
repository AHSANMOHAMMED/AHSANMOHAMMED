#!/usr/bin/env python3
"""Generate glassmorphism-styled coding activity SVG."""
import math
from datetime import datetime, timezone

svg_w = 600
svg_h = 280

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
lines.append('<defs>')
# Gradients
lines.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0a0e14"/><stop offset="100%" stop-color="#111820"/></linearGradient>')
lines.append('<linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>')
lines.append('<linearGradient id="bar-grad" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="#06b6d4" stop-opacity="0.3"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>')
lines.append('<linearGradient id="donut-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#06b6d4"/><stop offset="50%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient>')
# Glassmorphism filters
lines.append('<filter id="glow"><feGaussianBlur stdDeviation="2.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
lines.append('<filter id="soft-glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
lines.append('<filter id="shadow"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity="0.4"/></filter>')
lines.append('</defs>')

# Background
lines.append(f'<rect width="{svg_w}" height="{svg_h}" fill="url(#bg)" rx="16"/>')

# Animated blobs for glassmorphism depth
lines.append(f'<circle cx="80" cy="80" r="100" fill="#06b6d4" opacity="0.04"><animate attributeName="r" values="100;120;100" dur="8s" repeatCount="indefinite"/></circle>')
lines.append(f'<circle cx="{svg_w-80}" cy="{svg_h-80}" r="80" fill="#8b5cf6" opacity="0.04"><animate attributeName="r" values="80;100;80" dur="10s" repeatCount="indefinite"/></circle>')

# Top accent
lines.append(f'<rect x="0" y="0" width="{svg_w}" height="3" rx="1.5" fill="url(#accent)" filter="url(#soft-glow)"/>')

# Title
lines.append(f'<text x="{svg_w//2}" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="bold" fill="#06b6d4" filter="url(#glow)">⏱️ Weekly Coding Activity</text>')

# Glassmorphism bar chart section
chart_x, chart_y, chart_w, chart_h = 30, 50, 300, 180
lines.append(f'<rect x="{chart_x}" y="{chart_y}" width="{chart_w}" height="{chart_h}" rx="12" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.06)" stroke-width="1" filter="url(#shadow)"/>')
lines.append(f'<rect x="{chart_x}" y="{chart_y}" width="{chart_w}" height="{chart_h//3}" rx="12" fill="rgba(255,255,255,0.02)"/>')

today_idx = datetime.now(timezone.utc).weekday()
day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
hours_data = [
    (6.5, "#06b6d4"), (7.2, "#22d3ee"), (5.8, "#3b82f6"),
    (8.1, "#8b5cf6"), (4.5, "#a78bfa"), (3.2, "#6366f1"),
    (2.0, "#06b6d4")
]
max_h = max(h for h, _ in hours_data)

# Grid lines
for i in range(4):
    gy = chart_y + chart_h - 30 - (i * (chart_h-50) // 3)
    lines.append(f'<line x1="{chart_x+10}" y1="{gy}" x2="{chart_x+chart_w-10}" y2="{gy}" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>')
    lines.append(f'<text x="{chart_x+8}" y="{gy+4}" text-anchor="end" font-family="Arial,sans-serif" font-size="9" fill="#475569">{int(max_h * i / 3)}h</text>')

# Bars
bar_w_each = (chart_w - 40) // 7
for i, (hours, color) in enumerate(hours_data):
    bx = chart_x + 20 + i * bar_w_each
    bar_actual_h = int((hours / max_h) * (chart_h - 60))
    by = chart_y + chart_h - 25 - bar_actual_h
    
    is_today = (i == today_idx)
    
    if is_today:
        lines.append(f'<rect x="{bx}" y="{by}" width="{bar_w_each-8}" height="{bar_actual_h}" rx="6" fill="{color}" opacity="0.9" filter="url(#glow)">')
        lines.append(f'<animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/></rect>')
    else:
        lines.append(f'<rect x="{bx}" y="{by}" width="{bar_w_each-8}" height="{bar_actual_h}" rx="6" fill="{color}" opacity="0.5"/>')
    
    # Day label
    label_color = "#06b6d4" if is_today else "#64748b"
    lines.append(f'<text x="{bx+(bar_w_each-8)//2}" y="{chart_y+chart_h-10}" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" fill="{label_color}" font-weight="{"bold" if is_today else "normal"}">{day_names[i]}</text>')
    
    if is_today:
        lines.append(f'<text x="{bx+(bar_w_each-8)//2}" y="{by-6}" text-anchor="middle" font-family="Arial,sans-serif" font-size="8" fill="#06b6d4" filter="url(#glow)">▲ today</text>')

# Language donut section (glass card)
donut_cx, donut_cy = 460, 140
donut_r, donut_inner = 55, 35
lines.append(f'<rect x="355" y="50" width="230" height="180" rx="12" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.06)" stroke-width="1" filter="url(#shadow)"/>')
lines.append(f'<rect x="355" y="50" width="230" height="60" rx="12" fill="rgba(255,255,255,0.02)"/>')
lines.append(f'<text x="{donut_cx}" y="72" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="#94a3b8">Top Languages</text>')

languages = [
    ("TypeScript", 31, "#3178C6"), ("Python", 19, "#3572A5"),
    ("JavaScript", 17, "#F7DF1E"), ("Dart", 12, "#0175C2"),
    ("HTML", 8, "#E34F26"), ("CSS", 5, "#1572B6"),
    ("Other", 8, "#8b949e"),
]

start_angle = -90
for lang_name, pct, color in languages:
    angle = pct * 3.6
    end_angle = start_angle + angle
    large_arc = 1 if angle > 180 else 0
    
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    
    x1_out = donut_cx + donut_r * math.cos(start_rad)
    y1_out = donut_cy + donut_r * math.sin(start_rad)
    x2_out = donut_cx + donut_r * math.cos(end_rad)
    y2_out = donut_cy + donut_r * math.sin(end_rad)
    
    x1_in = donut_cx + donut_inner * math.cos(end_rad)
    y1_in = donut_cy + donut_inner * math.sin(end_rad)
    x2_in = donut_cx + donut_inner * math.cos(start_rad)
    y2_in = donut_cy + donut_inner * math.sin(start_rad)
    
    path = f'M{x1_out},{y1_out} A{donut_r},{donut_r} 0 {large_arc},1 {x2_out},{y2_out} L{x1_in},{y1_in} A{donut_inner},{donut_inner} 0 {large_arc},0 {x2_in},{y2_in} Z'
    lines.append(f'<path d="{path}" fill="{color}" opacity="0.85" stroke="#0a0e14" stroke-width="1"/>')
    start_angle = end_angle

lines.append(f'<text x="{donut_cx}" y="{donut_cy+4}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#e2e8f0">10</text>')
lines.append(f'<text x="{donut_cx}" y="{donut_cy+16}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="#64748b">languages</text>')

# Legend (glass pills)
legend_x = 370
for i, (lang_name, pct, color) in enumerate(languages[:5]):
    ly = 155 + i * 14
    lines.append(f'<rect x="{legend_x}" y="{ly-10}" width="10" height="10" rx="3" fill="{color}" opacity="0.8"/>')
    lines.append(f'<text x="{legend_x+14}" y="{ly}" font-family="Arial,sans-serif" font-size="9" fill="#94a3b8">{lang_name} {pct}%</text>')

lines.append('</svg>')

output_path = "/Users/ahsan/Documents/AHSANMOHAMMED-main/profile-3d-contrib/coding-activity.svg"
with open(output_path, 'w') as f:
    f.write('\n'.join(lines))
print(f"✅ Glassmorphism coding-activity.svg")
