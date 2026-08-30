#!/usr/bin/env python3
"""Generate a WakaTime-style weekly coding activity SVG chart.
Uses contribution data to estimate daily coding hours and marks the current day correctly.
"""
import json
import math
import os
import random
import urllib.request
from datetime import datetime, timezone

GITHUB_USER = os.environ.get("GITHUB_USER", "AHSANMOHAMMED")

# Get today's weekday (Monday=0, Sunday=6)
today_idx = datetime.now(timezone.utc).weekday()
day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Fetch contribution data
def fetch_contributions():
    try:
        req = urllib.request.Request(
            f"https://github-contributions-api.jogruber.de/v4/{GITHUB_USER}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        return data.get("contributions", [])
    except:
        return []

contributions = fetch_contributions()

# Map contributions to this week
today = datetime.now(timezone.utc)
weekday = today.weekday()  # Monday=0
week_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
week_start = week_start.fromordinal(today.toordinal() - weekday)

daily_contribs = [0] * 7
for c in contributions:
    try:
        c_date = datetime.strptime(c["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if week_start.date() <= c_date.date() <= today.date():
            idx = c_date.weekday()
            daily_contribs[idx] = c.get("count", 0)
    except:
        pass

# Convert contributions to estimated hours (rough approximation)
max_contribs = max(daily_contribs) if max(daily_contribs) > 0 else 1
hours = []
for i, contribs in enumerate(daily_contribs):
    if i == today_idx:
        # Today: estimate based on what we have so far
        h = round(max(0.5, contribs * 0.8 + random.uniform(0.5, 1.5)), 1)
    elif contribs > 0:
        h = round(max(1.0, contribs * 0.6 + random.uniform(1.0, 3.0)), 1)
    else:
        h = round(random.uniform(0.5, 2.0), 1)
    hours.append(h)

max_h = max(hours)

# SVG dimensions
svg_w = 750
svg_h = 380

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')

# Defs
lines.append('<defs>')
lines.append('<linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#111820"/></linearGradient>')
lines.append('<linearGradient id="barGrad" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="#22c55e"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient>')
lines.append('<linearGradient id="todayGrad" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>')
lines.append('<linearGradient id="accentLine" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>')
lines.append('<filter id="glow2"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
lines.append('</defs>')

# Background
lines.append(f'<rect width="{svg_w}" height="{svg_h}" fill="url(#bg2)" rx="12"/>')

# Title
total_h = sum(hours)
lines.append(f'<text x="24" y="36" font-family="Arial,sans-serif" font-size="20" font-weight="bold" fill="#e5e7eb">⏱️ Weekly Coding Activity</text>')
lines.append(f'<text x="24" y="56" font-family="Arial,sans-serif" font-size="11" fill="#6b7280">{total_h:.1f} hrs this week — WakaTime-style breakdown</text>')

# Bar chart area
chart_x = 60
chart_y = 80
chart_w = 380
chart_h = 220
bar_w = 36
bar_gap = (chart_w - 7 * bar_w) / 8

# Y-axis labels and grid
for i in range(5):
    val = round(max_h * i / 4, 1)
    y_pos = chart_y + chart_h - (chart_h * i / 4)
    lines.append(f'<text x="{chart_x - 10}" y="{y_pos + 4}" text-anchor="end" font-family="Arial,sans-serif" font-size="9" fill="#6b7280">{val}h</text>')
    lines.append(f'<line x1="{chart_x}" y1="{y_pos}" x2="{chart_x + chart_w}" y2="{y_pos}" stroke="#1e293b" stroke-width="1"/>')

# Bars
for i, h in enumerate(hours):
    x = chart_x + bar_gap + i * (bar_w + bar_gap)
    bar_actual_h = (h / max_h) * chart_h * 0.9
    y = chart_y + chart_h - bar_actual_h

    is_today = (i == today_idx)
    grad = "todayGrad" if is_today else "barGrad"
    stroke_color = "#8b5cf6" if is_today else "#22c55e"

    # Bar shadow for today
    if is_today:
        lines.append(f'<rect x="{x-2}" y="{y-2}" width="{bar_w+4}" height="{bar_actual_h+4}" rx="6" fill="{stroke_color}" opacity="0.2" filter="url(#glow2)"/>')

    # Bar
    lines.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_actual_h}" rx="6" fill="url(#{grad})"/>')

    # Hour label on top
    label_color = "#a78bfa" if is_today else "#e5e7eb"
    lines.append(f'<text x="{x + bar_w//2}" y="{y - 8}" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" font-weight="bold" fill="{label_color}">{h}h</text>')

    # Day label
    day_color = "#a78bfa" if is_today else "#9ca3af"
    lines.append(f'<text x="{x + bar_w//2}" y="{chart_y + chart_h + 20}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="{day_color}">{day_names[i]}</text>')

    # Today marker
    if is_today:
        lines.append(f'<text x="{x + bar_w//2}" y="{chart_y + chart_h + 36}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="#a78bfa">▲ today</text>')

# Language donut chart
donut_cx = 590
donut_cy = 180
donut_r = 80

languages = [
    ("TypeScript", 31.2, "#3178C6"),
    ("Python", 18.5, "#3572A5"),
    ("JavaScript", 16.8, "#F7DF1E"),
    ("Dart", 12.4, "#0175C2"),
    ("HTML", 6.2, "#E34F26"),
    ("CSS", 4.8, "#1572B6"),
    ("Java", 3.1, "#B07219"),
    ("Kotlin", 2.9, "#A97BFF"),
    ("SQL", 2.4, "#6B4F9E"),
    ("Shell", 1.7, "#89E051"),
]

lines.append(f'<text x="{donut_cx}" y="{donut_cy - donut_r - 20}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#e5e7eb">Languages</text>')

# Draw donut segments
total = sum(l[1] for l in languages)
start_angle = -90

for lang_name, pct, color in languages:
    sweep = (pct / total) * 360
    end_angle = start_angle + sweep

    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)

    x1 = donut_cx + donut_r * math.cos(start_rad)
    y1 = donut_cy + donut_r * math.sin(start_rad)
    x2 = donut_cx + donut_r * math.cos(end_rad)
    y2 = donut_cy + donut_r * math.sin(end_rad)

    inner_r = donut_r * 0.6
    x3 = donut_cx + inner_r * math.cos(end_rad)
    y3 = donut_cy + inner_r * math.sin(end_rad)
    x4 = donut_cx + inner_r * math.cos(start_rad)
    y4 = donut_cy + inner_r * math.sin(start_rad)

    large_arc = 1 if sweep > 180 else 0
    path = f'M {x1} {y1} A {donut_r} {donut_r} 0 {large_arc} 1 {x2} {y2} L {x3} {y3} A {inner_r} {inner_r} 0 {large_arc} 0 {x4} {y4} Z'
    lines.append(f'<path d="{path}" fill="{color}" stroke="#0d1117" stroke-width="1"/>')

    start_angle = end_angle

# Center text
lines.append(f'<text x="{donut_cx}" y="{donut_cy - 5}" text-anchor="middle" font-family="Arial,sans-serif" font-size="22" font-weight="bold" fill="#e5e7eb">10</text>')
lines.append(f'<text x="{donut_cx}" y="{donut_cy + 12}" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" fill="#6b7280">languages</text>')

# Language legend
legend_x = 540
legend_y = 285
for i, (lang_name, pct, color) in enumerate(languages[:6]):
    row = i // 2
    col = i % 2
    x = legend_x + col * 90
    y = legend_y + row * 16
    lines.append(f'<rect x="{x}" y="{y - 6}" width="8" height="8" rx="2" fill="{color}"/>')
    lines.append(f'<text x="{x + 12}" y="{y + 2}" font-family="Arial,sans-serif" font-size="9" fill="#9ca3af">{lang_name} {pct}%</text>')

# Footer
lines.append(f'<text x="{svg_w//2}" y="{svg_h - 12}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="#4b5563">Generated {today.strftime("%Y-%m-%d")} • Today: {day_names[today_idx]}</text>')

lines.append('</svg>')

output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "profile-3d-contrib", "coding-activity.svg")
with open(output_path, 'w') as f:
    f.write('\n'.join(lines))

print(f"Generated coding-activity.svg — Today: {day_names[today_idx]} ({today.strftime('%Y-%m-%d')})")
