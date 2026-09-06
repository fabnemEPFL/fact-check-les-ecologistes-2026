from __future__ import annotations

import json
import re
from pathlib import Path

import fitz


PDF = Path("upload/vdef-programme-1.pdf")
OUT = Path("tmp/claim_candidates.json")

CHAPTERS = {
    15: (1, "Gagner la bataille du climat"),
    19: (2, "Pouvoir se loger décemment"),
    22: (3, "Garantir la liberté de se déplacer autrement"),
    26: (4, "Adapter la France à +4 °C"),
    29: (5, "Restaurer la biodiversité terrestre"),
    31: (6, "Prendre soin des océans et de ses artisans"),
    34: (7, "Protéger nos forêts et l’économie sylvicole"),
    36: (8, "Améliorer la condition animale"),
    40: (9, "Sanctuariser l’accès à l’eau potable"),
    43: (10, "Préserver la terre"),
    45: (11, "Créer un droit à l’alimentation de qualité"),
    48: (12, "Transformer notre modèle agricole"),
    54: (13, "Assurer des rémunérations dignes"),
    56: (14, "Travailler mieux"),
    59: (15, "Soutenir la responsabilité des entreprises"),
    62: (16, "Changer les règles du marché"),
    65: (17, "Refonder le pacte fiscal"),
    69: (18, "Mettre la finance au service de l’économie réelle"),
    72: (19, "Prioriser l’économie circulaire"),
    76: (20, "Planifier une nouvelle industrialisation"),
    79: (21, "Protéger nos techno-diversités numériques"),
    86: (22, "Décentraliser les services publics"),
    89: (23, "Viser la réussite de tous les élèves"),
    93: (24, "Démocratiser l’enseignement supérieur"),
    95: (25, "Investir dans la recherche scientifique"),
    98: (26, "Ouvrir la politique culturelle"),
    102: (27, "Encourager un sport inclusif et décarboné"),
    107: (28, "Sortir de la civilisation des toxiques"),
    110: (29, "Améliorer la prévention et le parcours de soin"),
    113: (30, "Rendre accessible une offre de soin de qualité"),
    116: (31, "Adopter une autre réforme des retraites"),
    118: (32, "Lutter contre la pauvreté"),
    121: (33, "Lutter contre l’épidémie de solitude"),
    123: (34, "Soutenir toutes les familles"),
    125: (35, "Soutenir l’émancipation des jeunes"),
    127: (36, "Protéger le très grand âge"),
    129: (37, "Être solidaires face au deuil"),
    133: (38, "Éradiquer les violences sexistes et sexuelles"),
    135: (39, "Protéger les enfants en danger"),
    137: (40, "Amplifier la politique féministe"),
    140: (41, "Défendre les droits des personnes LGBTQIA+"),
    142: (42, "Bâtir une société antivalidiste"),
    145: (43, "Combattre le racisme, l’islamophobie, l’antisémitisme et l’antitsiganisme"),
    148: (44, "Réaliser l’égalité dans les quartiers populaires"),
    150: (45, "Atteindre l’égalité entre les villes et les ruralités"),
    152: (46, "Accomplir l’égalité avec tous les territoires dits d’Outre-mer"),
    155: (47, "Soutenir la vie associative et l’engagement citoyen"),
    159: (48, "Passer à la Première République Écologique et citoyenne"),
    162: (49, "Démocratiser la République"),
    164: (50, "Refonder une police républicaine"),
    166: (51, "Consacrer des moyens suffisants à la Justice"),
    168: (52, "Apaiser par la justice du quotidien"),
    170: (53, "Humaniser la prison"),
    172: (54, "Promouvoir la laïcité"),
    174: (55, "Défendre l’indépendance des médias"),
    177: (56, "Garantir les libertés de migration"),
    180: (57, "Lutter contre les terrorismes"),
    183: (58, "Lutter contre le narcotrafic"),
    185: (59, "Combattre la corruption"),
    189: (60, "Avancer vers une Europe fédérale"),
    192: (61, "Faire évoluer l’armée française dans l’Europe de la défense"),
    196: (62, "Soutenir l’Ukraine face à la Russie"),
    198: (63, "Adopter une nouvelle diplomatie de la paix"),
    201: (64, "Défendre la paix au Moyen-Orient"),
    203: (65, "Porter une politique de coopération postcoloniale"),
    206: (66, "Bifurquer vers une diplomatie féministe"),
}

PART_INTRO_PAGES = {14, 39, 52, 53, 84, 85, 105, 106, 132, 158, 188}
PREFACE_PAGES = set(range(2, 11))

EMPIRICAL_MARKERS = re.compile(
    r"(?:\d|%|€|million|milliard|hectare|km|tonne|degré|°C|"
    r"\best\b|\bsont\b|\bétait\b|\bétaient\b|\ba atteint\b|\breprésent|"
    r"\bdétient|\baccapare|\bcompte|\bcoûte|\bpermet|\bentraîne|\bproduit|"
    r"\baugmente|\bdiminue|\bréduit|\bfragilise|\bmenace|\bexpose|\bcontribue|"
    r"\bfavorise|\bimplique|\bdépend|\brésulte|\bsubit|\bsubissent|\bpâtit|"
    r"\bse distingue|\bplus (?:de|que)|\bmoins (?:de|que)|\bdeux fois|\bseul|"
    r"\bjamais|\bdéjà|\bactuellement|\baujourd’hui|\bchaque année|\bdepuis|"
    r"\bresponsable|\bprovoque|\bcause|\bimpact|\befficace|\binefficace|"
    r"\bdangereu|\bcher|\brapide|\blent|\bvulnérable|\bprécaire|\bdégrad|"
    r"\brecul|\bhausse|\bbaisse|\bcroissance|\binégalité|\bpauvreté|\brecord)",
    re.IGNORECASE,
)


def clean(text: str) -> str:
    text = text.replace("\xad", "").replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sentences(text: str) -> list[str]:
    # Conservative sentence splitting; keep semicolon-linked propositions together.
    text = clean(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ0-9\[«])", text) if len(s.strip()) > 15]


def chapter_for(page: int):
    starts = sorted(CHAPTERS)
    valid = [s for s in starts if s <= page]
    if not valid:
        return None, None
    start = valid[-1]
    return CHAPTERS[start]


doc = fitz.open(PDF)
candidates = []
for idx, page in enumerate(doc, 1):
    chapter_no, chapter_title = chapter_for(idx)
    blocks = page.get_text("blocks", sort=True)
    for bidx, block in enumerate(blocks):
        x0, y0, x1, y1, text, *_ = block
        text = clean(text)
        if not text or text == str(idx) or len(text) < 16:
            continue
        if re.fullmatch(r"\d+\. .{1,80}", text):
            continue
        context = "proposal"
        if idx in PREFACE_PAGES:
            context = "avant-propos"
        elif idx in PART_INTRO_PAGES:
            context = "introduction-partie"
        elif idx in CHAPTERS and x0 > 145 and y0 > 150:
            context = "introduction-chapitre"
        # A chapter-opening page can also contain proposal 1 in a separate low block.
        for sidx, sentence in enumerate(sentences(text)):
            keep = context != "proposal" or bool(EMPIRICAL_MARKERS.search(sentence))
            if not keep:
                continue
            candidates.append({
                "page": idx,
                "chapter": chapter_no,
                "chapter_title": chapter_title,
                "context": context,
                "block": bidx,
                "sentence": sidx,
                "text": sentence,
            })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
print(f"Wrote {len(candidates)} candidates to {OUT}")
from collections import Counter
print(Counter(x['context'] for x in candidates))
print(Counter(x['chapter'] for x in candidates))
