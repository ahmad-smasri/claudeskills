import re, xlrd, openpyxl
from collections import defaultdict

UP = '/root/.claude/uploads/7b732886-7f20-51be-97dc-21f5f8123adc/'
VAVF = UP + '56bf445f-HQ__SSC_VAV_LIST_2058.xls'
FCUF = UP + '9fe6993c-HQ__SSC_FCU_LIST_1397.xls'
REGF = UP + '6e868a0a-Copy_of_Appendix_A__Asset_Register_For_Ahmad_Only_1.xlsx'

SECTIONS = [('HQ', 4, 777), ('QNL', 779, 1329), ('SSC', 1331, 1454), ('RDC', 1456, 3215)]

def section_of(i):
    for n, lo, hi in SECTIONS:
        if lo <= i <= hi:
            return n
    return None

def norm_tag(t):
    """0050-FCU-0001 / 0051-VAV-0003 / FCU0001 -> ('FCU', 1)"""
    t = str(t).strip().upper().replace(' ', '')
    m = re.search(r'(VAV|FCU|AHU)[-_]?(\d+)$', t)
    if not m:
        return None
    return (m.group(1), int(m.group(2)))

def split_D(d):
    """'STAFF LOBBY B.103' -> ('STAFF LOBBY', 'B.103'); returns (name, num|None)"""
    d = ' '.join(str(d).split())
    m = re.match(r'^(.*?)[\s]+([A-Za-z]{0,3}\d*\.\d+[A-Za-z0-9\-]*)$', d)
    if m and m.group(1):
        return m.group(1).strip(), m.group(2).strip()
    return d, None

def norm_num(n):
    """canonical room number key: 'B1.103'/'B.103' -> ('B','103'); 'L01.029'/'01.029'/'1.029' -> ('1','029')"""
    if not n:
        return None
    n = str(n).strip().upper().replace(' ', '')
    if '.' not in n:
        return None
    lvl, rest = n.split('.', 1)
    lvl = lvl.lstrip('L') or 'L'
    if lvl.startswith('B'):
        lvl = 'B'
    elif lvl.isdigit():
        lvl = str(int(lvl))
    rest = rest.strip()
    rm = re.match(r'^0*(\d+)(.*)$', rest)
    if rm:
        rest = rm.group(1) + rm.group(2).strip()
    return (lvl, rest)

ABBR = [
    (r'\bRM\b', 'ROOM'), (r'\bRMS\b', 'ROOMS'), (r'&', ' AND '),
    (r'\bOFF\b', 'OFFICE'), (r'\bCORIDOR\b', 'CORRIDOR'),
    (r'\bMANA\b', 'MANAGER'), (r'\bMGR\b', 'MANAGER'),
    (r'\bSEC\b', 'SECURITY'), (r'\bMECH\b', 'MECHANICAL'),
    (r'\bELEC\b', 'ELECTRICAL'), (r'\bSTOR\b', 'STORAGE'),
    (r'\bTLT\b', 'TOILET'), (r'\bWC\b', 'TOILET'),
]

def norm_name(s):
    s = str(s or '').upper()
    s = re.sub(r'[^A-Z0-9&]+', ' ', s)
    for pat, rep in ABBR:
        s = re.sub(pat, rep, s)
    s = re.sub(r'[^A-Z0-9]+', ' ', s)
    return ' '.join(s.split())

# ---------- sources ----------
def read_xls(path, sheet, building=None):
    b = xlrd.open_workbook(path)
    s = b.sheet_by_name(sheet)
    out = []
    for r in range(1, s.nrows):
        vals = [str(s.cell_value(r, c)).strip() for c in range(s.ncols)]
        if not any(vals):
            continue
        out.append({'sheet': sheet, 'row': r + 1, 'building': (building or vals[0]).strip(),
                    'floor': vals[1], 'ref': vals[2], 'tag': vals[3],
                    'room_no': vals[4], 'room_name': vals[5]})
    return out

def sources():
    src = []
    src += read_xls(VAVF, 'HQ & SSC VAV LIST')
    src += read_xls(FCUF, 'HQ FCU LIST', 'HQ')
    src += read_xls(FCUF, 'SSC FCU LIST', 'SSC')
    return src

def registry():
    wb = openpyxl.load_workbook(REGF, data_only=True)
    ws = wb['Controllable Asset Registry']
    recs = []
    for i in range(1, ws.max_row + 1):
        sec = section_of(i)
        if not sec:
            continue
        a = ws.cell(i, 1).value
        if a is None or str(a).strip() == '':
            continue
        recs.append({'row': i, 'sec': sec, 'tag': str(a).strip(),
                     'type': str(ws.cell(i, 2).value or '').strip(),
                     'incl': ws.cell(i, 3).value,
                     'D': ws.cell(i, 4).value, 'E': ws.cell(i, 5).value,
                     'F': ws.cell(i, 6).value, 'H': ws.cell(i, 8).value})
    return recs
