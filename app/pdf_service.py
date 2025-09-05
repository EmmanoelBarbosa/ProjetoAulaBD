from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def gerar_relatorio_produtos(dashboard_data):
    """
    Gera um PDF com os dados do dashboard, incluindo:
    - Total de clientes
    - Total de produtos
    - Total de vendas
    - Receita total
    - Produtos mais vendidos
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Relatório de Produtos e Vendas")

    # Totais
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 100, f"Total de clientes: {dashboard_data.get('total_clientes', 0)}")
    pdf.drawString(50, height - 120, f"Total de produtos: {dashboard_data.get('total_produtos', 0)}")
    pdf.drawString(50, height - 140, f"Total de vendas: {dashboard_data.get('total_vendas', 0)}")
    pdf.drawString(50, height - 160, f"Receita total: R$ {dashboard_data.get('receita_total', 0):.2f}")

    # Produtos mais vendidos
    pdf.drawString(50, height - 200, "Produtos mais vendidos:")
    y = height - 220
    for produto in dashboard_data.get('produtos_mais_vendidos', []):
        pdf.drawString(60, y, f"{produto['nome']} - {produto['total_vendido']} vendidos")
        y -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()