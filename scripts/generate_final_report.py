#!/usr/bin/env python3
"""Generate and validate the final exhaustive factual-review report."""

from __future__ import annotations
import base64, hashlib, json, lzma, re, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/final"
PDF=OUT/"revue_factuelle_programme_ecologistes_2026.pdf"
MD=OUT/"revue_factuelle_programme_ecologistes_2026.md"
MANIFEST=OUT/"REPORT_MANIFEST.json"
ALLOWED=["Exact","Globalement exact","À nuancer","Trompeur","Faux","Invérifiable ou insuffisamment étayé"]
COLORS={"Exact":"#166534","Globalement exact":"#4D7C0F","À nuancer":"#B45309","Trompeur":"#C2410C","Faux":"#991B1B","Invérifiable ou insuffisamment étayé":"#475569"}

def esc(x):
    return str("" if x is None else x).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def txt(x):
    if x == "À rétablir": return "Non renseigné dans le ledger final"
    if isinstance(x,list): return "; ".join(map(str,x))
    if isinstance(x,dict): return json.dumps(x,ensure_ascii=False)
    return str(x or "")

def fmt_fr(x):
    return ("%.1f" % float(x)).replace(".", ",")

def load():
    latest=json.loads((ROOT/"checkpoints/latest.json").read_text())
    ref=latest["authoritative_recovery_source"]; p=ROOT/"checkpoints"/ref["name"]
    raw=lzma.decompress(base64.b64decode(p.read_text()))
    sha=hashlib.sha256(raw).hexdigest()
    if sha != ref["uncompressed_sha256"]: raise RuntimeError("checkpoint SHA décompressé incohérent")
    cp=json.loads(raw); rows=cp["restored_claim_ledger"]
    if len(rows)!=564 or len({r.get("id") for r in rows})!=564: raise RuntimeError("corpus non conforme")
    if any(r.get("verification_status")!="vérifiée" for r in rows): raise RuntimeError("affirmation non vérifiée")
    return latest,ref,p,rows

def fonts():
    reg=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"); bold=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if reg.exists():
        pdfmetrics.registerFont(TTFont("R",str(reg))); pdfmetrics.registerFont(TTFont("B",str(bold))); return "R","B"
    return "Helvetica","Helvetica-Bold"

class Doc(BaseDocTemplate):
    def __init__(self,*a,styles,**kw):
        super().__init__(*a,**kw); self.s=styles
        self.addPageTemplates(PageTemplate(id="p",frames=[Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id="f")],onPage=self.footer))
    def footer(self,c,d):
        c.saveState(); c.setStrokeColor(colors.HexColor("#CBD5E1")); c.line(self.leftMargin,13*mm,A4[0]-self.rightMargin,13*mm)
        c.setFillColor(colors.HexColor("#64748B")); c.setFont(self.s["r"],7.5)
        c.drawString(self.leftMargin,8.5*mm,"Revue factuelle du programme des Écologistes 2026 - version finale")
        c.drawRightString(A4[0]-self.rightMargin,8.5*mm,"p. %d" % d.page); c.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and f.style.name in ("H1","H2"):
            lev=0 if f.style.name=="H1" else 1; name="h-%d-%d" % (self.page,abs(hash(f.getPlainText())))
            self.canv.bookmarkPage(name); self.canv.addOutlineEntry(f.getPlainText(),name,lev,closed=False); self.notify("TOCEntry",(lev,f.getPlainText(),self.page,name))

def make_styles(r,b):
    return {"r":r,"b":b,
      "Title":ParagraphStyle("Title",fontName=b,fontSize=25,leading=30,textColor=colors.HexColor("#0F172A"),spaceAfter=12),
      "H1":ParagraphStyle("H1",fontName=b,fontSize=16,leading=20,textColor=colors.HexColor("#0F172A"),spaceBefore=10,spaceAfter=7,keepWithNext=True),
      "H2":ParagraphStyle("H2",fontName=b,fontSize=12,leading=15,textColor=colors.HexColor("#1E293B"),spaceBefore=9,spaceAfter=5,keepWithNext=True),
      "H3":ParagraphStyle("H3",fontName=b,fontSize=10,leading=13,textColor=colors.HexColor("#0F172A"),spaceBefore=7,spaceAfter=3,keepWithNext=True),
      "Body":ParagraphStyle("Body",fontName=r,fontSize=8.8,leading=12.6,textColor=colors.HexColor("#1F2937"),spaceAfter=4),
      "Small":ParagraphStyle("Small",fontName=r,fontSize=7.6,leading=10.2,textColor=colors.HexColor("#475569"),spaceAfter=2),
      "Tiny":ParagraphStyle("Tiny",fontName=r,fontSize=6.7,leading=8.7,textColor=colors.HexColor("#475569"),spaceAfter=1),
      "Quote":ParagraphStyle("Quote",fontName=r,fontSize=8.7,leading=12.2,leftIndent=8,rightIndent=4,textColor=colors.HexColor("#334155"),spaceAfter=4)}

