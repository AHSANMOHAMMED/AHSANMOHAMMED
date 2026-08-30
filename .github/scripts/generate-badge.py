#!/usr/bin/env python3
"""Generate a 'latest commit' SVG badge with commit hash and date."""

import subprocess
import sys

def get_latest_commit():
    """Get the latest commit hash and date from git."""
    hash_result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True
    )
    date_result = subprocess.run(
        ["git", "log", "-1", "--format=%cd", "--date=short"],
        capture_output=True, text=True
    )
    return hash_result.stdout.strip(), date_result.stdout.strip()

def generate_svg(commit_hash, commit_date):
    """Generate SVG badge content."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="340" height="28" role="img" aria-label="latest commit: {commit_hash}">
  <title>latest commit: {commit_hash}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="340" height="28" rx="5" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="120" height="28" fill="#1e293b"/>
    <rect x="120" width="220" height="28" fill="#0ea5e9"/>
    <rect width="340" height="28" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="60" y="18" fill="#06b6d4" font-weight="bold">latest commit</text>
    <text x="230" y="18" fill="#fff" font-weight="bold">{commit_hash}</text>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="9">
    <text x="230" y="26" fill="#e0f2fe" opacity="0.85">{commit_date}</text>
  </g>
</svg>'''

def main():
    commit_hash, commit_date = get_latest_commit()
    svg_content = generate_svg(commit_hash, commit_date)

    output_path = "latest-commit.svg"
    with open(output_path, "w") as f:
        f.write(svg_content)

    print(f"Badge generated: {commit_hash} ({commit_date})")

if __name__ == "__main__":
    main()
