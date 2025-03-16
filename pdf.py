import os
import uuid
from textwrap import wrap
from storage import storage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import retreiver

def text_to_pdf(base, doc, hash):
    print(doc)
    global index
    filename = uuid.uuid4()
    tmp = f'public/temp/{str(filename)}.pdf'
    c = canvas.Canvas(tmp, pagesize=A4)
    width, height = A4
    margin_x = 50  # Marge gauche/droite
    margin_top = 50  # Marge en haut
    margin_bottom = 50  # Marge en bas

    # Espace disponible pour le texte
    text_width = width - 2 * margin_x
    y_position = height - margin_top  # Position de départ du texte

    # Titre
    c.setFont("Helvetica-Bold", 20)
    title = f"{doc.get('Numero','')} {doc['Signataire'].split()[1]}".upper()
    tw = c.stringWidth(title, "Helvetica-Bold", 20)
    c.drawString((width - tw) / 2, y_position, title)
    y_position -= 40  # Décalage vers le bas

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y_position, f"Signataire {doc['Signataire']}")
    y_position -= 30  # Décalage vers le bas

    nodes = retreiver.get_decret(doc)
    max_chars_per_line = int(text_width / 5.5)

    for node in nodes:

        highlighted = node.node.hash in hash
        text = node.node.text
        c.setFont("Helvetica", 12)
        wrapped_text = wrap('•    ' + text, width=max_chars_per_line)
        from reportlab.pdfbase import pdfmetrics

        face = pdfmetrics.getFont("Helvetica").face

        if highlighted:
            string_height = (face.ascent - face.descent) / 1000 * 12
            c.setFillColorRGB(.98, .97, .1)
            c.rect(margin_x - 5, y_position + (face.ascent / 1000 * 12) + 2, int(text_width) + 5,
                   (-string_height + (face.descent / 1000 * 12)) * len(wrapped_text), fill=1, stroke=0)

        for line in wrapped_text:
            if y_position < margin_bottom:  # Vérifier si on atteint le bas de la page
                c.showPage()  # Nouvelle page
                c.setFont("Helvetica", 10)
                y_position = height - margin_top  # Reset à la nouvelle page

            if highlighted:
                c.setFillColorRGB(.98, 0, 0)
            else:
                c.setFillColorRGB(0, 0, 0)
            c.drawString(margin_x, y_position, line)

            y_position -= 15
        y_position -= 5

    c.save()
    object = open(tmp, 'rb').read()
    storage.sync_upload_file(str(filename), object, mime='application/pdf')
    return storage.sync_get_read_url(str(filename))