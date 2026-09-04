#!/usr/bin/env python3
"""Generate glassmorphism-styled repo activity heatmap SVG."""
import json
import os
import urllib.request

USERNAME = os.environ.get("GITHUB_USER", "AHSANMOHAMMED")

def fetch_repos(username):
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except:
        return []

repos = fetch_repos(USERNAME)
repos.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
repos = repos[:12]

lang_colors = {
    "TypeScript": "#3178C6", "JavaScript": "#F7DF1E", "Python": "#3572A5",
    "Dart": "#0175C2", "HTML": "#E34F26", "CSS": "#1572B6", "Java": "#B07219",
    "Kotlin": "#A97BFF", "Shell": "#89E051", "Unknown": "#8b949e",
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

svg_w = 600
row_h = 78
header_h = 80
footer_h = 50
total_h = header_h + len(repos) * row_h + footer_h

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {total_h}" width="{svg_w}" height="{total_h}">')
lines.append('<defs>')
# Glassmorphism filters
lines.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0a0e14"/><stop offset="50%" stop-color="#111820"/><stop offset="100%" stop-color="#0d1117"/></linearGradient>')
lines.append('<linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>')
lines.append('<linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#fbbf24"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient>')
# Glassmorphism blur filter
lines.append('<filter id="glass-blur"><feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur"/><feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.18 0" result="glass"/></filter>')
# Glow effect
lines.append('<filter id="glow"><feGaussianBlur stdDeviation="2.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
lines.append('<filter id="soft-glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
# Shadow
lines.append('<filter id="shadow"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.4"/></filter>')
lines.append('</defs>')

# Background
lines.append(f'<rect width="{svg_w}" height="{total_h}" fill="url(#bg)" rx="16"/>')

# Animated background blobs for glassmorphism depth
lines.append(f'<circle cx="100" cy="100" r="120" fill="#06b6d4" opacity="0.04"><animate attributeName="cx" values="100;120;100" dur="8s" repeatCount="indefinite"/></circle>')
lines.append(f'<circle cx="{svg_w-100}" cy="{total_h-100}" r="100" fill="#8b5cf6" opacity="0.04"><animate attributeName="cy" values="{total_h-100};{total_h-120};{total_h-100}" dur="10s" repeatCount="indefinite"/></circle>')
lines.append(f'<circle cx="{svg_w//2}" cy="{total_h//2}" r="150" fill="#3b82f6" opacity="0.02"><animate attributeName="r" values="150;170;150" dur="12s" repeatCount="indefinite"/></circle>')

# Top accent line with glow
lines.append(f'<rect x="0" y="0" width="{svg_w}" height="3" rx="1.5" fill="url(#accent)" filter="url(#soft-glow)"/>')

# Title with glow
lines.append(f'<text x="{svg_w//2}" y="42" text-anchor="middle" font-family="Arial,sans-serif" font-size="22" font-weight="bold" fill="#06b6d4" filter="url(#glow)">📦 Repository Activity</text>')
lines.append(f'<text x="{svg_w//2}" y="62" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#64748b">{USERNAME} — {len(repos)} recent repositories</text>')

intensity_colors = [
    ("#064e3b", "#065f46"),
    ("#047857", "#059669"),
    ("#10b981", "#34d399"),
    ("#06b6d4", "#22d3ee"),
    ("#8b5cf6", "#a78bfa"),
    ("#f59e0b", "#fbbf24"),
]

max_updated = max((r.get('updated_at', '') for r in repos), default='2024-01-01')

for idx, repo in enumerate(repos):
    y = header_h + idx * row_h
    name = repo.get('name', 'unknown')
    if len(name) > 28:
        name = name[:26] + "…"
    desc = repo.get('description', '') or ''
    if len(desc) > 55:
        desc = desc[:53] + "…"
    lang = repo.get('language') or 'Unknown'
    lang_color = lang_colors.get(lang, "#8b949e")
    stars = repo.get('stargazers_count', 0)
    forks = repo.get('forks_count', 0)
    updated = (repo.get('updated_at', '')[:10])

    updated_ts = repo.get('updated_at', '2024-01-01T00:00:00Z')
    try:
        days_ago = idx * 7
    except:
        days_ago = 30
    intensity = min(max(0, 1 - days_ago / 90), 1.0)

    color_idx = min(int(intensity * (len(intensity_colors) - 1)), len(intensity_colors) - 1)
    c1, c2 = intensity_colors[color_idx]

    # Glassmorphism card: frosted glass background
    card_x, card_y, card_w, card_h = 14, y+4, svg_w-28, row_h-8
    lines.append(f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="12" fill="{c1}" fill-opacity="0.2" stroke="rgba(255,255,255,0.08)" stroke-width="1" filter="url(#shadow)"/>')
    # Inner highlight (glass reflection)
    lines.append(f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h//2}" rx="12" fill="rgba(255,255,255,0.03)"/>')
    
    # Activity bar with glass effect
    bar_w = int(8 + intensity * 36)
    lines.append(f'<rect x="{card_x+8}" y="{card_y+8}" width="{bar_w}" height="{card_h-16}" rx="6" fill="{c2}" opacity="0.7" filter="url(#glow)"/>')

    # Repo name
    lines.append(f'<text x="{card_x+20+bar_w}" y="{card_y+22}" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#60a5fa" filter="url(#glow)">{esc(name)}</text>')

    # Description
    if desc:
        lines.append(f'<text x="{card_x+20+bar_w}" y="{card_y+40}" font-family="Arial,sans-serif" font-size="10" fill="#94a3b8">{esc(desc)}</text>')

    # Language badge (glass pill)
    lang_x = card_x + 20 + bar_w
    lang_y = card_y + 50 if desc else card_y + 44
    badge_w = len(lang) * 7 + 24
    lines.append(f'<rect x="{lang_x-4}" y="{lang_y-12}" width="{badge_w}" height="18" rx="9" fill="rgba(255,255,255,0.05)" stroke="{lang_color}" stroke-opacity="0.4" stroke-width="1"/>')
    lines.append(f'<circle cx="{lang_x+6}" cy="{lang_y-3}" r="3.5" fill="{lang_color}"/>')
    lines.append(f'<text x="{lang_x+16}" y="{lang_y}" font-family="Arial,sans-serif" font-size="10" fill="#d1d5db">{esc(lang)}</text>')

    if stars > 0:
        lines.append(f'<text x="{lang_x+badge_w+10}" y="{lang_y}" font-family="Arial,sans-serif" font-size="10" fill="#fbbf24" filter="url(#glow)">⭐ {stars}</text>')

    # Date
    lines.append(f'<text x="{card_x+card_w-12}" y="{card_y+22}" text-anchor="end" font-family="Arial,sans-serif" font-size="9" fill="#475569">{updated}</text>')

# Footer
footer_y = total_h - 30
lines.append(f'<rect x="14" y="{footer_y-16}" width="{svg_w-28}" height="1" fill="url(#accent)" opacity="0.2"/>')
lines.append(f'<text x="{svg_w//2}" y="{footer_y+8}" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" fill="#475569">Activity: Brighter colors = More recent · Glassmorphism UI ✨</text>')

lines.append('</svg>')

output_path = "/Users/ahsan/Documents/AHSANMOHAMMED-main/profile-3d-contrib/repo-heatmap.svg"
with open(output_path, 'w') as f:
    f.write('\n'.join(lines))
print(f"✅ Glassmorphism repo-heatmap.svg — {len(repos)} repos")
