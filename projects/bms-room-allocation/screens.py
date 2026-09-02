"""Map a screen label used in the allocation lists to the image file it came
from, so column K can point the reviewer straight at the picture."""

HQ_FOLDER = {
    'BF': 'Basment Floor', 'GF': 'Ground Floor', 'FF': '1F', 'SF': '2F',
    '3F': '3F', '4F': '4F', '5F': '5F', '6F': '6F', '7F': '7F',
    '8F': '8F', '9F': '9F', '10F': '10F', '11F': '11F', 'RF': 'RF',
    'CPF': 'Cark Park',
}
SSC_SCREENS = {'BF-part1', 'BF-part2', 'FF-part1', 'FF-part2',
               'Second Floor', 'TF-part1', 'TF-part2'}


def image(label):
    """'3F-1' -> 'HQ/3F/3F-1.jpg'; 'TF-part1' -> 'SSC/TF-part1.jpg'."""
    if not label:
        return ''
    if label in SSC_SCREENS:
        return 'SSC/%s.jpg' % label
    if '/' in label:                       # already 'Basment Floor/BF-1'
        folder, name = label.rsplit('/', 1)
        return 'HQ/%s/%s.jpg' % (folder, name)
    stem = label.split('-')[0]
    folder = HQ_FOLDER.get(stem)
    return 'HQ/%s/%s.jpg' % (folder, label) if folder else label
