# -*- coding: utf-8 -*-
"""
Helper functions to generate clean, inline SVGs for the visual questions in Cloud Computing quiz.
"""

def generate_elasticity_svg(variant):
    # variant in ['A', 'B', 'C', 'D']
    # 0 to 12 time, 0 to 60 servers
    # Dimensions: 220 x 140
    # X mapping: 35 to 205 (width 170) -> 0 to 12 (14.16 px per unit)
    # Y mapping: 115 (0 servers) to 25 (60 servers) (height 90 -> 1.5 px per server)
    
    paths = {
        'A': 'M 35 40 L 92 40 L 92 100 L 148 100 L 148 40 L 205 40', # starts 50, dips to 10 (t=4..8), back to 50
        'B': 'M 35 40 L 205 40',                                       # flat at 50
        'C': 'M 35 100 L 85 100 L 85 40 L 155 40 L 155 100 L 205 100', # starts 10, surges to 50 (t=3.5..8.5), drops to 10
        'D': 'M 35 100 L 205 100'                                      # flat at 10
    }
    
    d = paths.get(variant, paths['C'])
    
    return f'''<svg viewBox="0 0 230 145" class="quiz-chart-svg" style="max-width:210px; height:auto; display:block; margin:6px auto;">
      <rect width="230" height="145" rx="6" fill="var(--bg-secondary, #131d31)" stroke="var(--border-color, #263554)" stroke-width="1"/>
      <!-- Grid lines -->
      <line x1="35" y1="25" x2="210" y2="25" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="40" x2="210" y2="40" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="70" x2="210" y2="70" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="100" x2="210" y2="100" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <!-- Axes -->
      <line x1="35" y1="20" x2="35" y2="115" stroke="var(--text-muted, #94a3b8)" stroke-width="1.5"/>
      <line x1="35" y1="115" x2="215" y2="115" stroke="var(--text-muted, #94a3b8)" stroke-width="1.5"/>
      <!-- Y-ticks & labels -->
      <text x="30" y="44" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="end">50</text>
      <text x="30" y="104" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="end">10</text>
      <text x="30" y="118" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="end">0</text>
      <text x="12" y="70" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="middle" transform="rotate(-90, 12, 70)">Servers</text>
      <!-- X-ticks & labels -->
      <text x="35" y="128" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="middle">0</text>
      <text x="92" y="128" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="middle">4</text>
      <text x="148" y="128" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="middle">8</text>
      <text x="205" y="128" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="middle">12</text>
      <text x="120" y="140" font-size="9" fill="var(--text-muted, #94a3b8)" text-anchor="middle">Time</text>
      <!-- Curve Line -->
      <path d="{d}" fill="none" stroke="#3b82f6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>'''


def generate_cost_barchart_svg(cloud_val, trad_val):
    # Max height: 100 = 85px. 0 = 105px.
    # Dimensions: 200 x 140
    # Y axis: 0 to 100
    y_cloud = 105 - (cloud_val * 0.8)
    h_cloud = cloud_val * 0.8
    y_trad = 105 - (trad_val * 0.8)
    h_trad = trad_val * 0.8
    
    return f'''<svg viewBox="0 0 210 145" class="quiz-chart-svg" style="max-width:190px; height:auto; display:block; margin:6px auto;">
      <rect width="210" height="145" rx="6" fill="var(--bg-secondary, #131d31)" stroke="var(--border-color, #263554)" stroke-width="1"/>
      <!-- Grid -->
      <line x1="35" y1="25" x2="195" y2="25" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="57" x2="195" y2="57" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="105" x2="195" y2="105" stroke="var(--border-subtle, #1c2a44)"/>
      <!-- Axes -->
      <line x1="35" y1="20" x2="35" y2="105" stroke="var(--text-muted, #94a3b8)" stroke-width="1.5"/>
      <line x1="35" y1="105" x2="195" y2="105" stroke="var(--text-muted, #94a3b8)" stroke-width="1.5"/>
      <text x="30" y="28" font-size="8.5" fill="var(--text-muted, #94a3b8)" text-anchor="end">100</text>
      <text x="30" y="60" font-size="8.5" fill="var(--text-muted, #94a3b8)" text-anchor="end">50</text>
      <text x="30" y="108" font-size="8.5" fill="var(--text-muted, #94a3b8)" text-anchor="end">0</text>
      <text x="12" y="65" font-size="8" fill="var(--text-muted, #94a3b8)" text-anchor="middle" transform="rotate(-90, 12, 65)">Cost</text>
      <!-- Bars -->
      <!-- Cloud Bar (Blue) -->
      <rect x="58" y="{y_cloud:.1f}" width="42" height="{h_cloud:.1f}" rx="2" fill="#3b82f6"/>
      <text x="79" y="{y_cloud - 4:.1f}" font-size="9" font-weight="bold" fill="var(--text-main, #f8fafc)" text-anchor="middle">{cloud_val}</text>
      <text x="79" y="120" font-size="9" fill="var(--text-sub, #cbd5e1)" text-anchor="middle">Cloud</text>
      <!-- Traditional Bar (Orange) -->
      <rect x="128" y="{y_trad:.1f}" width="42" height="{h_trad:.1f}" rx="2" fill="#f97316"/>
      <text x="149" y="{y_trad - 4:.1f}" font-size="9" font-weight="bold" fill="var(--text-main, #f8fafc)" text-anchor="middle">{trad_val}</text>
      <text x="149" y="120" font-size="9" fill="var(--text-sub, #cbd5e1)" text-anchor="middle">Trad.</text>
    </svg>'''


