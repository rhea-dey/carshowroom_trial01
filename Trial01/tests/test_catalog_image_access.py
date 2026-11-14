from io import BytesIO

from PIL import Image

from app.frontend import catalog


def _catalog_page(monkeypatch):
    page = catalog.CatalogPage.__new__(catalog.CatalogPage)
    page.image_references = []
    page.winfo_toplevel = lambda: None
    monkeypatch.setattr(catalog.ImageTk, "PhotoImage", lambda image, master: image)
    return page


def test_catalog_loads_images_from_bytes(monkeypatch):
    image = Image.new("RGB", (4, 4), "red")
    image_data = BytesIO()
    image.save(image_data, format="PNG")

    photo = _catalog_page(monkeypatch)._load_image(
        {"images": [image_data.getvalue()]},
    )

    assert photo is not None
    assert photo.size == (4, 4)


def test_catalog_does_not_open_image_paths(monkeypatch):
    image_opened = False

    def fail_if_opened(*_args, **_kwargs):
        nonlocal image_opened
        image_opened = True
        raise AssertionError("Catalog must not open image paths")

    monkeypatch.setattr(catalog.Image, "open", fail_if_opened)
    photo = _catalog_page(monkeypatch)._load_image(
        {"images": ["images/panther-gls-130.png"]},
    )

    assert photo is None
    assert not image_opened
