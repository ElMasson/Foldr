#advanced_response_generation/pdf_generator.py

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO

def generate_pdf_report(project_name, session_state):
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf_path = os.path.join(output_dir, f"{project_name}_rapport.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))

    content = []

    # Titre
    content.append(Paragraph(f"Rapport de Projet: {project_name}", styles['Title']))
    content.append(Spacer(1, 12))

    # Contexte et Analyse
    content.append(Paragraph("Contexte de la Subvention", styles['Heading1']))
    content.append(Paragraph(session_state.subvention_context, styles['Justify']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Analyse d'Expert", styles['Heading1']))
    content.append(Paragraph(session_state.expert_advice, styles['Justify']))
    content.append(Spacer(1, 12))

    # Réponses Détaillées
    content.append(Paragraph("Réponses Détaillées", styles['Heading1']))
    for question, response_data in session_state.all_advanced_responses.items():
        content.append(Paragraph(question, styles['Heading2']))
        content.append(Paragraph(response_data['text'], styles['Justify']))
        content.append(Spacer(1, 12))

    # Ajouter un graphique si nécessaire
    if hasattr(session_state, 'funding_sources'):
        content.append(Paragraph("Répartition des Sources de Financement", styles['Heading1']))
        pie_chart = create_pie_chart(session_state.funding_sources)
        content.append(pie_chart)
        content.append(Spacer(1, 12))

    doc.build(content)

    return pdf_path

def create_pie_chart(data):
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 100
    pie.y = 0
    pie.width = 200
    pie.height = 200
    pie.data = list(data.values())
    pie.labels = list(data.keys())
    pie.slices.strokeWidth = 0.5
    drawing.add(pie)
    return drawing