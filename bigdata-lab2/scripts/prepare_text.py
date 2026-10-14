#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把下载到的 HTML 网页或纯文本文件转换成用于分词的纯文本。

用法: python3 prepare_text.py <input> <output>
  - .html/.htm: 抽取可见文本（忽略 script/style），按块级标签换行
  - .txt      : 去掉分页符与页码行，统一换行
"""
import html as html_mod
import re
import sys
from html.parser import HTMLParser

BLOCK_TAGS = {"p", "div", "br", "li", "tr", "td", "th", "h1", "h2", "h3", "h4",
              "h5", "h6", "pre", "table", "ul", "ol", "section", "article",
              "header", "footer", "nav", "blockquote", "dt", "dd"}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip > 0:
            self.skip -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def clean(text):
    text = html_mod.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\f", "\n", text)                     # 分页符 -> 换行
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main():
    src, dst = sys.argv[1], sys.argv[2]
    raw = open(src, encoding="utf-8", errors="ignore").read()
    if src.lower().endswith((".html", ".htm")) or "<html" in raw[:2000].lower():
        parser = TextExtractor()
        parser.feed(raw)
        out = "".join(parser.parts)
    else:
        out = raw
    open(dst, "w", encoding="utf-8").write(clean(out))
    print("converted: %s -> %s" % (src, dst))


if __name__ == "__main__":
    main()