def source(s,st):
    title=txt(s.get("title") or s.get("id") or "Source")
    meta=" - ".join(x for x in [txt(s.get("publisher")),txt(s.get("publication_date"))] if x)
    url=txt(s.get("url"))
    head=esc(title + ((" - "+meta) if meta else ""))
    return Paragraph("• "+head+((" - <link href='%s' color='#1D4ED8'>%s</link>" % (esc(url).replace("'","%27"),esc(url))) if url else ""),st["Tiny"])

def claim(row,st):
    page=", ".join(map(str,row.get("pdf_pages") or [])) or "?"
    chapter=txt(row.get("chapter_title") or row.get("chapter") or "Sans chapitre")
    out=[Paragraph("%s - %s - p. %s" % (esc(row["id"]),esc(chapter),esc(page)),st["H3"])]
    verdict=txt(row.get("verdict")); tab=Table([[Paragraph("<b>Verdict</b><br/><font color='white'>%s</font>"%esc(verdict),st["Small"]),Paragraph("<b>Confiance</b><br/>%s"%esc(txt(row.get("confidence")) or "Non renseignée"),st["Small"]),Paragraph("<b>Type</b><br/>%s"%esc(txt(row.get("claim_type")) or "Non renseigné"),st["Small"])]],colWidths=[52*mm,45*mm,62*mm])
    tab.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),colors.HexColor(COLORS[verdict])),("TEXTCOLOR",(0,0),(0,0),colors.white),("BACKGROUND",(1,0),(-1,0),colors.HexColor("#F8FAFC")),("BOX",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),("INNERGRID",(0,0),(-1,-1),.25,colors.HexColor("#E2E8F0")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)])); out += [tab,Spacer(1,3)]
    if row.get("quote"): out.append(Paragraph("« %s »"%esc(row["quote"]),st["Quote"]))
    if row.get("context_needed") and row.get("context"): out.append(Paragraph("<b>Contexte du programme.</b> %s"%esc(txt(row["context"])),st["Small"]))
    out.append(Paragraph("<b>Affirmation normalisée.</b> %s"%esc(txt(row.get("normalized_claim"))),st["Body"]))
    for label,key in [("Rôle argumentatif","argumentative_role"),("Politiques influencées","policies"),("Occurrences complémentaires","occurrences")]:
        if row.get(key): out.append(Paragraph("<b>%s.</b> %s"%(label,esc(txt(row[key]))),st["Small"]))
    out.append(Paragraph("<b>Justification.</b> %s"%esc(txt(row.get("justification"))),st["Body"]))
    out.append(Paragraph("<b>Consensus / controverse.</b> %s<br/><b>Qualité des sources.</b> %s"%(esc(txt(row.get("consensus_or_controversy"))),esc(txt(row.get("source_quality")))),st["Small"]))
    out.append(Paragraph("<b>Sources utilisées.</b>",st["Small"])); out += [source(s,st) for s in row.get("sources",[])]
    out.append(Spacer(1,6)); return out

