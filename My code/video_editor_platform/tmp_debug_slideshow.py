import sys, os
from pathlib import Path
# add project src to path
sys.path.insert(0, os.getcwd() + '/src')
from api.routes import _save_files, _generate_slideshow
from PIL import Image
import shutil

upload_dir = Path(__import__('config.base').base.Settings().UPLOAD_TEMP_DIR)
shutil.rmtree(upload_dir, ignore_errors=True)
upload_dir.mkdir(parents=True, exist_ok=True)

# create sample images
img1 = Path('temp_images/a.png'); img2 = Path('temp_images/b.png')
shutil.rmtree('temp_images', ignore_errors=True); os.makedirs('temp_images')
Image.new('RGB',(200,100),(10,20,30)).save(img1)
Image.new('RGB',(150,120),(50,60,70)).save(img2)

class DummyUpload:
    def __init__(self,p):
        self.filename = p.name
        self.file = open(p,'rb')

files_list = [DummyUpload(img1), DummyUpload(img2)]
saved = _save_files(files_list)
print('saved', saved)

# replicate part of _generate_slideshow to inspect frames
from services.description_agent import DescriptionAgent
from services.creative_agent import CreativeAgent
from services.edit_agent import EditAgent

decorations = []
desc_text = 'Big sale today'
kw = DescriptionAgent.extract_keywords(desc_text)
sent = DescriptionAgent.sentiment(desc_text)
decorations = CreativeAgent.generate_decorations(kw, sent)
print('decorations:', decorations)

# prepare images manually
image_paths = [f['path'] for f in saved if f['path'].lower().endswith(('jpg','jpeg','png','gif'))]
print('image_paths', image_paths)

from pathlib import Path
import shutil

# reuse internal _prepare_images definition
from PIL import Image
import imageio

def _prepare_images(paths, max_width=640):
    imgs = []
    for p in paths:
        try:
            im = Image.open(p).convert('RGB')
            if im.width > max_width:
                ratio = max_width / im.width
                im = im.resize((max_width, int(im.height * ratio)), Image.LANCZOS)
            if decorations:
                im = EditAgent.apply_decorations(im, decorations)
            imgs.append(imageio.core.util.Array(im))
        except Exception as e:
            print('prepare error', e)
            continue
    return imgs

frames = _prepare_images(image_paths)
print('frames count', len(frames))
for i,fr in enumerate(frames):
    print(i, type(fr), getattr(fr,'shape',None))

# run original generator
url = _generate_slideshow(saved, description=desc_text)
print('url ->', url)
print('folder contents', [p.name for p in upload_dir.iterdir()])
