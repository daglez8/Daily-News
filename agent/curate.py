#!/usr/bin/env python3
"""
curate.py — DEMO of the summarization/curation step for Phase 2.

In production this step is performed by Claude during the scheduled run (reading
raw_candidates.json and applying judgment). This script hard-codes the curation
decisions for the current run so we can render real data and verify the pipeline.
Links/dates are pulled from the live raw data. Also writes docs/archive.json (history).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "raw_candidates.json"), encoding="utf-8"))
by = raw["candidates"]

# (match_substring, category, relevance_score, summary)
CURATION = [
    ("AbbVie buys Apogee for $10.9bn", "Capital Markets & M&A", 82,
     "AbbVie agreed to buy Apogee Therapeutics for $10.9bn — its largest deal in over five years — amid a surge of M&A in the pharma sector. A notable data point on big-ticket strategic acquisitions and sector consolidation."),
    ("record $8.5bn deal for Arcosa", "Capital Markets & M&A", 76,
     "Irish building-materials group CRH agreed a record $8.5bn acquisition of Dallas-based Arcosa, underscoring continued large-cap M&A appetite in infrastructure and construction materials."),
    ("Aeroméxico e Inbursa presentan una tarjeta", "Financial Services Mexico", 76,
     "Aeroméxico e Inbursa lanzaron una nueva tarjeta enfocada en viajeros, un ejemplo de innovación en productos financieros y alianzas banca-marca en el mercado mexicano."),
    ("Getty Images Soars 200%", "AI & Agents", 78,
     "Getty Images shares jumped ~200% premarket after announcing a licensing deal with OpenAI — a marquee example of AI firms striking content-licensing agreements and the market's appetite for AI-linked deals."),
    ("Meta Taps New WhatsApp Boss", "Capital Markets & M&A", 74,
     "Meta is investing $900M into Indian fintech startup Cred and installing its founder as WhatsApp's new boss — a sizeable strategic bet linking big tech, fintech and payments."),
    ("Vacantes de IA en México se duplicaron", "AI & Agents", 74,
     "La demanda de talento en inteligencia artificial en México se duplicó en el último año, señal de que la adopción de IA en el país entra a una etapa temprana de madurez — relevante para talento y transformación."),
    ("Indicadores del 22 al 26 de junio", "Financial Services Mexico", 74,
     "La semana trae datos clave para México —inflación, empleo y el anuncio de política monetaria de Banxico— que marcarán el tono para tasas, crédito y el peso en el corto plazo."),
    ("Pemex: ni soberanía ni financiamiento", "Financial Services Mexico", 74,
     "Análisis de El Financiero sobre la estrategia de Pemex: los datos sugieren menor producción pese al objetivo de soberanía energética, con implicaciones para las finanzas públicas y el riesgo soberano."),
    ("Bain tests software takeover targets by vibecoding", "Capital Markets & M&A", 74,
     "Private equity firms like Bain are using AI to rapidly recreate software products ('vibecoding' replicas) to gauge takeover targets' competitive moats — a striking fusion of AI and M&A diligence."),
    ("Warsh salió bien librado", "Financial Services Mexico", 72,
     "Crónica de la primera reunión del FOMC presidida por Kevin Warsh como nuevo titular de la Fed; el tono y las señales sobre tasas tienen efecto directo sobre el peso y el costo de financiamiento en México."),
    ("SpaceX Kicks Off Debut High-Grade Bond Sale", "Capital Markets & M&A", 72,
     "SpaceX launched its first investment-grade bond sale to fund its AI ambitions following its record IPO — a milestone in how mega-cap tech issuers tap debt markets at scale."),
    ("Cómo usan la IA los líderes", "Leadership & Future of Work", 70,
     "Columna de El Financiero sobre cómo los ejecutivos están incorporando la inteligencia artificial en su trabajo diario y en la toma de decisiones — útil para liderazgo y productividad."),
    ("High AI Spending is", "AI & Agents", 70,
     "Everpure's CFO argued that elevated AI capital spending is 'not temporary,' reinforcing the view that enterprise AI infrastructure investment is structural rather than a passing cycle."),
    ("Nvidia Seeks to Make Humanoid AI Robots Safer", "AI & Agents", 66,
     "Nvidia is developing techniques to make humanoid robots safer around people, a sign of how AI is moving into physical, safety-critical deployments."),
    ("Argentina Approves Dollar Borrowing", "Capital Markets & M&A", 66,
     "Argentina authorized up to $5bn in new dollar-denominated borrowing amid multilateral loan talks — a notable LatAm sovereign-debt development for emerging-market credit watchers."),
    ("Microsoft and Chevron Sign 20-Year Power Deal", "Regulation / Governance / Risk", 64,
     "Chevron signed a 20-year deal to supply natural-gas power to a Microsoft data center in West Texas — highlighting the energy, infrastructure and governance pressures behind the AI build-out."),
    ("Inflationary Environment Suggests Higher Rates", "Capital Markets & M&A", 64,
     "Principal's chief global strategist Seema Shah argued the near-term inflationary impact of the AI capex boom points to higher rates — relevant for fixed income, spreads and financing costs."),
    ("Tencent Tests AI Assistant", "AI & Agents", 62,
     "Tencent began testing an AI assistant inside WeChat as it races to catch peers, a sign of AI agents being embedded into the super-apps that anchor large consumer ecosystems."),
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
amap = {a["link"]: a for a in archive}
for a in out:
    amap.setdefault(a["link"], a)
archive = sorted(amap.values(), key=lambda a: a.get("published") or "", reverse=True)[:500]
json.dump(archive, open(arch_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"Wrote {len(out)} to docs/news.json; history now holds {len(archive)} articles")
if missing:
    print("WARNING — not found:", missing, file=sys.stderr)
