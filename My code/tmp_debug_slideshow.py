import sys, os
from pathlib import Path
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
url = _generate_slideshow(saved, description='Big sale today')
print('url ->', url)
print('folder contents', [p.name for p in upload_dir.iterdir()])