def generate_ram_barchart_svg(before_val, after_val):
    # Max height: 20 GB = 80px. 0 = 105px.
    # 4px per GB.
    y_before = 105 - (before_val * 4)
    h_before = before_val * 4
    y_after = 105 - (after_val * 4)
    h_after = after_val * 4
    
    return f'''<svg viewBox="0 0 210 145" class="quiz-chart-svg" style="max-width:190px; height:auto; display:block; margin:6px auto;">
      <rect width="210" height="145" rx="6" fill="var(--bg-secondary, #131d31)" stroke="var(--border-color, #263554)" stroke-width="1"/>
      <line x1="35" y1="25" x2="195" y2="25" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="65" x2="195" y2="65" stroke="var(--border-subtle, #1c2a44)" stroke-dasharray="3,3"/>
      <line x1="35" y1="105" x2="195" y2="105" stroke="var(--border-subtle, #1c2a44)"/>
      <line x1="35" y1="20" x2="35" y2="105" stroke="var(--text-muted, #94a3b8)" stroke-width="1.5"/>
      <line x1="35" y1="105" x2="195" y2="105" stroke="var(--text-muted, #94a3b8)" stroke-width="1.5"/>
      <text x="30" y="28" font-size="8.5" fill="var(--text-muted, #94a3b8)" text-anchor="end">20</text>
      <text x="30" y="68" font-size="8.5" fill="var(--text-muted, #94a3b8)" text-anchor="end">10</text>
      <text x="30" y="108" font-size="8.5" fill="var(--text-muted, #94a3b8)" text-anchor="end">0</text>
      <text x="12" y="65" font-size="8" fill="var(--text-muted, #94a3b8)" text-anchor="middle" transform="rotate(-90, 12, 65)">RAM (GB)</text>
      <!-- Before -->
      <rect x="58" y="{y_before:.1f}" width="42" height="{h_before:.1f}" rx="2" fill="#0284c7"/>
      <text x="79" y="{y_before - 4:.1f}" font-size="9" font-weight="bold" fill="var(--text-main, #f8fafc)" text-anchor="middle">{before_val}</text>
      <text x="79" y="120" font-size="9" fill="var(--text-sub, #cbd5e1)" text-anchor="middle">Before</text>
      <!-- After -->
      <rect x="128" y="{y_after:.1f}" width="42" height="{h_after:.1f}" rx="2" fill="#ea580c"/>
      <text x="149" y="{y_after - 4:.1f}" font-size="9" font-weight="bold" fill="var(--text-main, #f8fafc)" text-anchor="middle">{after_val}</text>
      <text x="149" y="120" font-size="9" fill="var(--text-sub, #cbd5e1)" text-anchor="middle">After</text>
    </svg>'''


