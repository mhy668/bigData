# -*- coding: utf-8 -*-
"""Convert the lab report docx to PDF using Microsoft Word COM automation,
then report the page count and render pages to PNG for review."""
import os
import sys

import win32com.client
import pymupdf

BASE = r"E:\大数据管理与分析\大数据实验二\bigdata-lab2\report"
DOCX = os.path.join(BASE, "202400390057-李丰润-实验二.docx")
PDF = os.path.join(BASE, "202400390057-李丰润-实验二.pdf")
PAGES = os.path.join(BASE, "pages")

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(DOCX, ReadOnly=False)
    # update fields / repaginate
    doc.Repaginate()
    pages = doc.ComputeStatistics(2)  # wdStatisticPages
    doc.SaveAs(PDF, FileFormat=17)    # wdFormatPDF
    doc.Close(False)
finally:
    word.Quit()

print("PDF pages:", pages)

os.makedirs(PAGES, exist_ok=True)
d = pymupdf.open(PDF)
for i, page in enumerate(d):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4))
    out = os.path.join(PAGES, "page%02d.png" % (i + 1))
    pix.save(out)
    print("rendered", out, pix.width, "x", pix.height)
print("done")
