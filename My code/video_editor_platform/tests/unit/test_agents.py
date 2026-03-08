"""Unit tests for new agent modules."""

import sys, os
import pytest
from pathlib import Path

# ensure src in path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.services.description_agent import DescriptionAgent
from src.services.creative_agent import CreativeAgent
from src.services.edit_agent import EditAgent
from PIL import Image


def test_description_keywords_and_sentiment():
    desc = "Big SALE today with amazing discounts"
    kw = DescriptionAgent.extract_keywords(desc)
    assert 'sale' in kw
    assert 'discounts' in kw
    assert DescriptionAgent.sentiment(desc) == 'positive'


def test_creative_agent_generates_decorations():
    kw = ['sale', 'discounts']
    decs = CreativeAgent.generate_decorations(kw, 'positive')
    assert any(d['type'] == 'emoji' for d in decs)
    assert any(d['type'] == 'text' for d in decs)


def test_discount_keywords_trigger_sale():
    # numeric and 'off' keywords should produce sale decorations
    kw = ['helmets', '20', 'off']
    decs = CreativeAgent.generate_decorations(kw, 'neutral')
    texts = [d['value'] for d in decs if d['type'] == 'text']
    assert any('SALE' in t for t in texts)
    assert any('OFF' in t for t in texts)


def test_description_sentiment_and_keywords():
    # sentiment should be positive if percentage present
    from services.description_agent import DescriptionAgent
    sent = DescriptionAgent.sentiment('Helmets at 20% off')
    assert sent == 'positive'
    kw = DescriptionAgent.extract_keywords('Helmets at 20% off')
    assert '20' in kw and 'off' in kw


def test_edit_agent_draws_on_image(tmp_path):
    img = Image.new('RGB', (100, 50), (0, 0, 0))
    decs = [{'type': 'text', 'value': 'TEST', 'font_size': 20},
            {'type': 'emoji', 'value': '🎉'}]
    out = EditAgent.apply_decorations(img, decs)
    out_path = tmp_path / 'out.png'
    out.save(out_path)
    assert out_path.exists()
    # size should remain same
    assert out.size == (100, 50)


def test_edit_agent_color_enhances(tmp_path):
    # make a dull gray image and apply decorations (even empty list) to trigger enhancement
    img = Image.new('RGB', (50, 50), (128, 128, 128))
    out = EditAgent.apply_decorations(img, [])
    # ensure returned image is same size
    assert out.size == img.size
    # pick a pixel and verify it is not identical (color enhancer should change values)
    in_pixel = img.getpixel((10, 10))
    out_pixel = out.getpixel((10, 10))
    assert in_pixel != out_pixel


def test_slideshow_is_image_agnostic(tmp_path):
    # ensure that _generate_slideshow decorations depend only on description
    from api.routes import _save_files, _generate_slideshow
    from PIL import Image

    # create two different images
    img1 = tmp_path / 'a.png'
    img2 = tmp_path / 'b.png'
    Image.new('RGB', (120, 80), (255, 0, 0)).save(img1)
    Image.new('RGB', (80, 120), (0, 255, 0)).save(img2)

    class DummyUpload:
        def __init__(self, path):
            self.filename = path.name
            self.file = open(path, 'rb')

    files1 = [DummyUpload(img1)]
    files2 = [DummyUpload(img2)]

    saved1 = _save_files(files1)
    saved2 = _save_files(files2)

    url1 = _generate_slideshow(saved1, description="Helmets at 20% off")
    url2 = _generate_slideshow(saved2, description="Helmets at 20% off")

    # both should produce some video URL (gif/mp4) and not depend on image content
    assert url1 is not None
    assert url2 is not None
    assert url1.endswith(tuple(['.gif', '.mp4']))
    assert url2.endswith(tuple(['.gif', '.mp4']))

    # open the generated gif and check its dimensions approximate 9:16
    from PIL import Image
    dest = Path(__import__('config.base').base.Settings().UPLOAD_TEMP_DIR)
    gif = next(dest.glob('*slideshow.*'))
    with Image.open(gif) as im:
        w, h = im.size
        assert abs((w / h) - (9/16)) < 0.1, f"aspect {w}x{h} not 9:16"
        # sample bottom center pixel to ensure banner overlay changed color
        px = im.getpixel((w // 2, int(h * 0.95)))
        # pixel should not be same as default template color (assume not pure black)
        assert px != (0, 0, 0)


def test_generate_slideshow_with_description(tmp_path, monkeypatch):
    # verify helper can create a slideshow file when given real images and a description
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    from api.routes import _save_files, _generate_slideshow

    # create fake template directory and one template image
    tpl_dir = tmp_path / 'templates'
    tpl_dir.mkdir()
    tpl_img = tpl_dir / 'tpl.png'
    Image.new('RGB', (400, 300), (200, 100, 50)).save(tpl_img)
    # set environment so Settings picks it up
    monkeypatch.setenv('TEMPLATES_DIR', str(tpl_dir))

    # create two sample images
    img1 = tmp_path / 'a.png'
    img2 = tmp_path / 'b.png'
    Image.new('RGB', (200, 100), (10, 20, 30)).save(img1)
    Image.new('RGB', (150, 120), (50, 60, 70)).save(img2)

    # create UploadFile-like objects by reading
    class DummyUpload:
        def __init__(self, path):
            self.filename = path.name
            self.file = open(path, 'rb')
    files_list = [DummyUpload(img1), DummyUpload(img2)]

    saved = _save_files(files_list)
    # call generator
    url = _generate_slideshow(saved, description="Big sale today")
    assert url is not None
    # ensure file exists in upload directory
    upload_dir = Path(__import__('config.base').base.Settings().UPLOAD_TEMP_DIR)
    assert any(upload_dir.glob('*slideshow.*'))

    # no errors thrown and decorations should have been applied; size of output directory
    assert upload_dir.stat().st_size > 0