def write_md(latest,ref,rows,counts,energy):
    lines=["# Revue factuelle du programme des Écologistes 2026","","Version finale. Analyse méthodologiquement indépendante et politiquement neutre.","","## Résultats globaux",""]
    for v in ALLOWED: lines.append("- %s : %d (%.1f %%)"%(v,counts[v],100*counts[v]/len(rows)))
    lines += [
        "",
        "## Méthodologie",
        "",
        "Le corpus couvre 208 pages et 66 chapitres. Les affirmations à rôle argumentatif substantiel ont été normalisées, dédupliquées et vérifiées en privilégiant les sources primaires, institutionnelles et scientifiques. Une passe primaire complète, une résolution systématique des sources, un nettoyage, une passe de cohérence ciblée et une QA mécanique finale ont été réalisés. Aucun second audit contradictoire exhaustif des 564 dossiers n'a été mené.",
        "",
        "## Empreinte énergétique totale estimée de l'analyse",
        "",
        "**Consommation électrique totale estimée pour l'ensemble de l'analyse : %s kWh** en valeur centrale, avec un intervalle plausible de **%s à %s kWh**."%(fmt_fr(energy["estimate_kwh_central"]),fmt_fr(energy["estimate_kwh_low"]),fmt_fr(energy["estimate_kwh_high"])),
        "",
        "Il s'agit d'une estimation attribuable à l'inférence IA documentée, et non d'une mesure de l'infrastructure OpenAI. Aucun comptage de tokens n'était disponible. La méthode finale reconstruit des batches agentiques et des requêtes équivalentes ; l'entraînement, la fabrication du matériel, le poste utilisateur, le réseau, GitHub et les impacts indirects sont hors périmètre principal.",
        "",
        "L’estimation intermédiaire de 2,7 kWh reposait sur l’approximation « une requête lourde par affirmation ». Elle est remplacée ici par une reconstruction plus fine des batches agentiques et des continuations autour des outils et recherches; aucun changement n’est apporté aux 564 évaluations factuelles.",
        "",
        "Méthodologie détaillée : `metrics/energy_estimate.md` et `metrics/energy_estimate.json`.",
        "",
        "## Revue détaillée",
        ""
    ]
    for r in rows:
        lines += ["### %s - %s - p. %s"%(r["id"],txt(r.get("chapter_title") or r.get("chapter")),", ".join(map(str,r.get("pdf_pages") or []))),"",
        "**Citation.** "+txt(r.get("quote")),"","**Affirmation normalisée.** "+txt(r.get("normalized_claim")),"","**Verdict.** "+txt(r.get("verdict")),"","**Justification.** "+txt(r.get("justification")),"","**Sources.**"]
        for s in r.get("sources",[]): lines.append("- [%s](%s)"%(txt(s.get("title") or s.get("id") or "Source"),txt(s.get("url"))))
        lines.append("")
    lines += [
        "## Limites",
        "",
        "La revue dépend de la sélection des affirmations à rôle argumentatif, de choix de normalisation et de la disponibilité des données. Les causalités et projections conservent une incertitude propre. Il ne s'agit pas d'une réplication indépendante complète par un second analyste.",
        "",
        "## Conclusion",
        "",
        "Cette revue décrit la conformité factuelle des affirmations retenues et leurs limites ; elle ne constitue ni une note politique globale du programme ni une recommandation d'adopter ou de rejeter ses mesures.",
        ""
    ]
    MD.write_text("\n".join(lines),encoding="utf-8")

