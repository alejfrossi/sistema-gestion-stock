from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List
from fpdf import FPDF

app = FastAPI()

class ProductSchema(BaseModel):
    name: str
    sku: str = "-"
    quantity: int
    price: float

class ReportRequest(BaseModel):
    products: List[ProductSchema]

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Reporte de Stock', 0, 1, 'C')
        self.ln(5)

@app.post("/generate-pdf/")
def generate_pdf(data: ReportRequest):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Encabezados de la tabla
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, "SKU", 1, 0, 'C', fill=True)
    pdf.cell(80, 10, "Producto", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Cantidad", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Precio", 1, 1, 'C', fill=True)

    # Filas de datos
    for product in data.products:
        pdf.cell(40, 10, str(product.sku), 1)
        pdf.cell(80, 10, product.name[:35], 1)
        pdf.cell(30, 10, str(product.quantity), 1, 0, 'C')
        pdf.cell(40, 10, f"${product.price}", 1, 1, 'R')

    pdf_bytes = pdf.output()

    return Response(content=bytes(pdf_bytes), media_type="application/pdf")