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
    ("Banxico publica nuevas reglas para pagos digitales", "Financial Services Mexico", 90,
     "Banxico publicó en el DOF modificaciones al sistema de pagos y operaciones bancarias que cambian cómo funcionan las transferencias digitales en México. Las nuevas reglas buscan reforzar seguridad y eficiencia en el sistema de pagos."),
    ("Early Users of Anthropic Mythos", "AI & Agents", 88,
     "Some firms picked early by Anthropic to test its Mythos AI model kept their preview access despite a US government order, highlighting the tightening interplay between frontier AI access and government oversight."),
    ("Banxico advierte de los riesgos en el uso de IA", "Regulation / Governance / Risk", 92,
     "El Banco de México alertó sobre los riesgos del uso creciente de inteligencia artificial en el sistema financiero —riesgo de modelo, concentración tecnológica y ciberseguridad— anticipando mayor supervisión sobre cómo bancos y entidades adoptan IA."),
    ("Companies Move to Secure Data as AI Increases Security Risks", "Regulation / Governance / Risk", 78,
     "As AI raises new security exposures, companies and the US government are moving quickly to lock down data and ensure compliance. A signal of rising governance and cybersecurity expectations around enterprise AI."),
    ("Fmr. Lululemon CIO on AI", "Leadership & Future of Work", 74,
     "Former Lululemon/REI/Nordstrom CIO Julie Averill discusses how AI is reshaping C-suites and jobs, drawing on her book on impact-driven leadership — a useful lens on talent and organizational change."),
    ("SpaceX plots $20bn bond deal", "Capital Markets & M&A", 76,
     "Fresh off an $86bn record IPO, SpaceX is tapping debt markets for a ~$20bn bond deal. The move shows how mega-cap tech/AI issuers are pairing equity debuts with large-scale debt financing."),
    ("EU set to remove barriers to banks", "Capital Markets & M&A", 72,
     "A draft European Commission report aims to ease cross-border capital flows for EU banks, seeking to close the performance gap with US rivals — relevant to how banking competition and FIG strategy evolve."),
    ("Fibra Educa obtiene 4,000 mdp", "Capital Markets & M&A", 78,
     "Fibra Educa colocó 4,000 millones de pesos en tres bonos en la BMV, reflejando apetito del mercado mexicano por instrumentos de deuda en bienes raíces. Una señal positiva para la emisión local de capital."),
    ("Dólar toca niveles no vistos desde mayo de 2025", "Financial Services Mexico", 76,
     "El dólar alcanzó su nivel más alto desde mayo de 2025 tras el mensaje antiinflacionario de la Fed, arrastrando a la baja a la mayoría de las monedas de América Latina y añadiendo presión cambiaria para México."),
    ("US Acts to Speed Up Power Grid Hook-Ups for AI Data Centers", "Regulation / Governance / Risk", 70,
     "US regulators took their biggest step yet to speed grid connections for AI data centers while trying to contain rising utility bills — underscoring the collision between AI infrastructure growth and energy policy."),
    ("JPM Asset Mgt. CEO: AI Can Power", "AI & Agents", 72,
     "JPMorgan Asset Management's CEO argued that AI-driven innovation and a wave of mega-cap tech IPOs can sustain market momentum, framing the trend as a 'rising tide' of investment opportunity."),
    ("Meta Strikes New AI Computing Deals", "AI & Agents", 72,
     "Meta secured new AI computing agreements with data-center developer Crusoe, bolstering the infrastructure behind its AI ambitions amid an escalating race for compute capacity."),
    ("SpaceX abre la puerta: las OPI", "Capital Markets & M&A", 72,
     "El debut bursátil de SpaceX reavivó expectativas de una nueva ola de OPI tecnológicas en 2026, con al menos seis grandes empresas privadas perfilándose para salir a bolsa — señal de una ventana de liquidez más favorable."),
    ("Pimco realizó una apuesta de US$2.000 millones por Colombia", "Capital Markets & M&A", 68,
     "Pimco invirtió US$2,000 millones en deuda de administraciones locales de Colombia antes de la primera vuelta electoral, una apuesta de gran tamaño sobre el crédito soberano y subsoberano en la región."),
    ("A new golden age for Japanese banks", "Capital Markets & M&A", 66,
     "The Economist examines how rising rates revived profitability at Japanese banks while smaller lenders sit on low-return bonds they can't sell — a window into how rate regimes reshape bank economics."),
    ("Stocks Rise With Nvidia Leading", "Capital Markets & M&A", 64,
     "US stocks rose as semiconductor shares extended their rally, with Nvidia leading S&P 500 gainers. The chip-led move reflects continued investor enthusiasm for the AI hardware cycle."),
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
