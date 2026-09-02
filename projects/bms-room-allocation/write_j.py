import re, zipfile, os
import openpyxl
from ssc_alloc import ALLOC

SRC = '/root/.claude/uploads/7b732886-7f20-51be-97dc-21f5f8123adc/3527eedb-Copy_of_Appendix_A__Asset_Register_For_Ahmad_Only__Validated_Against_VAVs_and_FCUs_Locations_Excels.xlsx'
OUT = '/home/user/claudeskills/projects/bms-room-allocation/Appendix_A_Asset_Register_SSC_BMS_rooms.xlsx'
SSC_LO, SSC_HI = 1318, 1441
HEADER = 'ROOM PER BMS SCREEN (SSC)'


def reg_tag(bms):
    """BMS tag -> asset-register tag: FCU-0010 -> FCU0010, KEF-1F-0103 -> KEF0103"""
    t = bms.upper().replace('-', '_')
    m = re.match(r'^(VAV|FCU)_(\d+)$', t)
    if m:
        return m.group(1) + m.group(2)
    m = re.match(r'^(TEF|KEF|GEF|EF)_[A-Z0-9]+_(\d+)$', t)
    if m:
        return m.group(1) + m.group(2)
    m = re.match(r'^AHU_B_(\d+)$', t)
    if m:
        return 'AHUB_' + m.group(1)
    return t.replace('_', '')


wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['Controllable Asset Registry']
rows = {}
for i in range(SSC_LO, SSC_HI + 1):
    v = ws.cell(i, 1).value
    if v:
        rows[str(v).strip().upper()] = i

placed, unmatched = {}, []
for bms, room, screen, conf in ALLOC:
    t = reg_tag(bms)
    if t in rows:
        placed[rows[t]] = (room, bms, screen, conf)
    else:
        unmatched.append((bms, t, room, screen))

# --- write column J straight into the sheet XML, leaving everything else alone
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

z = zipfile.ZipFile(SRC)
name = 'xl/worksheets/sheet6.xml'
xml = z.read(name).decode('utf-8')
m = re.search(r'<c r="D2"([^>]*)>', xml)
sm = re.search(r's="(\d+)"', m.group(1)) if m else None
style = ' s="%s"' % sm.group(1) if sm else ''

targets = {i: v[0] for i, v in placed.items()}
targets[2] = HEADER
written = []

def fix(mo):
    head, body = mo.group(1), mo.group(2)
    rn = int(re.search(r'\br="(\d+)"', head).group(1))
    if rn not in targets or re.search(r'<c r="J%d[^0-9]' % rn, body):
        return mo.group(0)
    cell = '<c r="J%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (
        rn, style if rn == 2 else '', esc(targets[rn]))
    head = re.sub(r'spans="1:\d+"', 'spans="1:10"', head)
    written.append(rn)
    return '<row' + head + '>' + body + cell + '</row>'

xml2 = re.sub(r'<row([^>]*)>(.*?)</row>', fix, xml, flags=re.S)
# Widen column J by editing the <col> already there. Adding a second <col> for
# the same column makes <cols> overlap, which Excel treats as a repair case.
if re.search(r'<col min="10" max="10"[^>]*/>', xml2):
    xml2 = re.sub(r'<col min="10" max="10"[^>]*/>',
                  '<col min="10" max="10" width="40" customWidth="1"/>', xml2, count=1)
elif '<cols>' in xml2:
    xml2 = xml2.replace('<cols>', '<cols><col min="10" max="10" width="40" customWidth="1"/>', 1)
else:
    xml2 = re.sub(r'(<sheetData>)',
                  '<cols><col min="10" max="10" width="40" customWidth="1"/></cols>\\1', xml2, count=1)

# 2. The SSC block is a collapsed outline group - every row we just wrote to is
# hidden, so the column reads as empty on open. Expand it.
def unhide(mo):
    head = mo.group(1)
    rn = int(re.search(r'\br="(\d+)"', head).group(1))
    if SSC_LO <= rn <= SSC_HI:
        head = head.replace(' hidden="1"', '')
    if rn == SSC_LO - 1:
        head = head.replace(' collapsed="1"', '')
    return '<row' + head + '>'

xml2 = re.sub(r'<row([^>]*)>', unhide, xml2)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data = xml2.encode('utf-8') if it.filename == name else zin.read(it.filename)
    zout.writestr(it, data)
zout.close()

print('column J written on %d rows' % (len(written) - 1))
print('BMS units with no SSC register row:', unmatched)
