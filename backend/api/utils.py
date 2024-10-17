from io import BytesIO
import os

from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


FONT_PATH = os.path.join(settings.BASE_DIR,
                         'fonts/dajavu_sans/DejaVuSans.ttf')


def generate_pdf(ingredients_summary):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    title = 'Список ингредиентов для покупок'
    pdf.setTitle(title)
    pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
    pdf.setFont('DejaVuSans', 16)
    title_width = pdf.stringWidth(title, 'DejaVuSans', 16)
    x_position = (width - title_width) / 2
    pdf.drawString(x_position, height - 50, title)
    pdf.setFont('DejaVuSans', 12)
    y_position = height - 100
    counter = 1
    for ingredient in ingredients_summary:
        amount = ingredients_summary[ingredient]['amount']
        mes_unit = ingredients_summary[ingredient]['mes_unit']
        pdf.drawString(100, y_position,
                       f'{counter}. {ingredient}: {amount} {mes_unit}')
        counter += 1
        y_position -= 20
        if y_position < 50:
            pdf.showPage()
            pdf.setFont('DejaVuSans', 12)
            y_position = height - 50
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="Список покупок.pdf"')
    return response
