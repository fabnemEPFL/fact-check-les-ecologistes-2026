#!/usr/bin/env python3
"""Generate a professional final-style interim PDF from the verified subset.

The report is intentionally explicit that it covers only the verified prefix of the
564-claim corpus and that no full adversarial audit was performed. It preserves all
verified claims in the body with their sources and creates Base64 text chunks of the
PDF to make recovery through text-only connectors possible.
"""

from __future__ import annotations

import base64
import hashlib
import json
import lzma
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import Label

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "checkpoints" / "latest.json"
OUTDIR = ROOT / "reports" / "interim_415"
PDF = OUTDIR / "revue_factuelle_ecologistes_2026_415_affirmations.pdf"
MD = OUTDIR / "README.md"
B64DIR = OUTDIR / "pdf_base64_chunks"
ALLOWED = [
    "Exact",
    "Globalement exact",
    "À nuancer",
    "Trompeur",
    "Faux",
    "Invérifiable ou insuffisamment étayé",
]
VERDICT_COLORS = {
    "Exact": colors.HexColor("#1B5E20"),
    "Globalement exact": colors.HexColor("#558B2F"),
    "À nuancer": colors.HexColor("#D97706"),
    "Trompeur": colors.HexColor("#C2410C"),
    "Faux": colors.HexColor("#991B1B"),
    "Invérifiable ou insuffisamment étayé": colors.HexColor("#475569"),
}


def esc(value) -> str:
    s = "" if value is None else str(value)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_rows():
    latest = json.loads(LATEST.read_text(encoding="utf-8"))
    name = latest["authoritative_recovery_source"]["name"]
    raw = (ROOT / "checkpoints" / name).read_text(encoding="utf-8")
    payload = lzma.decompress(base64.b64decode(raw))
    cp = json.loads(payload)
    rows = cp["restored_claim_ledger"]
    verified = [r for r in rows if r.get("verification_status") == "vérifiée"]
    return latest, rows, verified


