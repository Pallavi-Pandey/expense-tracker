from xhtml2pdf import pisa
from flask import render_template
import os

def export_to_pdf(expenses, balances, transactions, filename="report.pdf"):
    html = render_template("pdf_template.html", expenses=expenses, balances=balances, transactions=transactions)
    with open(filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html, dest=result_file)
    return pisa_status.err == 0
