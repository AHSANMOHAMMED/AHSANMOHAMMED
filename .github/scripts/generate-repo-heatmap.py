#!/usr/bin/env python3
"""Generate a GitHub repository contribution heatmap SVG."""
import json
import urllib.request
import os
from datetime import datetime, timedelta

USERNAME = os.environ.get("GITHUB_USER", "AHSANMOHAMMED")

def fetch_repos(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=updated"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        if not data: break
        repos.extend(data)
        page += 1
        if len(data) < 100: break
    return repos

def fetch_contributions(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read()).get("contributions", [])

def lerp(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

LANG_COLORS = {
    "TypeScript": "#3178C6", "JavaScript": "#F7DF1E", "Python": "#3776AB",
    "Dart": "#0175C2", "HTML": "#E34F26", "CSS": "#1572B6", "Java": "#ED8B00",
    "Kotlin": "#7F52FF", "Swift": "#F05138", "Go": "#00ADD8", "Ruby": "#CC342D",
    "PHP": "#4F5D95", "C++": "#F34B7D", "C": "#555555", "Shell": "#89e051",
    "Vue": "#41B883", "Svelte": "#FF3E00", "Rust": "#DEA584", "Scala": "#DC322F",
    "Elixir": "#6E4A7E", "Haskell": "#5e5086", "Lua": "#000080",
    "Jupyter Notebook": "#DA5B0B", "MDX": "#FCB32C",
}

def get_color_for_lang(lang):
    return LANG_COLORS.get(lang, "#6e7681")

def calc_activity_score(repo):
    """Calculate activity score from stars, forks, open issues, and recency."""
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    issues = repo.get("open_issues_count", 0)
    updated = repo.get("updated_at", "2024-01-01")
    pushed = repo.get("pushed_at", "2024-01-01")
    
    # Recency score (days since last push)
    try:
        last_push = datetime.strptime(pushed[:10], "%Y-%m-%d")
        days_ago = (datetime.now() - last_push).days
        recency = max(0, 100 - days_ago)
    except:
        recency = 0
    
    return stars * 10 + forks * 5 + issues * 2 + recency

def generate_heatmap(repos, contributions, username):
    # Sort repos by activity score
    for r in repos:
        r["_score"] = calc_activity_score(r)
    repos.sort(key=lambda r: r["_score"], reverse=True)
    
    # Take top repos
    top_repos = [r for r in repos if not r.get("fork", False)][:20]
    max_score = max((r["_score"] for r in top_repos), default=1)
    
    # Contribution stats
    total_contribs = sum(c.get("count", 0) for c in contributions)
    
    # Colors for heatmap intensity
    def heat_color(score, max_s):
        t = min(score / max(max_s, 1), 1.0)
        if t < 0.2: return "#161b22", "#0d1117"
        if t < 0.4: return "#0e4429", "#1a5c35"
        if t < 0.6: return "#006d32", "#26a641"
        if t < 0.8: return "#26a641", "#39d353"
        return "#39d353", "#22d3ee"

    # Layout
    svg_w, svg_h = 820, 520
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    s.append('<defs>')
    s.append('<linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#161b22"/></linearGradient>')
    s.append('<filter id="hg"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s.append('</defs>')

    s.append(f'<rect width="{svg_w}" height="{svg_h}" fill="url(#hbg)" rx="12"/>')

    # Title
    s.append(f'<text x="20" y="28" fill="#58a6ff" font-family="Verdana,sans-serif" font-size="16" font-weight="bold">📦 Repository Activity Heatmap</text>')
    s.append(f'<text x="20" y="44" fill="#8b949e" font-family="Verdana,sans-serif" font-size="10">{username} — {len(repos)} repos • {total_contribs} total contributions</text>')

    # === HEATMAP GRID ===
    # 4 columns x 5 rows of repo cards
    cols, rows = 2, 10
    card_w, card_h = 380, 38
    card_gap_x, card_gap_y = 12, 6
    start_x, start_y = 20, 60

    for i, repo in enumerate(top_repos[:cols*rows]):
        row = i // cols
        col = i % cols
        
        x = start_x + col * (card_w + card_gap_x)
        y = start_y + row * (card_h + card_gap_y)
        
        score = repo["_score"]
        name = repo.get("name", "unknown")
        lang = repo.get("language") or "Unknown"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        issues = repo.get("open_issues_count", 0)
        desc = (repo.get("description") or "")[:45]
        pushed = repo.get("pushed_at", "")[:10]
        is_private = repo.get("private", False)
        
        heat, heat_dark = heat_color(score, max_score)
        lang_color = get_color_for_lang(lang)
        
        # Intensity bar (left edge)
        intensity = min(score / max(max_score, 1), 1.0)
        bar_h = card_h * intensity
        bar_y = y + card_h - bar_h
        s.append(f'<rect x="{x}" y="{bar_y}" width="4" height="{bar_h}" fill="{heat}" rx="2">')
        s.append(f'<animate attributeName="height" values="0;{bar_h}" dur="0.8s" begin="{i*0.05}s" fill="freeze"/>')
        s.append(f'<animate attributeName="y" values="{y+card_h};{bar_y}" dur="0.8s" begin="{i*0.05}s" fill="freeze"/>')
        s.append('</rect>')
        
        # Card background
        s.append(f'<rect x="{x+6}" y="{y}" width="{card_w-6}" height="{card_h}" fill="{heat_dark}" stroke="{heat}" stroke-width="0.5" rx="4" opacity="0.8">')
        s.append(f'<animate attributeName="opacity" values="0;0.8" dur="0.5s" begin="{i*0.05}s" fill="freeze"/>')
        s.append('</rect>')
        
        # Repo name
        name_display = name[:22] + ("..." if len(name) > 22 else "")
        s.append(f'<text x="{x+14}" y="{y+15}" fill="#58a6ff" font-family="Verdana,sans-serif" font-size="11" font-weight="bold">')
        if is_private: name_display = "🔒 " + name_display
        s.append(f'{name_display}</text>')
        
        # Description
        if desc:
            s.append(f'<text x="{x+14}" y="{y+28}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="8">{desc}</text>')
        
        # Language dot + name
        dot_x = x + card_w - 130
        s.append(f'<circle cx="{dot_x}" cy="{y+12}" r="4" fill="{lang_color}"/>')
        s.append(f'<text x="{dot_x+8}" y="{y+15}" fill="#e6edf3" font-family="Verdana,sans-serif" font-size="9">{lang}</text>')
        
        # Stats badges
        stats_x = x + card_w - 100
        s.append(f'<text x="{stats_x}" y="{y+15}" fill="#FFD700" font-family="Verdana,sans-serif" font-size="9">⭐{stars}</text>')
        s.append(f'<text x="{stats_x+45}" y="{y+15}" fill="#06b6d4" font-family="Verdana,sans-serif" font-size="9">🍴{forks}</text>')
        
        # Last updated
        if pushed:
            s.append(f'<text x="{x+card_w-12}" y="{y+15}" text-anchor="end" fill="#484f58" font-family="Verdana,sans-serif" font-size="7">{pushed}</text>')

    # === LEGEND ===
    ly = start_y + rows * (card_h + card_gap_y) + 15
    
    # Heatmap legend
    s.append(f'<text x="20" y="{ly}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="10">Activity Level:</text>')
    legend_colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    legend_labels = ["None", "Low", "Medium", "High", "Very High"]
    for i, (c, l) in enumerate(zip(legend_colors, legend_labels)):
        lx = 120 + i * 70
        s.append(f'<rect x="{lx}" y="{ly-9}" width="14" height="14" fill="{c}" rx="2" stroke="#30363d" stroke-width="0.5"/>')
        s.append(f'<text x="{lx+18}" y="{ly+2}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="8">{l}</text>')
    
    # Language color legend
    s.append(f'<text x="20" y="{ly+22}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="10">Languages:</text>')
    used_langs = list(dict.fromkeys(r.get("language", "Unknown") for r in top_repos[:10] if r.get("language")))
    for i, lang in enumerate(used_langs[:8]):
        lx = 100 + i * 85
        s.append(f'<circle cx="{lx}" cy="{ly+18}" r="4" fill="{get_color_for_lang(lang)}"/>')
        s.append(f'<text x="{lx+8}" y="{ly+21}" fill="#8b949e" font-family="Verdana,sans-serif" font-size="8">{lang}</text>')

    # Stats summary
    s.append(f'<text x="20" y="{ly+42}" fill="#484f58" font-family="Verdana,sans-serif" font-size="8">📊 Sorted by activity score (stars × 10 + forks × 5 + issues × 2 + recency) • Data from GitHub API</text>')
    
    # Live indicator
    s.append(f'<text x="{svg_w-20}" y="{ly+42}" text-anchor="end" fill="#06b6d4" font-family="Verdana,sans-serif" font-size="8">● live<animate attributeName="opacity" values="0.8;0.3;0.8" dur="2s" repeatCount="indefinite"/></text>')

    s.append('</svg>')
    return '\n'.join(s)

if __name__ == "__main__":
    print(f"Fetching repos for {USERNAME}...")
    repos = fetch_repos(USERNAME)
    print(f"Got {len(repos)} repos")
    
    print(f"Fetching contributions...")
    contributions = fetch_contributions(USERNAME)
    print(f"Got {len(contributions)} days")
    
    svg = generate_heatmap(repos, contributions, USERNAME)
    out = "profile-3d-contrib/repo-heatmap.svg"
    with open(out, "w") as f:
        f.write(svg)
    print(f"Generated: {out} ({len(svg)} bytes)")
