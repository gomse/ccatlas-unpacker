import os, sys
from xml.etree import ElementTree
from PIL import Image

# Dictionary from XML Elements
def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            tag = tree[index + 1].tag
            if tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tag == 'true':
                d[item.text] = True
            elif tag == 'false':
                d[item.text] = False
            elif tag == 'dict':
                d[item.text] = tree_to_dict(tree[index + 1])
    return d

#parse_rect = lambda s: s.replace('{','').replace('}','').split(',')
def parse_rect(s):
    rect = s.replace('{','').replace('}','').split(',')
    for i in range(len(rect)):
        rect[i] = int(rect[i])
    return rect

# Parse plist
def save_png_from_plist(plist_filename, atlas_filename):
    print(plist_filename + ':')

    outpath = plist_filename.replace('.plist', '')

    root = ElementTree.fromstring(open(plist_filename, 'r').read())
    atlas_image = Image.open(atlas_filename)

    plist_dict = tree_to_dict(root[0])

    for k, v in plist_dict['frames'].items():
        frame_rect = parse_rect(v['textureRect'])
        frame_size = parse_rect(v['spriteSourceSize'])
        offset = parse_rect(v['spriteOffset'])
        rotated = v['textureRotated']

        width = frame_rect[3] if rotated else frame_rect[2]
        height = frame_rect[2] if rotated else frame_rect[3]

        box = (
            frame_rect[0],
            frame_rect[1],
            frame_rect[0] + width,
            frame_rect[1] + height
            )

        frame = atlas_image.crop(box)

        '''
        # offset correction
        result_image = Image.new('RGBA', frame_size, (0,0,0,0))
        if rotated:
            result_box = (
                int((frame_size[0] - width) / 2) + offset[0],
                int((frame_size[1] - height) / 2) + offset[1],
                int((frame_size[0] + width) / 2),
                int((frame_size[1] + height) / 2)
                )
        else:
            result_box = (
                int((frame_size[0] - height) / 2) + offset[0],
                int((frame_size[1] - width) / 2) + offset[1],
                int((frame_size[0] + height) / 2),
                int((frame_size[1] + width) / 2)
                )
        result_image.paste(frame, result_box, mask=0)
        '''

        result_image = frame.rotate(90) if rotated else frame

        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        outfile = (outpath + '/' + k)
        result_image.save(outfile)

        print('> "' + outfile + '" generated.')

# Entrypoint
if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        plist_filename = filename + '.plist'
        atlas_filename = filename + '.png'
        if (os.path.exists(plist_filename) and os.path.exists(atlas_filename)):
            save_png_from_plist(plist_filename, atlas_filename)
        else:
            print("Make sure you have boith plist and png files in the same directory.")
    else:
        for filename in os.listdir('.'):
            if filename.endswith('.plist'):
                plist_filename = filename
                atlas_filename = filename.replace('.plist', '.png')
                if (os.path.exists(plist_filename) and os.path.exists(atlas_filename)):
                    save_png_from_plist(plist_filename, atlas_filename)
                else:
                    print(plist_filename + ': passed.')
