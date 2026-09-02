"""Write the room read off each QNL BMS screen into columns J and K.

J is `ROOM PER BMS SCREEN` and K is `BMS SCREEN (IMAGE FILE)`, the same two
columns the HQ and SSC pass filled. Column D is never touched: the point of the
exercise is to have the two side by side.

The sheet XML is edited inside the workbook zip rather than round-tripped
through openpyxl, so the cell comments, the web-extension task pane and the
spilling FILTER formulas on the three `Room Names with Equip.` sheets survive.
"""
import os
import re
import shutil
import sys
import zipfile

import alloc

SRC = ('/root/.claude/uploads/7abe1193-772a-5e87-a7e1-f943639e6ba5/'
       'd37d3a55-Appendix_A_Asset_Register_SSC_HQ_BMS_rooms_4.xlsx')
OUT = ('/home/user/claudeskills/projects/qnl-bms-room-allocation/'
       'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
SHEET = 'xl/worksheets/sheet6.xml'
QNL_LO, QNL_HI = 766, 1316

SCREEN_FILE = alloc.SCREEN_FILE

ALLOC = [(tag, room, screen, note)
         for screen, rows in alloc.SCREENS.items()
         for tag, room, note in rows]


def reg_tag(bms, rows):
    """screen tag -> register tag.

    `VAV-B-S11-011` is `VAV_B_S11_011`, but the screens drop the level segment
    on some families - `CAV-S12-003` is `CAV_B_S12_003` and `CAV-S11-002` on a
    first-floor screen is `CAV_1F_S11_002` - so the level is put back when the
    plain form is not there. Which level is decided by what the register
    actually holds, not by the screen the tag came off, because the same
    family number is reused on more than one level.
    """
    t = bms.strip().upper().replace('-', '_')
    if t in rows:
        return t
    m = re.match(r'^(CAV|VAV|FCU)_(S\d+_.*)$', t)
    if m:
        for level in ('B', '1F', '2F'):
            alt = '%s_%s_%s' % (m.group(1), level, m.group(2))
            if alt in rows:
                return alt
    return t


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def shared_strings(z):
    """the workbook's string table - column A is stored in it, not inline"""
    try:
        xml = z.read('xl/sharedStrings.xml').decode('utf-8')
    except KeyError:
        return []
    out = []
    for si in re.finditer(r'<si>(.*?)</si>', xml, re.S):
        out.append(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si.group(1), re.S)))
    return out


def cells(xml, strings):
    """row number -> the tag in column A, for the QNL block"""
    out = {}
    for mo in re.finditer(r'<row([^>]*)>(.*?)</row>', xml, re.S):
        rn = int(re.search(r'\br="(\d+)"', mo.group(1)).group(1))
        if not (QNL_LO <= rn <= QNL_HI):
            continue
        c = re.search(r'<c r="A%d"([^>]*)>(.*?)</c>' % rn, mo.group(2), re.S)
        if not c:
            continue
        body = c.group(2)
        if 't="s"' in c.group(1):
            v = re.search(r'<v>(\d+)</v>', body)
            if v and int(v.group(1)) < len(strings):
                out[rn] = strings[int(v.group(1))].strip()
        else:
            t = re.search(r'<t[^>]*>(.*?)</t>', body, re.S)
            if t:
                out[rn] = t.group(1).strip()
    return out


def main():
    zin = zipfile.ZipFile(SRC)
    xml = zin.read(SHEET).decode('utf-8')
    rows = {v.upper(): k for k, v in cells(xml, shared_strings(zin)).items()}

    targets, missing = {}, []
    for bms, room, screen, _note in ALLOC:
        t = reg_tag(bms, rows)
        if t in rows:
            targets[rows[t]] = (room, SCREEN_FILE[screen])
        else:
            missing.append((bms, t))

    style = ''
    m = re.search(r'<c r="J3"([^>]*)>', xml)
    if m:
        sm = re.search(r's="(\d+)"', m.group(1))
        style = ' s="%s"' % sm.group(1) if sm else ''

    written = []
    cell_re = re.compile(r'<c r="([A-Z]+)(\d+)"(?:[^>]*/>|[^>]*>.*?</c>)', re.S)

    def col_no(letters):
        n = 0
        for ch in letters:
            n = n * 26 + ord(ch) - 64
        return n

    def fix(mo):
        head, body = mo.group(1), mo.group(2)
        rn = int(re.search(r'\br="(\d+)"', head).group(1))
        if rn not in targets:
            return mo.group(0)
        # An empty, style-only J or K cell is already there on some rows, so the
        # new value has to replace it rather than be appended after it - a row
        # whose cells are out of column order is a repair prompt in Excel.
        keep = [(col_no(m.group(1)), m.group(0)) for m in cell_re.finditer(body)
                if m.group(1) not in ('J', 'K')]
        for col, val in zip('JK', targets[rn]):
            keep.append((col_no(col),
                         '<c r="%s%d"%s t="inlineStr"><is><t>%s</t></is></c>'
                         % (col, rn, style, esc(val))))
        keep.sort(key=lambda t: t[0])
        head = re.sub(r'spans="1:\d+"', 'spans="1:11"', head)
        written.append(rn)
        return '<row' + head + '>' + ''.join(c for _, c in keep) + '</row>'

    xml = re.sub(r'<row([^>]*)>(.*?)</row>', fix, xml, flags=re.S)

    tmp = OUT + '.tmp'
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = xml.encode('utf-8') if it.filename == SHEET else zin.read(it.filename)
        zout.writestr(it, data)
    zout.close()
    shutil.move(tmp, OUT)

    print('columns J and K written on %d QNL rows' % len(written))
    if missing:
        print('no register row for:', missing)


if __name__ == '__main__':
    main()
