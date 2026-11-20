# -*- coding: utf-8 -*-
"""
Enriches cloud computing MCQs with diagrams and creates:
1. cloud_computing_mcqs_rich.json
2. all_subjects_mcqs.json (merged 180 MCQs)
"""
import json
from generate_diagram_assets import (
    generate_elasticity_svg,
    generate_cost_barchart_svg,
    generate_ram_barchart_svg,
    generate_subnet_diagram_svg,
    generate_pie_3sector_svg,
    generate_pie_4sector_svg
)

with open("cloud_computing_mcqs.json", "r", encoding="utf-8") as f:
    cc_list = json.load(f)

# Flow steps helper for Q5
def flow_html(steps):
    items = []
    for i, s in enumerate(steps):
        items.append(f'<span class="flow-node" style="display:inline-block; padding:2px 6px; background:var(--bg-primary, #0b1120); border:1px solid var(--border-color, #263554); border-radius:4px; font-size:0.75rem;">{s}</span>')
        if i < len(steps) - 1:
            items.append('<span style="color:var(--primary, #3b82f6); font-weight:bold; margin:0 3px;">↓</span>')
    return f'<div style="line-height:1.8; margin:4px 0;">{"".join(items)}</div>'

for q in cc_list:
    qid = q["id"]
    q["uid"] = f"CC-{qid}"
    
    if qid == 5:
        q["options"]["A"] = "Option A" + flow_html(["Personal Computers (PCs)", "Mainframe Computers", "Client-Server Computing", "Virtualization", "Data Centers", "Cloud Computing", "Modern Cloud / Cloud-Native"])
        q["options"]["B"] = "Option B" + flow_html(["Mainframe Computers", "Personal Computers (PCs)", "Client-Server Computing", "Data Centers", "Virtualization", "Cloud Computing", "Modern Cloud / Cloud-Native"])
        q["options"]["C"] = "Option C" + flow_html(["Mainframe Computers", "Client-Server Computing", "Personal Computers (PCs)", "Virtualization", "Cloud Computing", "Data Centers", "Modern Cloud / Cloud-Native"])
        q["options"]["D"] = "Option D" + flow_html(["Mainframe Computers", "Personal Computers (PCs)", "Client-Server Computing", "Virtualization", "Data Centers", "Cloud Computing", "Modern Cloud / Cloud-Native"])

    elif qid == 11:
        q["options"]["A"] = "<strong>Graph A</strong>" + generate_elasticity_svg('A')
        q["options"]["B"] = "<strong>Graph B</strong>" + generate_elasticity_svg('B')
        q["options"]["C"] = "<strong>Graph C</strong>" + generate_elasticity_svg('C')
        q["options"]["D"] = "<strong>Graph D</strong>" + generate_elasticity_svg('D')

    elif qid == 17:
        q["options"]["A"] = "<strong>Graph A</strong>" + generate_cost_barchart_svg(30, 90)
        q["options"]["B"] = "<strong>Graph B</strong>" + generate_cost_barchart_svg(60, 60)
        q["options"]["C"] = "<strong>Graph C</strong>" + generate_cost_barchart_svg(90, 90)
        q["options"]["D"] = "<strong>Graph D</strong>" + generate_cost_barchart_svg(90, 30)

    elif qid == 23:
        q["question"] = """The diagram shows the stack Hardware, Hypervisor, Guest OS, App (bottom to top). Which type of hypervisor is this?
<div class="arch-stack" style="max-width:240px; margin:14px auto 8px auto; text-align:center; font-weight:600; font-size:0.82rem; border-radius:6px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
  <div style="background:#3b82f6; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">App</div>
  <div style="background:#0284c7; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Guest OS</div>
  <div style="background:#059669; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Hypervisor</div>
  <div style="background:#475569; color:#fff; padding:6px;">Hardware</div>
</div>"""

    elif qid == 24:
        q["question"] = """The diagram shows Hardware, Operating System, Hypervisor, Guest OS, App (bottom to top). Which type of hypervisor is this?
<div class="arch-stack" style="max-width:240px; margin:14px auto 8px auto; text-align:center; font-weight:600; font-size:0.82rem; border-radius:6px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
  <div style="background:#3b82f6; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">App</div>
  <div style="background:#0284c7; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Guest OS</div>
  <div style="background:#d97706; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Hypervisor</div>
  <div style="background:#6366f1; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Operating System (Host OS)</div>
  <div style="background:#475569; color:#fff; padding:6px;">Hardware</div>
</div>"""

    elif qid == 28:
        q["question"] = """The diagram shows a Modified Guest OS above a Hypervisor. Which technique is this?
<div class="arch-stack" style="max-width:260px; margin:14px auto 8px auto; text-align:center; font-weight:600; font-size:0.82rem; border-radius:6px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
  <div style="background:#3b82f6; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">App</div>
  <div style="background:#8b5cf6; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Modified Guest OS (Aware of Hypervisor)</div>
  <div style="background:#059669; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Hypervisor</div>
  <div style="background:#6366f1; color:#fff; padding:6px; border-bottom:1px solid rgba(255,255,255,0.2);">Host OS</div>
  <div style="background:#475569; color:#fff; padding:6px;">Hardware</div>
</div>"""

    elif qid == 40:
        q["options"]["A"] = "<strong>Pie A</strong>" + generate_pie_3sector_svg('Pie A', 'IaaS (Python app upload)', '#93c5fd', 'PaaS (Gmail)', '#fed7aa', 'SaaS (VM on AWS)', '#86efac')
        q["options"]["B"] = "<strong>Pie B</strong>" + generate_pie_3sector_svg('Pie B', 'IaaS (Gmail)', '#93c5fd', 'PaaS (VM on AWS)', '#fed7aa', 'SaaS (Python app upload)', '#86efac')
        q["options"]["C"] = "<strong>Pie C</strong>" + generate_pie_3sector_svg('Pie C', 'IaaS (Gmail)', '#93c5fd', 'PaaS (Python app upload)', '#fed7aa', 'SaaS (VM on AWS)', '#86efac')
        q["options"]["D"] = "<strong>Pie D</strong>" + generate_pie_3sector_svg('Pie D', 'IaaS (VM on AWS)', '#93c5fd', 'PaaS (Python app upload)', '#fed7aa', 'SaaS (Gmail)', '#86efac')

    elif qid == 45:
        q["options"]["A"] = "<strong>Diagram A</strong>" + generate_subnet_diagram_svg(['Web Server'], ['Database'])
        q["options"]["B"] = "<strong>Diagram B</strong>" + generate_subnet_diagram_svg(['Database'], ['Web Server'])
        q["options"]["C"] = "<strong>Diagram C</strong>" + generate_subnet_diagram_svg(['Web Server', 'Database'], [])
        q["options"]["D"] = "<strong>Diagram D</strong>" + generate_subnet_diagram_svg([], ['Web Server', 'Database'])

    elif qid == 50:
        q["options"]["A"] = "<strong>Graph A</strong>" + generate_ram_barchart_svg(4, 16)
        q["options"]["B"] = "<strong>Graph B</strong>" + generate_ram_barchart_svg(4, 4)
        q["options"]["C"] = "<strong>Graph C</strong>" + generate_ram_barchart_svg(16, 16)
        q["options"]["D"] = "<strong>Graph D</strong>" + generate_ram_barchart_svg(16, 4)

    elif qid == 57:
        q["options"]["A"] = "<strong>Pie A</strong>" + generate_pie_3sector_svg('Pie A', 'AWS (Identity)', '#93c5fd', 'Azure (Website)', '#fed7aa', 'Google Cloud (Research analytics)', '#86efac')
        q["options"]["B"] = "<strong>Pie B</strong>" + generate_pie_3sector_svg('Pie B', 'AWS (Website)', '#93c5fd', 'Azure (Identity)', '#fed7aa', 'Google Cloud (Research analytics)', '#86efac')
        q["options"]["C"] = "<strong>Pie C</strong>" + generate_pie_3sector_svg('Pie C', 'AWS (Identity)', '#93c5fd', 'Azure (Research analytics)', '#fed7aa', 'Google Cloud (Website)', '#86efac')
        q["options"]["D"] = "<strong>Pie D</strong>" + generate_pie_3sector_svg('Pie D', 'AWS (Research analytics)', '#93c5fd', 'Azure (Identity)', '#fed7aa', 'Google Cloud (Website)', '#86efac')

    elif qid == 70:
        q["options"]["A"] = "<strong>Pie A</strong>" + generate_pie_4sector_svg('Document (MongoDB)', '#93c5fd', 'Graph (Neo4j)', '#fca5a5', 'Wide-column (Cassandra)', '#86efac', 'Key-value (Redis)', '#fed7aa')
        q["options"]["B"] = "<strong>Pie B</strong>" + generate_pie_4sector_svg('Document (Cassandra)', '#93c5fd', 'Graph (Neo4j)', '#fca5a5', 'Wide-column (MongoDB)', '#86efac', 'Key-value (Redis)', '#fed7aa')
        q["options"]["C"] = "<strong>Pie C</strong>" + generate_pie_4sector_svg('Document (Redis)', '#93c5fd', 'Graph (Neo4j)', '#fca5a5', 'Wide-column (Cassandra)', '#86efac', 'Key-value (MongoDB)', '#fed7aa')
        q["options"]["D"] = "<strong>Pie D</strong>" + generate_pie_4sector_svg('Document (MongoDB)', '#93c5fd', 'Graph (Redis)', '#fca5a5', 'Wide-column (Cassandra)', '#86efac', 'Key-value (Neo4j)', '#fed7aa')

with open("cloud_computing_mcqs_rich.json", "w", encoding="utf-8") as f:
    json.dump(cc_list, f, indent=2, ensure_ascii=False)

print(f"cloud_computing_mcqs_rich.json generated: {len(cc_list)} questions.")

# Now prepare all_subjects_mcqs.json
with open("enriched_mcqs.json", "r", encoding="utf-8") as f:
    we_list = json.load(f)

for item in we_list:
    item["subject"] = "Web Engineering"
    item["uid"] = f"WE-{item['id']}"

all_mcqs = []
all_mcqs.extend(cc_list)
all_mcqs.extend(we_list)

with open("all_subjects_mcqs.json", "w", encoding="utf-8") as f:
    json.dump(all_mcqs, f, indent=2, ensure_ascii=False)

print(f"all_subjects_mcqs.json created with {len(all_mcqs)} questions ({len(cc_list)} Cloud Computing + {len(we_list)} Web Engineering).")
