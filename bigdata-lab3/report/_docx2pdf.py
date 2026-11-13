# -*- coding: utf-8 -*-
"""Convert the lab3 report docx to PDF using Microsoft Word COM automation.

Word 在本机对中文路径打开文件不稳定，因此先把 docx 复制到 ASCII 临时路径，
转换后再把 PDF 复制回报告目录。同时输出页数并渲染每页 PNG 供检查。
"""
import os
import shutil
import tempfile

import win32com.client
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(BASE, "202400390057-李丰润-实验三.docx")
PDF = os.path.join(BASE, "202400390057-李丰润-实验三.pdf")

tmpdir = tempfile.mkdtemp(prefix="lab3pdf_")
tmp_docx = os.path.join(tmpdir, "report.docx")
tmp_pdf = os.path.join(tmpdir, "report.pdf")
shutil.copyfile(DOCX, tmp_docx)

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
pages = None
try:
    doc = word.Documents.Open(tmp_docx, ReadOnly=True)
    doc.Repaginate()
    pages = doc.ComputeStatistics(2)   # wdStatisticPages
    doc.SaveAs(tmp_pdf, FileFormat=17)  # wdFormatPDF
    doc.Close(False)
finally:
    word.Quit()

shutil.copyfile(tmp_pdf, PDF)
shutil.rmtree(tmpdir, ignore_errors=True)

print("PDF pages:", pages)

pages_dir = os.path.join(BASE, "pages")
os.makedirs(pages_dir, exist_ok=True)
d = pymupdf.open(PDF)
for i, page in enumerate(d):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4))
    pix.save(os.path.join(pages_dir, "page%02d.png" % (i + 1)))
print("rendered pages:", len(d))
