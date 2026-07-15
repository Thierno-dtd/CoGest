import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

from django.conf import settings


def _fmt(v):
    try:
        return f"{int(round(float(v))):,}".replace(',', ' ') + f" {settings.DEVISE}"
    except (TypeError, ValueError):
        return str(v)


def generer_pdf_facture(facture):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm,
                             leftMargin=18 * mm, rightMargin=18 * mm)
    styles = getSampleStyleSheet()
    titre_style = ParagraphStyle('Titre', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#111827'))
    sous_titre = ParagraphStyle('Sous', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#6B7280'))
    normal = styles['Normal']
    droite = ParagraphStyle('Droite', parent=styles['Normal'], alignment=TA_RIGHT)

    elements = []
    elements.append(Paragraph(settings.NOM_ENTREPRISE, titre_style))
    elements.append(Paragraph("Libreville, Gabon", sous_titre))
    elements.append(Spacer(1, 10 * mm))

    entete_data = [
        [Paragraph(f"<b>Facture N° :</b> {facture.numero}", normal),
         Paragraph(f"<b>Type :</b> {facture.get_type_facture_display()}", droite)],
        [Paragraph(f"<b>Date de facturation :</b> {facture.date_facturation.strftime('%d/%m/%Y')}", normal),
         Paragraph(f"<b>Échéance :</b> {facture.date_echeance.strftime('%d/%m/%Y')}", droite)],
    ]
    t = Table(entete_data, colWidths=[90 * mm, 82 * mm])
    t.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    elements.append(t)
    elements.append(Spacer(1, 6 * mm))

    tiers = facture.tiers
    nom_tiers = getattr(tiers, 'nom_complet', None) or getattr(tiers, 'raison_sociale', '—')
    libelle_tiers = "Client" if facture.type_facture == 'VENTE' else "Fournisseur"
    elements.append(Paragraph(f"<b>{libelle_tiers} :</b> {nom_tiers}", normal))
    if getattr(tiers, 'telephone', ''):
        elements.append(Paragraph(f"Téléphone : {tiers.telephone}", sous_titre))
    if getattr(tiers, 'adresse', ''):
        elements.append(Paragraph(f"Adresse : {tiers.adresse}", sous_titre))
    elements.append(Spacer(1, 8 * mm))

    data = [["Désignation", "Qté", "P.U.", "TVA", "Montant TTC"]]
    for ligne in facture.lignes:
        produit = ligne.produit
        qte = ligne.quantite_achetee if hasattr(ligne, 'quantite_achetee') else ligne.quantite_vendue
        pu = ligne.prix_achat_unitaire_applique if hasattr(ligne, 'prix_achat_unitaire_applique') else ligne.prix_vente_unitaire_applique
        data.append([
            produit.designation,
            str(qte),
            _fmt(pu),
            f"{float(ligne.taux_tva_applique) * 100:.0f}%",
            _fmt(ligne.montant_ttc),
        ])

    table = Table(data, colWidths=[70 * mm, 20 * mm, 30 * mm, 20 * mm, 32 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 8 * mm))

    totaux_data = [
        ["Montant HT", _fmt(facture.montant_ht)],
        ["Montant TVA", _fmt(facture.montant_tva)],
        ["Montant TTC", _fmt(facture.montant_ttc)],
        ["Montant payé", _fmt(facture.montant_paye)],
        ["Solde restant", _fmt(facture.solde_restant)],
    ]
    t2 = Table(totaux_data, colWidths=[130 * mm, 42 * mm])
    t2.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('LINEABOVE', (0, 2), (-1, 2), 0.8, colors.HexColor('#111827')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t2)

    elements.append(Spacer(1, 12 * mm))
    statut = "SOLDÉE" if facture.est_soldee else ("EN RETARD" if facture.est_en_retard else "EN COURS")
    elements.append(Paragraph(f"<b>Statut :</b> {statut}", normal))
    elements.append(Spacer(1, 20 * mm))
    elements.append(Paragraph("Merci pour votre confiance.", sous_titre))

    doc.build(elements)
    buffer.seek(0)
    return buffer
