import os
from PIL import Image

from images_manager import creer_couverture_reliure


def test_creer_couverture_reliure_cree_une_image_brown_120x180():
    path = creer_couverture_reliure('test_reliure')

    assert path
    assert os.path.exists(path)
    with Image.open(path) as img:
        assert img.size == (120, 180)
        assert img.mode in {"RGB", "RGBA"}

    os.remove(path)