def main():
    latest,ref,cp_path,rows=load(); stats=json.loads((ROOT/"analysis/statistics_final.json").read_text()); energy=json.loads((ROOT/"metrics/energy_estimate.json").read_text())
    counts=Counter(r["verdict"] for r in rows)
    if {v:counts[v] for v in ALLOWED}!={v:stats["verdict_distribution"][v]["count"] for v in ALLOWED}: raise RuntimeError("statistiques incohérentes")
    OUT.mkdir(parents=True,exist_ok=True); r,b=fonts(); st=make_styles(r,b)
    doc=Doc(str(PDF),styles=st,pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=18*mm,bottomMargin=18*mm,title="Revue factuelle du programme des Écologistes 2026")
    S=[Spacer(1,30*mm),Paragraph("REVUE FACTUELLE",st["Small"]),Paragraph("Programme des Écologistes 2026",st["Title"]),Paragraph("Rapport final - 564 affirmations factuelles uniques",st["Body"]),Spacer(1,8*mm),Paragraph("Analyse fondée sur le checkpoint factuel autoritatif du dépôt. Elle évalue les affirmations selon les données disponibles à la date pertinente, sans appréciation du bien-fondé politique des mesures.",st["Body"]),PageBreak(),Paragraph("Sommaire",st["H1"])]
    toc=TableOfContents(); toc.levelStyles=[ParagraphStyle("t0",fontName=b,fontSize=9,leading=12),ParagraphStyle("t1",fontName=r,fontSize=8,leading=10,leftIndent=12)]; S += [toc,PageBreak(),Paragraph("1. Résumé exécutif",st["H1"])]
    exact=counts["Exact"]+counts["Globalement exact"]; severe=counts["Trompeur"]+counts["Faux"]
    S.append(Paragraph("Le corpus comprend 564 affirmations uniques et 568 occurrences relevées dans les 208 pages et 66 chapitres du programme. %d affirmations (%.1f %%) sont Exactes ou Globalement exactes; %d (%.1f %%) sont À nuancer; %d (%.1f %%) sont Trompeuses ou Fausses; %d (%.1f %%) sont Invérifiables ou insuffisamment étayées."%(exact,100*exact/564,counts["À nuancer"],100*counts["À nuancer"]/564,severe,100*severe/564,counts["Invérifiable ou insuffisamment étayé"],100*counts["Invérifiable ou insuffisamment étayé"]/564),st["Body"]))
    S.append(Paragraph("Ces proportions décrivent la précision factuelle des affirmations retenues, et non la qualité politique globale du programme. Les catégories « À nuancer », « Trompeur » et « Faux » sont distinctes: la première signale une imprécision non matériellement invalidante; la deuxième un cadrage susceptible d’induire une conclusion sensiblement différente; la troisième une incompatibilité substantielle avec les meilleures preuves disponibles.",st["Body"]))
    data=[["Verdict","Nombre","Part"]] + [[v,str(counts[v]),"%.1f %%"%(100*counts[v]/564)] for v in ALLOWED]; t=Table(data,colWidths=[95*mm,30*mm,35*mm],repeatRows=1); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E2E8F0")),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),("FONTNAME",(0,0),(-1,0),b),("FONTNAME",(0,1),(-1,-1),r),("FONTSIZE",(0,0),(-1,-1),8.2),("ALIGN",(1,1),(-1,-1),"RIGHT"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)])); S += [t,Paragraph("2. Méthodologie",st["H1"])]
    S.append(Paragraph("Les affirmations ont été sélectionnées lorsqu’elles jouaient un rôle argumentatif substantiel; les propositions indépendantes ont été séparées et les répétitions dédupliquées tout en conservant leurs occurrences. Les vérifications privilégient données primaires, institutions publiques, littérature scientifique et rapports reconnus. Période, périmètre, dénominateur, causalité, projections, incertitude et consensus ont été pris en compte.",st["Body"]))
    S.append(Paragraph("Une passe primaire complète, une résolution systématique des sources, un nettoyage, une passe de cohérence ciblée de 46 cas à risque et une QA finale ont été menés. En revanche, aucun second audit contradictoire exhaustif des 564 dossiers n’a été réalisé: claims_adversarially_audited = 0. Ce fait historique ne doit pas être masqué.",st["Body"]))
    S.append(Paragraph("3. Résultats et tendances",st["H1"]))
    by=defaultdict(Counter)
    for x in rows: by[txt(x.get("chapter_title") or x.get("chapter") or "Sans chapitre")][x["verdict"]]+=1
    ranked=sorted(((k,sum(v.values()),v["À nuancer"],v["Trompeur"]+v["Faux"]) for k,v in by.items()),key=lambda x:(x[3],x[2],x[1]),reverse=True)[:12]
    S.append(Paragraph("Les tendances décrites ici sont strictement descriptives. Les justifications font souvent apparaître les périodes, dénominateurs, généralisations, inférences causales, valeurs obsolètes, définitions imprécises et hypothèses de projection comme motifs de nuance.",st["Body"]))
    d=[["Chapitres les plus concernés (descriptif)","n","À nuancer","Trompeur + Faux"]]+[[Paragraph(esc(a),st["Tiny"]),str(n),str(x),str(y)] for a,n,x,y in ranked]; tt=Table(d,colWidths=[95*mm,18*mm,26*mm,30*mm],repeatRows=1); tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E2E8F0")),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#CBD5E1")),("FONTNAME",(0,0),(-1,0),b),("FONTSIZE",(0,0),(-1,-1),7.2),("VALIGN",(0,0),(-1,-1),"TOP"),("ALIGN",(1,1),(-1,-1),"RIGHT")])); S += [tt,Paragraph("4. Revue détaillée des 564 affirmations",st["H1"]),Paragraph("Chaque dossier ci-dessous reprend l’affirmation, le verdict, sa justification et les sources finales du ledger. Lorsqu’une même affirmation a plusieurs occurrences, celles-ci sont indiquées dans le dossier plutôt que répétées.",st["Body"])]
    current=None
    for row in rows:
        ch=txt(row.get("chapter_title") or row.get("chapter") or "Sans chapitre")
        if ch!=current: current=ch; S.append(Paragraph(esc(ch),st["H2"]))
        S += claim(row,st)
    energy_total="Consommation électrique totale estimée pour l'ensemble de l'analyse : <b>%s kWh</b> en valeur centrale, avec un intervalle plausible de <b>%s à %s kWh</b>."%(fmt_fr(energy["estimate_kwh_central"]),fmt_fr(energy["estimate_kwh_low"]),fmt_fr(energy["estimate_kwh_high"]))
    S += [PageBreak(),Paragraph("5. Limites",st["H1"]),Paragraph("Le corpus repose sur une sélection des affirmations à rôle argumentatif et sur des jugements nécessaires à la normalisation. Les données disponibles et la qualité des sources varient selon les sujets; causalités et projections conservent une incertitude propre. Cette revue n’est pas une réplication indépendante complète par un second analyste et est temporellement bornée aux connaissances disponibles à la date pertinente.",st["Body"]),Paragraph("6. Empreinte énergétique totale estimée de l’analyse",st["H1"]),Paragraph(energy_total,st["Body"]),Paragraph("Il s’agit d’une estimation attribuable aux interactions d’inférence IA documentées, et non d’une mesure de l’infrastructure OpenAI: aucun comptage de tokens n’était disponible. La méthode finale remplace l’estimation intermédiaire de 2,7 kWh, qui assimilait chaque affirmation à une requête lourde, par une reconstruction des batches agentiques et des continuations autour des outils et recherches; aucun changement n’est apporté aux 564 évaluations factuelles. Elle exclut notamment l’entraînement, la fabrication du matériel, le poste utilisateur, le réseau, GitHub et les impacts indirects. Les analogies domestiques éventuelles ne sont que des illustrations, pas une méthode de calcul.",st["Body"]),Paragraph("Références énergétiques: "+", ".join("<link href='%s' color='#1D4ED8'>%s</link>"%(esc(x["url"]),esc(x["title"])) for x in energy.get("references",[])),st["Small"]),Paragraph("7. Conclusion",st["H1"]),Paragraph("Cette revue décrit la conformité factuelle des affirmations retenues et les limites qui leur sont associées. Elle ne constitue ni une note politique du programme ni une recommandation d’adopter ou de rejeter ses mesures.",st["Body"])]
    doc.multiBuild(S); write_md(latest,ref,rows,counts,energy)
    reader=PdfReader(str(PDF)); text="\n".join(p.extract_text() or "" for p in reader.pages); expected={r["id"] for r in rows}; ids={i for i in expected if i in text}
    if ids!=expected: raise RuntimeError("IDs PDF incomplets: %d/%d"%(len(ids),len(expected)))
    if any((r["id"] not in text or r["verdict"] not in text) for r in rows): raise RuntimeError("contenu PDF incomplet")
    energy_probe=("%s kWh" % fmt_fr(energy["estimate_kwh_central"]))
    if energy_probe not in text or "Empreinte énergétique totale" not in text: raise RuntimeError("estimation énergétique totale absente du PDF")
    md_text=MD.read_text(encoding="utf-8")
    if energy_probe not in md_text or "Empreinte énergétique totale" not in md_text: raise RuntimeError("estimation énergétique totale absente de la source Markdown")
    if PDF.stat().st_size<100000: raise RuntimeError("PDF anormalement petit")
    links=sum(1 for p in reader.pages for a in (p.get("/Annots") or []) if a.get_object().get("/A"))
    if links==0: raise RuntimeError("liens PDF absents")
    render=OUT/"qa_render"; render.mkdir(exist_ok=True); subprocess.run(["pdftoppm","-f","1","-l",str(len(reader.pages)),"-scale-to","900","-png",str(PDF),str(render/"page")],check=True)
    imgs=list(render.glob("*.png"))
    if len(imgs)!=len(reader.pages) or any(p.stat().st_size<1000 for p in imgs): raise RuntimeError("rendu PDF invalide")
    sha=hashlib.sha256(PDF.read_bytes()).hexdigest()
    manifest={"generated_at_utc":datetime.now(timezone.utc).isoformat(),"checkpoint_factuel_utilise":ref["name"],"sha256_checkpoint":hashlib.sha256(cp_path.read_bytes()).hexdigest(),"checkpoint_uncompressed_sha256":ref["uncompressed_sha256"],"statistiques_finales":{v:counts[v] for v in ALLOWED},"estimation_energetique_kwh":{"central":energy["estimate_kwh_central"],"low":energy["estimate_kwh_low"],"high":energy["estimate_kwh_high"],"section_verified":True},"pdf":{"name":PDF.name,"size_bytes":PDF.stat().st_size,"pages":len(reader.pages),"sha256":sha,"link_annotations":links},"source":{"name":MD.name,"sha256":hashlib.sha256(MD.read_bytes()).hexdigest()},"qa":{"ids":len(ids),"rendered_pages":len(imgs),"energy_section_verified":True,"status":"passed"}}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps(manifest,ensure_ascii=False))
if __name__=="__main__": main()
