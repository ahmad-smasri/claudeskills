"""Fill A:K green on every QNL row where the screen and the register disagree.

The green is `FF00B050`, the one already used on the HQ and SSC rows in the
delivered workbook, and it is filled across the whole row rather than a single
cell because another pass reads the row colour.

The fill is written into the sheet XML rather than through openpyxl, for the
same reason `write_j.py` is: a round-trip drops the cell comments, the
web-extension task pane and the spilling FILTER formulas on the three
`Room Names with Equip.` sheets. Each cell keeps the style it had - a clone of
its own `cellXf` is added with the green fill on it, so fonts, borders and
number formats survive.
"""
import re
import shutil
import zipfile

import report_qnl

BOOK = ('/home/user/claudeskills/projects/qnl-bms-room-allocation/'
        'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
SHEET = 'xl/worksheets/sheet6.xml'
STYLES = 'xl/styles.xml'
GREEN = 'FF00B050'
COLS = 'ABCDEFGHIJK'
# a row is 'to check' when the screen puts the unit somewhere column D does
# not (DIFF), or when it was read with a caveat that names column D (CHECK).
MARK = {'DIFF', 'CHECK'}


def green_fill_id(styles):
    """index of the FF00B050 solid fill, appending one if it is not there"""
    block = re.search(r'<fills count="(\d+)">(.*?)</fills>', styles, re.S)
    fills = re.findall(r'<fill>.*?</fill>|<fill/>', block.group(2), re.S)
    for i, f in enumerate(fills):
        if 'solid' in f and GREEN in f:
            return i, styles
    new = ('<fill><patternFill patternType="solid"><fgColor rgb="%s"/>'
           '<bgColor indexed="64"/></patternFill></fill>' % GREEN)
    styles = styles.replace(block.group(0),
                            '<fills count="%d">%s%s</fills>'
                            % (len(fills) + 1, block.group(2), new))
    return len(fills), styles


def add_xfs(styles, wanted, fill_id):
    """clone each style in `wanted` with the green fill; returns old -> new"""
    block = re.search(r'<cellXfs count="(\d+)">(.*?)</cellXfs>', styles, re.S)
    xfs = re.findall(r'<xf\b[^>]*/>|<xf\b[^>]*>.*?</xf>', block.group(2), re.S)
    added, mapping = [], {}
    for old in sorted(wanted):
        src = xfs[old] if old < len(xfs) else '<xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
        new = re.sub(r'\bfillId="\d+"', 'fillId="%d"' % fill_id, src)
        if 'fillId=' not in new:
            new = new.replace('<xf ', '<xf fillId="%d" ' % fill_id, 1)
        new = re.sub(r'\bapplyFill="[01]"', '', new)
        new = new.replace('<xf ', '<xf applyFill="1" ', 1)
        mapping[old] = len(xfs) + len(added)
        added.append(new)
    styles = styles.replace(
        block.group(0),
        '<cellXfs count="%d">%s%s</cellXfs>'
        % (len(xfs) + len(added), block.group(2), ''.join(added)))
    return styles, mapping


def main():
    zin = zipfile.ZipFile(BOOK)
    sheet = zin.read(SHEET).decode('utf-8')
    styles = zin.read(STYLES).decode('utf-8')

    rows = {r[0] for r in report_qnl.findings() if r[5] in MARK}
    if not rows:
        print('nothing to mark')
        return

    # pass one: what style does each target cell carry today
    cell_re = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(/>|>.*?</c>)', re.S)
    wanted = set()
    for mo in re.finditer(r'<row([^>]*)>(.*?)</row>', sheet, re.S):
        rn = int(re.search(r'\br="(\d+)"', mo.group(1)).group(1))
        if rn not in rows:
            continue
        seen = set()
        for c in cell_re.finditer(mo.group(2)):
            if c.group(1) in COLS:
                s = re.search(r'\bs="(\d+)"', c.group(3))
                wanted.add(int(s.group(1)) if s else 0)
                seen.add(c.group(1))
        if seen != set(COLS):
            wanted.add(0)              # empty cells have to be created at s=0

    fill_id, styles = green_fill_id(styles)
    styles, mapping = add_xfs(styles, wanted, fill_id)

    marked = []

    def paint(mo):
        head, body = mo.group(1), mo.group(2)
        rn = int(re.search(r'\br="(\d+)"', head).group(1))
        if rn not in rows:
            return mo.group(0)
        keep = {}
        for c in cell_re.finditer(body):
            col, txt = c.group(1), c.group(0)
            if col in COLS:
                s = re.search(r'\bs="(\d+)"', c.group(3))
                new = mapping[int(s.group(1)) if s else 0]
                txt = (re.sub(r'\bs="\d+"', 's="%d"' % new, txt) if s
                       else txt.replace('<c ', '<c s="%d" ' % new, 1))
            keep[col] = txt
        for col in COLS:                # a blank cell still has to carry colour
            keep.setdefault(col, '<c r="%s%d" s="%d"/>' % (col, rn, mapping[0]))
        order = sorted(keep, key=lambda c: (len(c), c))
        head = re.sub(r'spans="1:\d+"', 'spans="1:11"', head)
        marked.append(rn)
        return '<row' + head + '>' + ''.join(keep[c] for c in order) + '</row>'

    sheet = re.sub(r'<row([^>]*)>(.*?)</row>', paint, sheet, flags=re.S)

    tmp = BOOK + '.tmp'
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = {SHEET: sheet, STYLES: styles}.get(it.filename)
        zout.writestr(it, data.encode('utf-8') if data else zin.read(it.filename))
    zout.close()
    shutil.move(tmp, BOOK)
    print('%d rows filled %s across A:K' % (len(marked), GREEN))


if __name__ == '__main__':
    main()
