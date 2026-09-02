import re, zipfile, os
import openpyxl
from hq_alloc import HQ, SSC_EXTRA
from gf_alloc import GF
from bf_alloc import BF
from ff_alloc import FF1

SRC = '/root/.claude/uploads/7b732886-7f20-51be-97dc-21f5f8123adc/849d736f-Appendix_A_Asset_Register_SSC_HQ_BMS_rooms_1.xlsx'
OUT = '/home/user/claudeskills/projects/bms-room-allocation/Appendix_A_Asset_Register_SSC_HQ_BMS_rooms.xlsx'
HQ_LO, HQ_HI = 4, 764
SSC_LO, SSC_HI = 1318, 1441
HEADER = 'ROOM PER BMS SCREEN'

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['Controllable Asset Registry']
def index(lo, hi):
    d = {}
    for i in range(lo, hi + 1):
        v = ws.cell(i, 1).value
        if v:
            d[str(v).strip().upper()] = i
    return d

hq_rows, ssc_rows = index(HQ_LO, HQ_HI), index(SSC_LO, SSC_HI)
targets = {}
for bms, room, screen, conf in HQ:
    t = bms.replace('-', '')
    if t in hq_rows:
        targets[hq_rows[t]] = room
    else:
        print('!! no HQ register row for', bms)
for bms, room, screen, conf in list(GF) + list(BF) + list(FF1):
    if not room:
        continue                     # nothing the screen names - leave blank
    t = bms.replace('-', '')
    if t in hq_rows:
        targets.setdefault(hq_rows[t], room)   # green rows already set win
    else:
        print('!! no HQ register row for', bms)
for bms, room, screen, conf in SSC_EXTRA:
    t = bms.replace('-', '')
    if t in ssc_rows:
        targets[ssc_rows[t]] = room
    else:
        print('!! no SSC register row for', bms)
targets[2] = HEADER

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

z = zipfile.ZipFile(SRC)
name = 'xl/worksheets/sheet6.xml'
xml = z.read(name).decode('utf-8')
m = re.search(r'<c r="D2"([^>]*)>', xml)
sm = re.search(r's="(\d+)"', m.group(1)) if m else None
style = ' s="%s"' % sm.group(1) if sm else ''

written = []

def fix(mo):
    head, body = mo.group(1), mo.group(2)
    rn = int(re.search(r'\br="(\d+)"', head).group(1))
    if rn == 2:
        # Excel re-saved the header as a shared string; swap the whole cell for
        # an inline one so the text can be set without touching sharedStrings.
        body = re.sub(r'<c r="J2"([^>]*?)(?: t="s")?(?:/>|>.*?</c>)',
                      lambda c: '<c r="J2"%s t="inlineStr"><is><t>%s</t></is></c>'
                                % (re.sub(r' t="[^"]*"', '', c.group(1)), esc(HEADER)),
                      body, count=1, flags=re.S)
    if rn in targets and not re.search(r'<c r="J%d[^0-9]' % rn, body):
        cell = '<c r="J%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (
            rn, style if rn == 2 else '', esc(targets[rn]))
        head = re.sub(r'spans="1:\d+"', 'spans="1:10"', head)
        body += cell
        written.append(rn)
    # the blocks are collapsed outline groups - unhide or column J reads empty
    if HQ_LO <= rn <= HQ_HI or SSC_LO <= rn <= SSC_HI:
        head = head.replace(' hidden="1"', '')
    if rn in (HQ_LO - 1, SSC_LO - 1):
        head = head.replace(' collapsed="1"', '')
    return '<row' + head + '>' + body + '</row>'

xml2 = re.sub(r'<row([^>]*)>(.*?)</row>', fix, xml, flags=re.S)

# widen J in place; never add a second <col> for the same column
if re.search(r'<col min="10" max="10"[^>]*/>', xml2):
    xml2 = re.sub(r'<col min="10" max="10"[^>]*/>',
                  '<col min="10" max="10" width="40" customWidth="1"/>', xml2, count=1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    zout.writestr(it, xml2.encode('utf-8') if it.filename == name else zin.read(it.filename))
zout.close()
print('rows written to column J:', len(written) - 1)
