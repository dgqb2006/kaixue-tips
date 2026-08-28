import re, sys

src = open(r'D:\公众号\deploy_article\index.html', encoding='utf-8').read()

CARD_OPEN = '<div style="background:#F3FAF8;border:1px solid #D9EFE9;border-radius:14px;padding:16px 18px;margin:14px 0;">'
HEADER_OPEN = '<div style="background:linear-gradient(135deg,#1F9E8E 0%,#0F766E 100%);padding:36px 28px 32px;text-align:center;color:#ffffff;position:relative;">'

def wrap_cards(html):
    if CARD_OPEN not in html:
        return html
    parts = html.split(CARD_OPEN)
    out = [parts[0]]
    for seg in parts[1:]:
        i1 = seg.find('</div>')
        i2 = seg.find('</div>', i1 + 1)
        inner = seg[:i2]
        rest = seg[i2 + 6:]
        out.append('<table style="width:100%;border-collapse:collapse;margin:14px 0;"><tr><td style="background:#F3FAF8;border:1px solid #D9EFE9;padding:16px 18px;border-radius:14px;">' + inner + '</td></tr></table>' + rest)
    return ''.join(out)

def wrap_header(html):
    if HEADER_OPEN not in html:
        return html
    parts = html.split(HEADER_OPEN)
    out = [parts[0]]
    for seg in parts[1:]:
        idxs = []
        start = 0
        for _ in range(3):
            p = seg.find('</div>', start)
            if p < 0:
                break
            idxs.append(p)
            start = p + 6
        inner = seg[:idxs[-1]]
        rest = seg[idxs[-1] + 6:]
        out.append('<table style="width:100%;border-collapse:collapse;"><tr><td style="background:#1F9E8E;padding:36px 28px 32px;text-align:center;color:#ffffff;">' + inner + '</td></tr></table>' + rest)
    return ''.join(out)

# 移除会被微信忽略的 gradient 装饰条（不影响内容）
html = src
html = wrap_header(html)
html = wrap_cards(html)
# 去掉顶部/底部纯装饰渐变条（微信会丢，留着也无意义）
html = re.sub(r'<div style="height:8px;background:linear-gradient\([^"]*\);"></div>', '', html)
html = re.sub(r'<div style="height:6px;background:linear-gradient\([^"]*\);"></div>', '', html)

# 校验标签平衡
from html.parser import HTMLParser
class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.void = {'meta','br','img','hr','input','link'}
    def handle_starttag(self, tag, attrs):
        if tag not in self.void:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.void:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
c = Checker()
c.feed(html)
print("未闭合标签栈:", c.stack)
print("表格卡片数:", html.count('<table'))
print("仍含 card div:", CARD_OPEN in html)

open(r'D:\公众号\deploy_article\index.html', 'w', encoding='utf-8').write(html)
print("已写入 index.html (表格兼容版)")