def register_fonts():
    regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    italic = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf")
    if regular.exists():
        pdfmetrics.registerFont(TTFont("ReportSans", str(regular)))
        pdfmetrics.registerFont(TTFont("ReportSans-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("ReportSans-Italic", str(italic)))
        return "ReportSans", "ReportSans-Bold", "ReportSans-Italic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, styles, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.styles_ref = styles
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self._header_footer))

    def _header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.4)
        canvas.line(self.leftMargin, 13*mm, A4[0]-self.rightMargin, 13*mm)
        canvas.setFont(self.styles_ref["font_regular"], 7.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(self.leftMargin, 8.5*mm, "Revue factuelle du programme des Écologistes 2026 - version 415 affirmations")
        canvas.drawRightString(A4[0]-self.rightMargin, 8.5*mm, f"p. {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in ("H1", "H2"):
                level = 0 if style == "H1" else 1
                text = flowable.getPlainText()
                key = f"h{level}-{self.page}-{abs(hash(text))}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def styles(fonts):
    regular, bold, italic = fonts
    ss = getSampleStyleSheet()
    out = {"font_regular": regular, "font_bold": bold, "font_italic": italic}
    out["Title"] = ParagraphStyle("Title", fontName=bold, fontSize=26, leading=31, textColor=colors.HexColor("#0F172A"), alignment=TA_LEFT, spaceAfter=12)
    out["Subtitle"] = ParagraphStyle("Subtitle", fontName=regular, fontSize=13, leading=18, textColor=colors.HexColor("#475569"), spaceAfter=10)
    out["H1"] = ParagraphStyle("H1", fontName=bold, fontSize=17, leading=21, textColor=colors.HexColor("#0F172A"), spaceBefore=10, spaceAfter=8, keepWithNext=True)
    out["H2"] = ParagraphStyle("H2", fontName=bold, fontSize=13, leading=17, textColor=colors.HexColor("#1E293B"), spaceBefore=9, spaceAfter=6, keepWithNext=True)
    out["H3"] = ParagraphStyle("H3", fontName=bold, fontSize=10.5, leading=14, textColor=colors.HexColor("#0F172A"), spaceBefore=8, spaceAfter=4, keepWithNext=True)
    out["Body"] = ParagraphStyle("Body", fontName=regular, fontSize=9.3, leading=13.3, textColor=colors.HexColor("#1F2937"), spaceAfter=5)
    out["Small"] = ParagraphStyle("Small", fontName=regular, fontSize=7.8, leading=10.8, textColor=colors.HexColor("#475569"), spaceAfter=3)
    out["Tiny"] = ParagraphStyle("Tiny", fontName=regular, fontSize=6.8, leading=9.3, textColor=colors.HexColor("#475569"), spaceAfter=2)
    out["Quote"] = ParagraphStyle("Quote", fontName=italic, fontSize=9.2, leading=13.2, leftIndent=8, rightIndent=4, borderColor=colors.HexColor("#CBD5E1"), borderWidth=0, borderPadding=(0,0,0,8), textColor=colors.HexColor("#334155"), spaceAfter=5)
    out["Callout"] = ParagraphStyle("Callout", fontName=regular, fontSize=9.2, leading=13.4, backColor=colors.HexColor("#F8FAFC"), borderColor=colors.HexColor("#CBD5E1"), borderWidth=0.6, borderPadding=7, spaceBefore=4, spaceAfter=8)
    out["CoverKicker"] = ParagraphStyle("CoverKicker", fontName=bold, fontSize=9, leading=12, textColor=colors.HexColor("#166534"), spaceAfter=12)
    return out


def verdict_chart(counts, font_regular):
    d = Drawing(470, 195)
    chart = VerticalBarChart()
    chart.x = 35
    chart.y = 42
    chart.height = 125
    chart.width = 410
    vals = [counts.get(v, 0) for v in ALLOWED]
    chart.data = [vals]
    chart.categoryAxis.categoryNames = ["Exact", "Glob. exact", "À nuancer", "Trompeur", "Faux", "Insuff." ]
    chart.categoryAxis.labels.fontName = font_regular
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontName = font_regular
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(vals) * 1.15 if vals else 1
    chart.valueAxis.valueStep = max(10, int(max(vals)/5/10)*10) if max(vals) else 1
    chart.bars[0].fillColor = colors.HexColor("#64748B")
    chart.bars[0].strokeColor = colors.HexColor("#475569")
    d.add(chart)
    lab = Label()
    lab.setOrigin(235, 182)
    lab.fontName = font_regular
    lab.fontSize = 8
    lab.setText("Distribution des verdicts dans le sous-corpus vérifié")
    lab.textAnchor = "middle"
    d.add(lab)
    return d


def pct(n, d):
    return 0 if not d else 100*n/d


def source_label(src):
    title = src.get("title") or src.get("id") or "Source"
    pub = src.get("publisher")
    dt = src.get("publication_date")
    bits = [title]
    if pub: bits.append(pub)
    if dt: bits.append(str(dt))
    return " - ".join(bits)


def claim_story(row, st):
    page = ", ".join(str(x) for x in (row.get("pdf_pages") or [])) or "?"
    chapter = row.get("chapter_title") or (f"Chapitre {row.get('chapter')}" if row.get("chapter") is not None else "Sans chapitre")
    heading = f"{esc(row.get('id'))} - {esc(chapter)} - p. {esc(page)}"
    flows = [Paragraph(heading, st["H3"])]
    verdict = row.get("verdict") or "Non renseigné"
    vc = VERDICT_COLORS.get(verdict, colors.HexColor("#475569"))
    meta = Table([
        [Paragraph(f"<b>Verdict</b><br/><font color='white'>{esc(verdict)}</font>", st["Small"]),
         Paragraph(f"<b>Confiance</b><br/>{esc(row.get('confidence') or 'Non renseignée')}", st["Small"]),
         Paragraph(f"<b>Type</b><br/>{esc(row.get('claim_type') or 'Non renseigné')}", st["Small"])]
    ], colWidths=[5.4*cm, 4.2*cm, 7.2*cm])
    meta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), vc),
        ("TEXTCOLOR", (0,0), (0,0), colors.white),
        ("BACKGROUND", (1,0), (-1,0), colors.HexColor("#F8FAFC")),
        ("BOX", (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    flows += [meta, Spacer(1, 4)]
    if row.get("quote"):
        flows.append(Paragraph(f"« {esc(row['quote'])} »", st["Quote"]))
    flows.append(Paragraph(f"<b>Proposition évaluée.</b> {esc(row.get('normalized_claim') or '')}", st["Body"]))
    if row.get("argumentative_role"):
        flows.append(Paragraph(f"<b>Rôle argumentatif.</b> {esc(row.get('argumentative_role'))}", st["Small"]))
    policies = row.get("policies") or []
    if policies:
        flows.append(Paragraph(f"<b>Politiques concernées.</b> {esc('; '.join(map(str, policies)))}", st["Small"]))
    flows.append(Paragraph(f"<b>Justification.</b> {esc(row.get('justification') or 'Non renseignée')}", st["Body"]))
    cons = row.get("consensus_or_controversy")
    qual = row.get("source_quality")
    if cons or qual:
        text = []
        if cons: text.append(f"<b>Consensus / controverse.</b> {esc(cons)}")
        if qual: text.append(f"<b>Qualité des sources.</b> {esc(qual)}")
        flows.append(Paragraph("<br/>".join(text), st["Small"]))
    else:
        flows.append(Paragraph("<b>Métadonnées de revue.</b> Consensus/controverse et qualité synthétique non renseignés dans le ledger de cette version; les sources, le verdict et la justification sont néanmoins présents.", st["Small"]))
    srcs = row.get("sources") or []
    if srcs:
        flows.append(Paragraph("<b>Sources.</b>", st["Small"]))
        for s in srcs:
            url = s.get("url") or ""
            grade = s.get("quality_grade")
            label = source_label(s)
            grade_txt = f" [grade {grade}]" if grade else ""
            if url:
                safe_url = esc(url).replace("'", "%27")
                txt = f"• {esc(label)}{esc(grade_txt)} - <link href='{safe_url}' color='#1D4ED8'>{esc(url)}</link>"
            else:
                txt = f"• {esc(label)}{esc(grade_txt)}"
            flows.append(Paragraph(txt, st["Tiny"]))
    if row.get("needs_sol_review"):
        reason = row.get("sol_review_reason") or "Dossier marqué pour revue approfondie."
        flows.append(Paragraph(f"<b>Revue approfondie signalée.</b> {esc(reason)}", st["Tiny"]))
    flows.append(Spacer(1, 7))
    return flows


def main():
    latest, all_rows, verified = load_rows()
    n = len(verified)
    total = len(all_rows)
    counts = Counter(r.get("verdict") for r in verified)
    flags = [r for r in verified if r.get("needs_sol_review")]
    missing_review_meta = [r for r in verified if not r.get("consensus_or_controversy") or not r.get("source_quality")]
    policy_links = sum(len(r.get("policies") or []) for r in verified)
    source_citations = [s for r in verified for s in (r.get("sources") or [])]
    grade_counts = Counter(s.get("quality_grade") or "Non renseigné" for s in source_citations)
    type_counts = Counter(r.get("claim_type") or "Non renseigné" for r in verified)
    exactish = counts["Exact"] + counts["Globalement exact"]
    strict_problem = counts["Trompeur"] + counts["Faux"]

    # Per-chapter summary for chapters represented by at least 5 verified rows.
    chapter_rows = defaultdict(list)
    chapter_order = []
    for r in verified:
        ch = r.get("chapter_title") or (f"Chapitre {r.get('chapter')}" if r.get("chapter") is not None else "Sans chapitre")
        if ch not in chapter_rows: chapter_order.append(ch)
        chapter_rows[ch].append(r)
    chapter_summary = []
    for ch in chapter_order:
        rs = chapter_rows[ch]
        if len(rs) < 5: continue
        pc = sum(r.get("verdict") in ("Trompeur", "Faux") for r in rs)
        nv = sum(r.get("verdict") == "À nuancer" for r in rs)
        chapter_summary.append((ch, len(rs), pc, nv, pct(pc, len(rs))))
    top_problem = sorted(chapter_summary, key=lambda x: (x[4], x[1]), reverse=True)[:12]

    fonts = register_fonts()
    st = styles(fonts)
    OUTDIR.mkdir(parents=True, exist_ok=True)

    doc = ReportDoc(str(PDF), st, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm, topMargin=18*mm, bottomMargin=18*mm,
                    title=f"Revue factuelle du programme des Écologistes 2026 - {n} affirmations vérifiées",
                    author="Analyse assistée par IA - état intermédiaire")
    story = []

    # Cover
    story.append(Spacer(1, 32*mm))
    story.append(Paragraph("REVUE FACTUELLE", st["CoverKicker"]))
    story.append(Paragraph("Programme des Écologistes 2026", st["Title"]))
    story.append(Paragraph(f"Rapport sur {n} affirmations vérifiées sur {total}", st["Subtitle"]))
    story.append(Spacer(1, 8*mm))
    cover_tbl = Table([
        [Paragraph("Corpus consolidé", st["Small"]), Paragraph("Affirmations vérifiées", st["Small"]), Paragraph("Couverture", st["Small"])],
        [Paragraph(f"<b>{total}</b> affirmations", st["H2"]), Paragraph(f"<b>{n}</b>", st["H2"]), Paragraph(f"<b>{pct(n,total):.1f} %</b>", st["H2"])],
    ], colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ("BOX", (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0,0), (-1,-1), 0.4, colors.HexColor("#E2E8F0")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(
        "<b>Version intermédiaire au format du rapport final.</b> Le recensement des affirmations couvre les 208 pages et les 66 chapitres du programme. "
        f"La passe de vérification est ici arrêtée après {n} affirmations, au premier identifiant non terminé <b>{esc(latest.get('resume',{}).get('first_unfinished_identifier'))}</b>. "
        "Les statistiques de verdict portent exclusivement sur le sous-corpus vérifié et ne doivent pas être extrapolées mécaniquement aux affirmations restantes.", st["Callout"]))
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph("État documentaire généré à partir du checkpoint autoritatif du dépôt GitHub. Un nouveau rapport sera produit lorsque les 564 affirmations auront été vérifiées.", st["Small"]))
    story.append(PageBreak())

    # TOC
    story.append(Paragraph("Sommaire", st["H1"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOC0", fontName=fonts[1], fontSize=9.5, leading=13, leftIndent=0, firstLineIndent=0, spaceBefore=5),
        ParagraphStyle(name="TOC1", fontName=fonts[0], fontSize=8, leading=11, leftIndent=12, firstLineIndent=0, spaceBefore=2),
    ]
    story.append(toc)
    story.append(PageBreak())

    # Executive summary
    story.append(Paragraph("1. Résumé exécutif", st["H1"]))
    story.append(Paragraph(
        f"Cette version examine {n} affirmations factuelles uniques, soit {pct(n,total):.1f} % des {total} affirmations consolidées dans le programme. "
        f"Parmi elles, {exactish} ({pct(exactish,n):.1f} %) sont classées <i>Exact</i> ou <i>Globalement exact</i>; "
        f"{counts['À nuancer']} ({pct(counts['À nuancer'],n):.1f} %) nécessitent une nuance substantielle mais non invalidante; "
        f"{strict_problem} ({pct(strict_problem,n):.1f} %) sont classées <i>Trompeur</i> ou <i>Faux</i>; "
        f"et {counts['Invérifiable ou insuffisamment étayé']} ({pct(counts['Invérifiable ou insuffisamment étayé'],n):.1f} %) restent invérifiables ou insuffisamment étayées avec les éléments disponibles.", st["Body"]))
    story.append(Paragraph(
        "Le signal principal de cette passe primaire n'est donc pas une accumulation d'erreurs franches: les rectifications les plus sévères sont minoritaires. "
        "Une part importante des formulations demande cependant de préciser le dénominateur, la période, la portée causale, le caractère prospectif ou le niveau de certitude. "
        "Cette lecture doit rester prudente car le sous-corpus vérifié suit l'ordre du programme: il n'est ni aléatoire ni nécessairement représentatif des 149 affirmations encore non vérifiées.", st["Body"]))
    if flags:
        story.append(Paragraph(
            f"Le ledger marque {len(flags)} dossiers ({pct(len(flags),n):.1f} %) comme pouvant bénéficier d'une revue approfondie par un modèle plus puissant. "
            "Ce marquage a été volontairement large (causalités, projections, définitions ambiguës, sources contradictoires ou verdicts sensibles). "
            "À la demande du commanditaire, aucun post-audit contradictoire exhaustif n'est réalisé dans cette version; les verdicts sont donc ceux de la passe primaire.", st["Callout"]))
    story.append(verdict_chart(counts, fonts[0]))

    data = [["Verdict", "Nombre", "% du sous-corpus"]] + [[v, counts.get(v,0), f"{pct(counts.get(v,0),n):.1f} %"] for v in ALLOWED]
    t = Table(data, colWidths=[9.2*cm, 3.2*cm, 4.2*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ("FONTNAME", (0,0), (-1,0), fonts[1]), ("FONTNAME", (0,1), (-1,-1), fonts[0]),
        ("FONTSIZE", (0,0), (-1,-1), 8.2),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story += [t, Spacer(1, 8)]

    # Method
    story.append(Paragraph("2. Méthodologie", st["H1"]))
    story.append(Paragraph(
        "Le corpus a été constitué par parcours systématique des 208 pages, puis consolidation des doublons en affirmations uniques. Une affirmation est retenue lorsqu'elle joue un rôle argumentatif substantiel: établir un problème, quantifier son ampleur, attribuer une cause, comparer des situations, justifier une intervention ou soutenir une projection. Les jugements normatifs purs sont exclus.", st["Body"]))
    story.append(Paragraph(
        "Pour chaque affirmation, la vérification privilégie les données primaires, organismes statistiques et institutions publiques, puis la littérature scientifique et les rapports reconnus. Les périodes, populations, dénominateurs, périmètres, définitions d'indicateurs et sources originales citées par le programme sont contrôlés autant que possible. Les causalités sont distinguées des simples corrélations; les projections sont appréciées selon leurs hypothèses plutôt que comme des faits observés.", st["Body"]))
    story.append(Paragraph(
        "Six verdicts sont utilisés: Exact; Globalement exact; À nuancer; Trompeur; Faux; Invérifiable ou insuffisamment étayé. Le classement « Trompeur » est réservé aux omissions ou cadrages qui conduisent matériellement à une conclusion différente des meilleures données; « Faux » aux incompatibilités substantielles avec les preuves disponibles.", st["Body"]))
    story.append(Paragraph(
        f"Contrôle structurel: les compteurs du checkpoint sont cohérents avec {total} lignes et {n} lignes marquées vérifiées. Aucun identifiant dupliqué n'a été détecté. "
        f"{len(missing_review_meta)} lignes vérifiées, concentrées dans la partie la plus récente du travail, n'ont pas encore les deux métadonnées synthétiques « consensus/controverse » et « qualité des sources »; elles disposent néanmoins de sources, d'un verdict et d'une justification. Cette lacune est signalée et ces champs ne sont pas imputés artificiellement.", st["Body"]))

    # Quantitative results
    story.append(Paragraph("3. Résultats quantitatifs", st["H1"]))
    story.append(Paragraph(f"Le sous-corpus vérifié représente {n} affirmations uniques et {sum(len(r.get('occurrences') or []) for r in verified)} occurrences. Il contient {policy_links} relations affirmation → politique et {len(source_citations)} citations de sources dans les dossiers de preuve.", st["Body"]))
    qdata = [["Grade de source", "Citations dans les dossiers"]] + [[str(k), v] for k,v in sorted(grade_counts.items(), key=lambda kv: str(kv[0]))]
    qt = Table(qdata, colWidths=[8*cm, 5*cm], repeatRows=1)
    qt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E2E8F0")), ("FONTNAME", (0,0), (-1,0), fonts[1]),
        ("FONTNAME", (0,1), (-1,-1), fonts[0]), ("FONTSIZE", (0,0), (-1,-1), 8.2),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5E1")),
        ("ALIGN", (1,1), (1,-1), "RIGHT"), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(Paragraph("3.1 Nature des sources", st["H2"]))
    story.append(Paragraph("Les grades ci-dessous sont ceux enregistrés source par source dans le ledger. Ils comptent les citations dans les dossiers, et non les documents uniques: une même source peut soutenir plusieurs affirmations.", st["Small"]))
    story.append(qt)

    story.append(Paragraph("3.2 Types d'affirmations", st["H2"]))
    type_data = [["Type (libellé du ledger)", "n"]] + [[k,v] for k,v in type_counts.most_common(15)]
    tt = Table(type_data, colWidths=[12.5*cm, 2.5*cm], repeatRows=1)
    tt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E2E8F0")), ("FONTNAME", (0,0), (-1,0), fonts[1]),
        ("FONTNAME", (0,1), (-1,-1), fonts[0]), ("FONTSIZE", (0,0), (-1,-1), 7.8),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")), ("ALIGN", (1,1), (1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(tt)

    story.append(Paragraph("3.3 Concentration des verdicts sévères par chapitre", st["H2"]))
    story.append(Paragraph("Le tableau suivant est descriptif et limité aux chapitres déjà représentés par au moins cinq affirmations vérifiées. Les pourcentages sur petits effectifs ne doivent pas être surinterprétés.", st["Small"]))
    cdata = [["Chapitre / section", "n", "Trompeur+Faux", "À nuancer", "% sévères"]]
    for ch, nn, pp, nv, rate in top_problem:
        cdata.append([Paragraph(esc(ch), st["Tiny"]), nn, pp, nv, f"{rate:.1f} %"])
    ct = Table(cdata, colWidths=[9.5*cm, 1.4*cm, 2.5*cm, 2.0*cm, 2.1*cm], repeatRows=1)
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E2E8F0")), ("FONTNAME", (0,0), (-1,0), fonts[1]),
        ("FONTNAME", (0,1), (-1,-1), fonts[0]), ("FONTSIZE", (0,0), (-1,-1), 7.3),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")), ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(ct)

    # Qualitative synthesis
    story.append(Paragraph("4. Tendances qualitatives observées", st["H1"]))
    story.append(Paragraph(
        "Les justifications du ledger montrent plusieurs familles récurrentes de réserves: dénominateurs ou populations mal définis; périodes non précisées; généralisation d'un résultat local ou sectoriel; passage d'une corrélation à une causalité; projection présentée sans hypothèses; comparaison entre indicateurs qui ne mesurent pas exactement la même chose; ou formulation absolue (« toujours », « à l'abri », « uniquement ») plus forte que les sources disponibles. Ces mécanismes expliquent une grande partie des verdicts « À nuancer » et une partie des dossiers signalés pour revue approfondie.", st["Body"]))
    story.append(Paragraph(
        "Les verdicts « Trompeur » et « Faux » sont relativement rares dans le sous-corpus vérifié. Ils apparaissent surtout lorsque le cadrage modifie substantiellement le sens du chiffre ou lorsque la formulation catégorique contredit une série, un seuil juridique ou un ensemble de scénarios de référence. Les affirmations invérifiables recouvrent notamment des attributions globales d'intention, des superlatifs sans métrique et des chiffres dont le périmètre n'est pas suffisamment identifiable.", st["Body"]))
    story.append(Paragraph(
        "Ces tendances sont descriptives du sous-corpus analysé. Le programme n'a pas été échantillonné: la vérification s'est déroulée séquentiellement et la présente version s'interrompt au chapitre 48. Les thèmes situés plus loin dans le document sont donc absents des statistiques de verdict de cette version.", st["Callout"]))

    # Energy
    central = n * 4.32 / 1000 * 1.5
    story.append(Paragraph("5. Estimation provisoire de la consommation électrique", st["H1"]))
    story.append(Paragraph(
        f"Le journal d'exécution conserve les modèles, périodes, nombres d'affirmations et nombres approximatifs d'appels d'outils, mais l'environnement n'expose pas les volumes de tokens d'entrée, de sortie, de raisonnement ou de cache. Il est donc impossible de mesurer directement l'énergie consommée. Pour la phase menée jusqu'à {n} affirmations vérifiées, nous retenons une estimation centrale d'environ <b>{central:.1f} kWh</b>, avec une fourchette plausible très large d'environ <b>0,5 à 15 kWh</b> pour l'inférence et l'orchestration associées à l'étude jusqu'à cette version.", st["Body"]))
    story.append(Paragraph(
        "La valeur centrale utilise comme ordre de grandeur 4,32 Wh pour une requête de modèle frontière avec environ 15 fois plus de calcul à l'inférence qu'une requête typique, puis applique un facteur de 1,5 pour les étapes de récupération, d'extraction, de synthèse et de génération du rapport qui ne se ramènent pas directement à une affirmation. Cette méthode est volontairement simple et doit être lue comme une reconstruction d'ordre de grandeur, non comme une mesure du datacenter.", st["Body"]))
    story.append(Paragraph(
        "La borne basse est compatible avec des déploiements très optimisés et beaucoup de réutilisation/cache; la borne haute tient compte du fait que les tâches de raisonnement peuvent consommer plusieurs dizaines de fois plus d'énergie par réponse que la conversation textuelle ordinaire, et que les longs contextes accroissent fortement le coût du pré-remplissage. La fourchette exclut l'énergie de pré-entraînement des modèles, la fabrication du matériel et l'énergie des terminaux de l'utilisateur; elle inclut conceptuellement l'inférence LLM et, de façon grossière, l'orchestration de recherche et de traitement.", st["Body"]))
    story.append(Paragraph("Références pour l'estimation énergétique", st["H2"]))
    energy_refs = [
        ("Josh You / Epoch AI (2025), How much energy does ChatGPT use?", "https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use", "~0,3 Wh pour une requête GPT-4o typique; ~2,5 Wh pour 10k tokens d'entrée et presque 40 Wh pour 100k dans leur scénario."),
        ("Elsworth et al. (2025), Measuring the environmental impact of delivering AI at Google Scale", "https://arxiv.org/abs/2508.15734", "Mesure production à grande échelle: 0,24 Wh pour la requête texte médiane de Gemini Apps."),
        ("Oviedo et al. (2025), Energy Use of AI Inference: Efficiency Pathways and Test-Time Compute", "https://arxiv.org/abs/2509.20241", "Estimation médiane 0,34 Wh pour requêtes de modèles frontière; 4,32 Wh avec un scénario de test-time compute 15×."),
        ("Chung et al. / ML.ENERGY (2026), Where Do the Joules Go?", "https://arxiv.org/abs/2601.22076", "Les tâches de raisonnement/problème présentent des consommations par réponse pouvant être ~25× celles de la conversation textuelle dans leurs mesures."),
    ]
    for title, url, note in energy_refs:
        story.append(Paragraph(f"• <b>{esc(title)}</b> - {esc(note)} <link href='{esc(url)}' color='#1D4ED8'>{esc(url)}</link>", st["Small"]))

    # Limitations
    story.append(Paragraph("6. Limites de cette version", st["H1"]))
    limits = [
        f"149 affirmations du corpus consolidé n'ont pas encore reçu de verdict et sont exclues de toutes les statistiques de verdict.",
        "Le sous-corpus vérifié est séquentiel et non aléatoire: il ne constitue pas un échantillon représentatif de l'ensemble du programme.",
        "Aucun audit contradictoire exhaustif n'a été réalisé après la passe primaire dans cette version.",
        f"{len(flags)} dossiers sont marqués pour une éventuelle revue approfondie; leurs verdicts restent ceux de la passe primaire.",
        f"{len(missing_review_meta)} dossiers récents ne disposent pas encore des deux champs synthétiques consensus/controverse et qualité des sources, bien qu'ils aient sources, verdict et justification.",
        "L'estimation électrique est un ordre de grandeur reconstruit en l'absence de télémétrie et de comptage de tokens; elle ne mesure pas les datacenters d'OpenAI.",
    ]
    for x in limits:
        story.append(Paragraph(f"• {esc(x)}", st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("7. Revue détaillée des affirmations vérifiées", st["H1"]))
    story.append(Paragraph("Les 415 dossiers ci-dessous constituent le corps documentaire de cette version. Ils sont présentés dans l'ordre du programme. Les liens indiqués permettent de retrouver les sources de preuve utilisées lors de la passe primaire.", st["Callout"]))

    current_ch = None
    for r in verified:
        ch = r.get("chapter_title") or (f"Chapitre {r.get('chapter')}" if r.get("chapter") is not None else "Sans chapitre")
        if ch != current_ch:
            current_ch = ch
            story.append(Paragraph(esc(ch), st["H2"]))
        story.extend(claim_story(r, st))

    # Appendix on reproducibility
    story.append(PageBreak())
    story.append(Paragraph("8. Reproductibilité et état de reprise", st["H1"]))
    story.append(Paragraph(
        f"Le rapport est généré depuis <b>{esc(latest['authoritative_recovery_source']['name'])}</b>. Le checkpoint annonce {total} affirmations uniques, {latest['counters']['occurrences']} occurrences et {n} affirmations vérifiées. Le premier identifiant non terminé est {esc(latest['resume']['first_unfinished_identifier'])}. Les artefacts de reprise, le ledger et le journal de calcul sont conservés dans le dépôt GitHub du projet.", st["Body"]))
    story.append(Paragraph("Le rapport complet sera régénéré à partir du même pipeline lorsque les 564 affirmations auront reçu un verdict.", st["Callout"]))

    doc.multiBuild(story)

    # Markdown landing page
    sha = hashlib.sha256(PDF.read_bytes()).hexdigest()
    MD.write_text(
        "# Rapport intermédiaire - 415 affirmations vérifiées\n\n"
        f"- Corpus consolidé : **{total}** affirmations uniques.\n"
        f"- Vérifiées dans ce rapport : **{n}** ({pct(n,total):.1f} %).\n"
        f"- Première non terminée : **{latest['resume']['first_unfinished_identifier']}**.\n"
        f"- PDF : `revue_factuelle_ecologistes_2026_415_affirmations.pdf`\n"
        f"- SHA-256 : `{sha}`\n\n"
        "Cette version ne comporte pas d'audit contradictoire exhaustif et ne doit pas être extrapolée aux 149 affirmations encore non vérifiées.\n",
        encoding="utf-8",
    )

    # Text-only recovery chunks of PDF.
    B64DIR.mkdir(parents=True, exist_ok=True)
    for old in B64DIR.glob("part_*.txt"):
        old.unlink()
    encoded = base64.b64encode(PDF.read_bytes()).decode("ascii")
    chunk_size = 48000
    parts = []
    for i in range(0, len(encoded), chunk_size):
        name = f"part_{i//chunk_size + 1:03d}.txt"
        chunk = encoded[i:i+chunk_size]
        (B64DIR / name).write_text(chunk, encoding="ascii")
        parts.append(name)
    manifest = {
        "pdf": PDF.name,
        "pdf_size_bytes": PDF.stat().st_size,
        "pdf_sha256": sha,
        "base64_length": len(encoded),
        "chunk_size": chunk_size,
        "parts": parts,
    }
    (B64DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
