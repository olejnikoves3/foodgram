from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse


def generate_pdf(ingredients_summary):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle('Список покупок')
    pdf.setFont('Times-Roman', 16)
    pdf.drawString(100, height - 50, 'Список ингредиентов для покупок')
    pdf.setFont('Times-Roman', 12)
    y_position = height - 100
    for ingredient in ingredients_summary:
        amount = ingredients_summary[ingredient]['amount']
        mes_unit = ingredients_summary[ingredient]['mes_unit']
        pdf.drawString(100, y_position, f'{ingredient}: {amount} {mes_unit}')
        y_position -= 20
        if y_position < 50:
            pdf.showPage()
            y_position = height - 50
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="Список покупок.pdf"')
    return response
