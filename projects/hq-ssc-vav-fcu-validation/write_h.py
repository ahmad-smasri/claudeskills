import re, shutil, zipfile, os
from compare import *

SRC = REGF
OUT = '/home/user/claudeskills/out/Appendix_A_Asset_Register_VAV_FCU_validated.xlsx'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

WRITE = {}
for r in results:
    if r['status'] in ('DIFF_NAME', 'DIFF_NUMBER', 'DIFF_BOTH'):
        v = new_value(r).strip()
        if v:
            WRITE[r['row']] = v
HEADER = 'ROOM NAME PER VAV / FCU LIST (WHERE DIFFERENT)'

def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

z = zipfile.ZipFile(SRC)
xml = z.read('xl/worksheets/sheet6.xml').decode('utf-8')

# style of D2, reused for the H2 header so it looks like the other headers
m = re.search(r'<c r="D2"([^>]*)>', xml)
hdr_style = ''
if m:
    sm = re.search(r's="(\d+)"', m.group(1))
    if sm:
        hdr_style = ' s="%s"' % sm.group(1)

targets = dict(WRITE)
targets[2] = HEADER
written = []

def fix_row(mo):
    head, body = mo.group(1), mo.group(2)
    rn = int(re.search(r'\br="(\d+)"', head).group(1))
    if rn not in targets:
        return mo.group(0)
    if re.search(r'<c r="H%d[^0-9]' % rn, body):        # never overwrite an existing H cell
        return mo.group(0)
    style = hdr_style if rn == 2 else ''
    cell = '<c r="H%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (rn, style, esc(targets[rn]))
    head = re.sub(r'spans="1:\d+"', 'spans="1:8"', head)
    written.append(rn)
    return '<row' + head + '>' + body + cell + '</row>'

xml2 = re.sub(r'<row([^>]*)>(.*?)</row>', fix_row, xml, flags=re.S)
assert len(written) == len(targets), (len(written), len(targets))

# widen column H so the text is readable
if '<cols>' in xml2:
    xml2 = xml2.replace('<cols>', '<cols><col min="8" max="8" width="46" customWidth="1"/>', 1)
else:
    xml2 = re.sub(r'(<sheetData>)', '<cols><col min="8" max="8" width="46" customWidth="1"/></cols>\\1', xml2, count=1)

zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == 'xl/worksheets/sheet6.xml':
        data = xml2.encode('utf-8')
    zout.writestr(item, data)
zout.close()
print('wrote %d cells (incl. header) to %s' % (len(written), OUT))