def generate_subnet_diagram_svg(public_items, private_items):
    pub_txt = " + ".join(public_items) if public_items else "(Empty)"
    priv_txt = " + ".join(private_items) if private_items else "(Empty)"
    
    return f'''<div class="subnet-card" style="display:flex; gap:8px; margin:6px auto; max-width:240px;">
      <div style="flex:1; background:rgba(16, 185, 129, 0.15); border:1.5px solid #10b981; border-radius:6px; padding:8px 4px; text-align:center;">
        <div style="font-size:0.7rem; font-weight:bold; color:#10b981; text-transform:uppercase;">Public Subnet</div>
        <div style="font-size:0.8rem; font-weight:600; color:var(--text-main, #f8fafc); margin-top:4px;">{pub_txt}</div>
      </div>
      <div style="flex:1; background:rgba(239, 68, 68, 0.15); border:1.5px solid #ef4444; border-radius:6px; padding:8px 4px; text-align:center;">
        <div style="font-size:0.7rem; font-weight:bold; color:#ef4444; text-transform:uppercase;">Private Subnet</div>
        <div style="font-size:0.8rem; font-weight:600; color:var(--text-main, #f8fafc); margin-top:4px;">{priv_txt}</div>
      </div>
    </div>'''


def generate_pie_3sector_svg(title, seg1_label, seg1_color, seg2_label, seg2_color, seg3_label, seg3_color):
    # Generates a 3-sector pie chart (120 deg each)
    # Circle center (70, 70), r = 50
    # Sector 1: -90 deg to 30 deg
    # Sector 2: 30 deg to 150 deg
    # Sector 3: 150 deg to 270 deg (-90 deg)
    # Angles in rad:
    # 0 = top: (70, 20)
    # 120 = bottom-right: 70 + 50*sin(120)=113.3, 70 - 50*cos(120)=95
    # 240 = bottom-left: 70 + 50*sin(240)=26.7, 70 - 50*cos(240)=95
    return f'''<div style="text-align:center; margin:6px auto; max-width:220px;">
      <svg viewBox="0 0 140 140" style="width:110px; height:110px; margin:0 auto; display:block;">
        <!-- Sector 1 (Top-Right) -->
        <path d="M 70 70 L 70 20 A 50 50 0 0 1 113.3 95 Z" fill="{seg1_color}"/>
        <!-- Sector 2 (Bottom) -->
        <path d="M 70 70 L 113.3 95 A 50 50 0 0 1 26.7 95 Z" fill="{seg2_color}"/>
        <!-- Sector 3 (Top-Left) -->
        <path d="M 70 70 L 26.7 95 A 50 50 0 0 1 70 20 Z" fill="{seg3_color}"/>
      </svg>
      <div style="font-size:0.75rem; text-align:left; margin-top:4px; display:inline-block;">
        <div><span style="color:{seg1_color}">●</span> {seg1_label}</div>
        <div><span style="color:{seg2_color}">●</span> {seg2_label}</div>
        <div><span style="color:{seg3_color}">●</span> {seg3_label}</div>
      </div>
    </div>'''


def generate_pie_4sector_svg(seg1_label, seg1_color, seg2_label, seg2_color, seg3_label, seg3_color, seg4_label, seg4_color):
    # Generates a 4-sector pie chart (90 deg each)
    # Circle center (70, 70), r = 50
    return f'''<div style="text-align:center; margin:6px auto; max-width:220px;">
      <svg viewBox="0 0 140 140" style="width:110px; height:110px; margin:0 auto; display:block;">
        <!-- Sector 1: Top-Right (0 to 90) -->
        <path d="M 70 70 L 70 20 A 50 50 0 0 1 120 70 Z" fill="{seg1_color}"/>
        <!-- Sector 2: Bottom-Right (90 to 180) -->
        <path d="M 70 70 L 120 70 A 50 50 0 0 1 70 120 Z" fill="{seg2_color}"/>
        <!-- Sector 3: Bottom-Left (180 to 270) -->
        <path d="M 70 70 L 70 120 A 50 50 0 0 1 20 70 Z" fill="{seg3_color}"/>
        <!-- Sector 4: Top-Left (270 to 360) -->
        <path d="M 70 70 L 20 70 A 50 50 0 0 1 70 20 Z" fill="{seg4_color}"/>
      </svg>
      <div style="font-size:0.72rem; text-align:left; margin-top:4px; display:inline-block;">
        <div><span style="color:{seg1_color}">●</span> {seg1_label}</div>
        <div><span style="color:{seg2_color}">●</span> {seg2_label}</div>
        <div><span style="color:{seg3_color}">●</span> {seg3_label}</div>
        <div><span style="color:{seg4_color}">●</span> {seg4_label}</div>
      </div>
    </div>'''

print("Diagram generators defined successfully.")
