#!/usr/bin/env python3
"""
curate.py — DEMO of the summarization/curation step for Phase 2.

NOTE: In production this step is performed by Claude during the scheduled run
(reading raw_candidates.json and applying judgment). This script hard-codes the
curation decisions Claude made for the current run so we can render real data and
verify the pipeline end-to-end. Links/dates are pulled from the live raw data.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "raw_candidates.json"), encoding="utf-8"))
by = raw["candidates"]

# (match_substring, category, relevance_score, summary)
CURATION = [
    ("Anthropic Crackdown Claims New Power", "AI & Agents", 92,
     "A Commerce Department order led by Secretary Lutnick asserts unprecedented authority over Anthropic's AI models via export controls, escalating US government oversight of frontier AI — a key signal for AI governance and model risk."),
    ("Co-Founder and Top Economist on Doing Research", "AI & Agents", 82,
     "Anthropic's co-founder and chief economist discuss AI's impact on labor markets, society and existential questions — a substantive look at where frontier AI research and its economic effects are heading."),
    ("Early Users of Anthropic Mythos", "AI & Agents", 86,
     "Some firms picked early by Anthropic to test its Mythos AI model kept their preview access despite a US government order, underscoring the tightening interplay between frontier AI access and government oversight."),
    ("EU Tech Chief Virkkunen", "AI & Agents", 72,
     "The EU's top technology official discussed AI, digital sovereignty and relations with the US at VivaTech — relevant to how AI regulation and governance diverge across regions."),
    ("trampa del ingreso medio", "AI & Agents", 70,
     "Columna de El Economista sobre cómo la inteligencia artificial podría agravar o aliviar la 'trampa del ingreso medio' en economías como México, ligando adopción de IA con productividad y crecimiento."),
    ("prueba de fuego para la banca digital", "Financial Services Mexico", 80,
     "Análisis sobre los retos reales de la banca digital y la inclusión financiera en México —más allá del discurso de digitalización—, con implicaciones para fintech y servicios financieros."),
    ("costo de aplazar la reforma fiscal", "Financial Services Mexico", 76,
     "El Economista advierte sobre el costo de posponer la reforma fiscal en México, recordando que las calificadoras (Moody's) ya han degradado la perspectiva — un riesgo macro y soberano relevante para el crédito."),
    ("Dólar toca niveles no vistos desde mayo de 2025", "Financial Services Mexico", 74,
     "El dólar alcanzó su nivel más alto desde mayo de 2025 tras el mensaje antiinflacionario de la Fed, arrastrando a la baja a la mayoría de las monedas de América Latina y presionando a México."),
    ("Cuts Bank Capital Level to Boost Lending", "Regulation / Governance / Risk", 74,
     "Canada's regulator lowered capital requirements for its largest banks for the first time in three years to encourage lending — a notable example of regulators dialing risk settings to spur credit."),
    ("Starling Shrinks Board", "Regulation / Governance / Risk", 66,
     "UK digital bank Starling is streamlining its board after several departures, concentrating control with its largest shareholder — a governance development worth watching in digital banking."),
    ("Santander Surpasses Inditex", "Capital Markets & M&A", 70,
     "Banco Santander became Spain's most valuable listed company, overtaking Inditex for the first time in eight years — a marker of renewed investor appetite for banks in a higher-rate world."),
    ("Jio Platforms Files For", "Capital Markets & M&A", 64,
     "Mukesh Ambani's Jio Platforms filed draft documents for what could be India's largest-ever IPO, with Meta and other backers — a major test of global appetite for mega-cap tech listings."),
    ("Struggling Car Parts Stock", "Capital Markets & M&A", 62,
     "Traders are chasing French car-parts maker Valeo as a speculative AI-adjacent play, a sign of how far the AI trade is stretching across the market."),
    ("Ya no habrá que pagar a los CEOs", "Leadership & Future of Work", 68,
     "Columna de El Financiero que reflexiona, con tono provocador, sobre cómo la IA y la automatización están redefiniendo el rol y el valor del liderazgo ejecutivo y la gestión."),
    ("Villa CORA", "Personal Interest Watchlist", 70,
     "ArchDaily features Villa CORA, a bamboo house in Tulum by terrAurea studio blending tropical materials with modern resort design — a reference for high-end, climate-adapted architecture in Mexico's coastal markets."),
    ("Melides House", "Personal Interest Watchlist", 62,
     "A contemporary 500 m² house in Portugal's Melides region pairing restrained volumes with natural materials and landscape integration — an example of high-end residential design worth tracking."),
]

def find(sub):
    for c in by:
        if sub in c["title"]:
            return c
    return None

out, missing = [], []
for sub, cat, score, summary in CURATION:
    c = find(sub)
    if not c:
        missing.append(sub); continue
    out.append({
        "title": c["title"], "summary": summary, "link": c["link"],
        "source": c["source"], "published": c["published"], "category": cat,
        "relevance_score": score, "language": c["language"], "light": bool(c["paywall"]),
    })

out.sort(key=lambda a: a["published"] or "", reverse=True)
news_path = os.path.join(HERE, "..", "docs", "news.json")
arch_path = os.path.join(HERE, "..", "docs", "archive.json")
json.dump(out, open(news_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# archive.json — rolling history: merge the current feed in, dedupe by link, keep newest 500.
archive = []
if os.path.exists(arch_path):
    try: archive = json.load(open(arch_path, encoding="utf-8"))
    except Exception: archive = []
by = {a["link"]: a for a in archive}
for a in out:
    by.setdefault(a["link"], a)
archive = sorted(by.values(), key=lambda a: a.get("published") or "", reverse=True)[:500]
json.dump(archive, open(arch_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"Wrote {len(out)} to docs/news.json; history now holds {len(archive)} articles")
if missing:
    print("WARNING — not found:", missing, file=sys.stderr)
