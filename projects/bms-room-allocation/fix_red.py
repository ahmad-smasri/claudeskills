"""Re-read the rows flagged red on Ground Floor and write the corrections.

Two different mistakes were behind them:

1. The walker stepped off the end of a leader onto a wall it touched and
   followed the wall across the plan (VAV0026, VAV0028, VAV0029, FCU0016).
   trace.wall_suspect() now detects this - an endpoint reached along an
   unbroken run, where a real leader is always dashed.

2. The endpoint was right but I named the room from the nearest text. On HQ
   screens the room name sits outside its room on its own pointer, so the room
   has to be resolved from the polygon the endpoint falls in, and only then
   matched to whichever label points into that polygon (VAV0052, VAV0053).
"""
import re, zipfile, os
import openpyxl

SRC = '/root/.claude/uploads/7b732886-7f20-51be-97dc-21f5f8123adc/849d736f-Appendix_A_Asset_Register_SSC_HQ_BMS_rooms_1.xlsx'
OUT = '/home/user/claudeskills/projects/bms-room-allocation/Appendix_A_Asset_Register_SSC_HQ_BMS_rooms.xlsx'

# row -> corrected column J ('' clears the cell)
FIX = {
    186: 'G.103 BMS ROOM',          # leader really ends at (665,452) inside G.103;
                                    # its name "BMS Room" is printed to the right
    188: 'G.003',                   # leader ends at (546,617), above the G.003/G.002 wall
    189: 'G.002',                   # VAV0029 - real end (548,659), not the far side of the plan
    190: '',                        # VAV0030 ends in the corridor east of G.001-G.004; unnamed
    212: 'G.108 CONSULTANT SPACE',  # endpoint sits inside G.108, not at the Male Toilet text
    213: '',                        # VAV0053 also ends inside G.108 - left blank per review
}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

z = zipfile.ZipFile(SRC)
name = 'xl/worksheets/sheet6.xml'
xml = z.read(name).decode('utf-8')
touched = []

def fix(mo):
    head, body = mo.group(1), mo.group(2)
    rn = int(re.search(r'\br="(\d+)"', head).group(1))
    if rn in FIX:
        val = FIX[rn]
        old = re.search(r'<c r="J%d"([^>]*?)(?:/>|>.*?</c>)' % rn, body, re.S)
        # keep whatever style the cell already carries - that is where the
        # reviewer's fill lives, and dropping it would wipe their marking
        style = ''
        if old:
            sm = re.search(r's="(\d+)"', old.group(1))
            if sm:
                style = ' s="%s"' % sm.group(1)
        cell = ('<c r="J%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (rn, style, esc(val))
                if val else '<c r="J%d"%s/>' % (rn, style))
        if old:
            body = body[:old.start()] + cell + body[old.end():]
        else:
            body += cell
            head = re.sub(r'spans="1:\d+"', 'spans="1:10"', head)
        touched.append(rn)
    return '<row' + head + '>' + body + '</row>'

xml2 = re.sub(r'<row([^>]*)>(.*?)</row>', fix, xml, flags=re.S)
assert sorted(touched) == sorted(FIX), (touched, list(FIX))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    zout.writestr(it, xml2.encode('utf-8') if it.filename == name else zin.read(it.filename))
zout.close()
print('corrected rows:', sorted(touched))
