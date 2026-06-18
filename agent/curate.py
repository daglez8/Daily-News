#!/usr/bin/env python3
"""
curate.py — DEMO of the summarization/curation step for Phase 2.

NOTE: In production this step is performed by Claude during the scheduled run
(reading raw_candidates.json and applying judgment). This script just hard-codes
the curation decisions Claude made for THIS run so we can render real data and
verify the pipeline end-to-end. Links/dates are pulled from the live raw data.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "raw_candidates.json"), encoding="utf-8"))
by = raw["candidates"]

# (match_substring, category, relevance_score, summary)
CURATION = [
    ("Banxico advierte de los riesgos en el uso de IA", "Regulation / Governance / Risk", 93,
     "El Banco de México alertó sobre los riesgos del uso creciente de inteligencia artificial en el sistema financiero —riesgo de modelo, concentración tecnológica y ciberseguridad— y anticipó mayor supervisión sobre cómo bancos y entidades adoptan IA en sus procesos."),
    ("Trainium", "AI & Agents", 80,
     "Amazon está en conversaciones para vender sus chips de IA Trainium a terceros para uso en centros de datos, buscando erosionar el dominio de Nvidia. El movimiento intensifica la competencia por la infraestructura que sostiene el auge de la IA empresarial."),
    ("Accenture shares fall", "Leadership & Future of Work", 82,
     "Accenture's stock fell to its lowest since 2017 on fears that generative AI is eroding demand for traditional consulting and IT services. The sell-off underscores how AI is reshaping professional-services business models and headcount."),
    ("JPM Asset Mgt. CEO: AI Can Power", "AI & Agents", 74,
     "JPMorgan Asset Management's CEO argued that AI-driven innovation and a wave of mega-cap tech IPOs can sustain market momentum, framing the trend as a 'rising tide' of investment opportunity."),
    ("Meta Strikes New AI Computing Deals", "AI & Agents", 72,
     "Meta signed new AI computing agreements with data-center operator Crusoe, expanding the infrastructure behind its AI ambitions amid an escalating race among tech giants to lock in compute capacity."),
    ("US Acts to Accelerate Power Grid", "Regulation / Governance / Risk", 70,
     "US regulators moved to speed grid connections for AI data centers as surging electricity demand strains power networks — highlighting the growing collision between AI infrastructure growth and energy policy."),
    ("sobre subir la tasa de interés afecta al peso", "Financial Services Mexico", 84,
     "El peso se debilitó frente al dólar luego de que la Fed, en su primera decisión bajo Kevin Warsh, mantuviera la tasa pero endureciera su tono sobre posibles alzas. La señal hawkish presiona a las monedas latinoamericanas y al costo de financiamiento en México."),
    ("Dólar toca niveles no vistos desde mayo de 2025", "Financial Services Mexico", 76,
     "El dólar alcanzó su nivel más alto desde mayo de 2025 tras el mensaje antiinflacionario de la Fed, arrastrando a la baja a la mayoría de las monedas de América Latina y añadiendo presión cambiaria para economías como la mexicana."),
    ("Hawkish Fed to Put Pressure on Historically Tight Credit Spreads", "Capital Markets & M&A", 75,
     "A more hawkish Federal Reserve could pressure credit spreads trading at historically tight levels, Bloomberg analysts note. Wider spreads would raise borrowing costs across corporate and structured-credit markets."),
    ("Oaktree Private Credit Fund Redemptions", "Capital Markets & M&A", 72,
     "Redemptions from Oaktree's private credit fund fell back below the watched 5% threshold, easing concerns about liquidity stress in the asset class — a useful barometer for risk appetite in financial services."),
    ("SpaceX abre la puerta: las OPI", "Capital Markets & M&A", 73,
     "El exitoso debut bursátil de SpaceX reavivó las expectativas de una nueva ola de OPI tecnológicas en 2026, con al menos seis grandes empresas privadas perfilándose para salir a bolsa, lo que sugiere una ventana de liquidez más favorable."),
    ("A new golden age for Japanese banks", "Capital Markets & M&A", 68,
     "The Economist examines how rising rates revived profitability at Japanese banks while warning of risks tied to bond portfolios and competition — a window into how rate regimes reshape bank economics."),
    ("Seth Klarman on the Importance of Venture Capital", "Capital Markets & M&A", 66,
     "Baupost Group's Seth Klarman, the Boston-based value investor, discussed risk, IPOs and venture capital across his career, offering a disciplined-capital perspective on today's frothy markets."),
    ("Regulador energético de EU insta a redes", "Regulation / Governance / Risk", 67,
     "El regulador energético de EU ordenó a los operadores de red reconsiderar las reglas de conexión para grandes consumidores como los centros de datos, cuya demanda satura el sistema eléctrico — otra señal de la tensión entre IA y capacidad energética."),
    ("Steinberger, LeCun, Habib on AI Deployment", "AI & Agents", 70,
     "At VivaTech, Yann LeCun, Writer CEO May Habib and developer Peter Steinberger debated real-world AI deployment, from enterprise adoption to model limitations — a snapshot of where practitioners see AI delivering value."),
    ("Jalisco perdió 1,507 patrones", "Financial Services Mexico", 64,
     "Jalisco registró la baja de 1,507 patrones ante el IMSS en cinco meses, la segunda mayor caída del país según Coparmex, apuntando a un debilitamiento del empleo formal y del entorno empresarial."),
    ("Villa CORA", "Personal Interest Watchlist", 70,
     "ArchDaily features Villa CORA, a bamboo house in Tulum by terrAurea studio blending tropical materials with modern resort design — a reference for high-end, climate-adapted architecture in Mexico's coastal markets."),
    ("Melides House", "Personal Interest Watchlist", 62,
     "A contemporary house in Portugal's Melides region pairing restrained volumes with natural materials and landscape integration — an example of high-end residential design worth tracking."),
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
        "title": c["title"],
        "summary": summary,
        "link": c["link"],
        "source": c["source"],
        "published": c["published"],
        "category": cat,
        "relevance_score": score,
        "language": c["language"],
        "light": bool(c["paywall"]),
    })

out.sort(key=lambda a: a["published"] or "", reverse=True)
json.dump(out, open(os.path.join(HERE, "..", "docs", "news.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"Wrote {len(out)} curated articles to news.json")
if missing:
    print("WARNING — not found:", missing, file=sys.stderr)
