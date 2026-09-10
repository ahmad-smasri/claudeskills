"""Write the verdict and its reason into columns L and M of the register.

Until now the reading went into column J and the screen it came off into K,
and *why* a row was flagged lived only in `QNL_BMS_screen_findings.csv`. A
reviewer with the workbook open saw `Processing Rm` with no way to tell that
column D says SECURITY & BMS B.102, or that a plant item's column D is where
the unit sits rather than what it serves. The reason belongs beside the
reading.

Run after `write_j.py`, before `highlight_rows.py`.
"""
import re
import shutil
import zipfile

import report_qnl

BOOK = ('/home/user/claudeskills/projects/qnl-bms-room-allocation/'
        'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
SHEET = 'xl/worksheets/sheet6.xml'
HEAD = {'L': 'BMS SCREEN vs DRAWINGS', 'M': 'WHY'}
VERDICT = {
    'SAME': 'SAME - screen and column D name the same room',
    'OPEN': 'OPEN - one space, two or more labels; the screen cannot split them',
    'CHECK': 'CHECK - read, but with a caveat; see the reason',
    'DIFF': 'DIFF - the screen puts this unit somewhere column D does not',
}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    rows = {r[0]: (VERDICT.get(r[5], r[5]), r[6] or '')
            for r in report_qnl.findings() if r[5]}
    zin = zipfile.ZipFile(BOOK)
    xml = zin.read(SHEET).decode('utf-8')

    m = re.search(r'<c r="J2"([^>]*)>', xml)
    sm = re.search(r's="(\d+)"', m.group(1)) if m else None
    head_style = ' s="%s"' % sm.group(1) if sm else ''

    cell_re = re.compile(r'<c r="([A-Z]+)(\d+)"(?:[^>]*/>|[^>]*>.*?</c>)', re.S)

    def col_no(letters):
        n = 0
        for ch in letters:
            n = n * 26 + ord(ch) - 64
        return n

    written = []

    def fix(mo):
        head, body = mo.group(1), mo.group(2)
        rn = int(re.search(r'\br="(\d+)"', head).group(1))
        if rn == 2:
            vals = {c: HEAD[c] for c in 'LM'}
            style = head_style
        elif rn in rows:
            vals = dict(zip('LM', rows[rn]))
            style = ''
        else:
            return mo.group(0)
        keep = [(col_no(c.group(1)), c.group(0)) for c in cell_re.finditer(body)
                if c.group(1) not in vals]
        for col, val in vals.items():
            if not val:
                continue
            keep.append((col_no(col),
                         '<c r="%s%d"%s t="inlineStr"><is><t>%s</t></is></c>'
                         % (col, rn, style, esc(val))))
        keep.sort(key=lambda t: t[0])
        head = re.sub(r'spans="1:\d+"', 'spans="1:13"', head)
        written.append(rn)
        return '<row' + head + '>' + ''.join(c for _, c in keep) + '</row>'

    xml = re.sub(r'<row([^>]*)>(.*?)</row>', fix, xml, flags=re.S)

    # give the two new columns room to be read
    for col, width in (('12', 46), ('13', 90)):
        add = '<col min="%s" max="%s" width="%d" customWidth="1"/>' % (col, col, width)
        if re.search(r'<col min="%s" max="%s"[^>]*/>' % (col, col), xml):
            xml = re.sub(r'<col min="%s" max="%s"[^>]*/>' % (col, col), add, xml, 1)
        elif '<cols>' in xml:
            xml = xml.replace('<cols>', '<cols>' + add, 1)
        else:
            xml = re.sub(r'(<sheetData>)', '<cols>' + add + '</cols>\\1', xml, 1)

    tmp = BOOK + '.tmp'
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = xml.encode('utf-8') if it.filename == SHEET else zin.read(it.filename)
        zout.writestr(it, data)
    zout.close()
    shutil.move(tmp, BOOK)
    print('verdict and reason written on %d rows' % (len(written) - 1))


if __name__ == '__main__':
    main()
