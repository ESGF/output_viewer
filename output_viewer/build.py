from .htmlbuilder import Document, BootstrapNavbar, Table, Link
import shutil
import json
import sys
from .page import Page
from collections import OrderedDict
import datetime
import os
import stat
from .utils import rechmod


def open_specs(index_path):
    """
    Open return the specs json at index_path.
    """
    try:
        with open(index_path) as index_file:
            return json.load(index_file)
    except:
        print(("Unable to load index file at '%s'. Please make sure it's a valid JSON file." % index_path))
        sys.exit()

def copy_and_edit_path(path, default_mask):
    """
    At the given path, copy it and modify it
    so its contents can be viewed correctly.
    """
    static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")
    viewer_dir = os.path.join(path, "viewer")

    if os.path.exists(viewer_dir):
        shutil.rmtree(viewer_dir)

    shutil.copytree(static_dir, viewer_dir)

    if default_mask is not None:
        rechmod(viewer_dir, default_mask)

def build_page(output_page, index_path="index.json", default_mask=None):
    """
    Given an OutputPage object, generate and return the
    location of the HTML page.
    """
    spec = open_specs(index_path)
    spec = spec["specification"]

    path = os.path.dirname(index_path)

    page_path = None
    for plotspec in spec:
        if plotspec['short_name'] == output_page.short_name:
            page = Page(plotspec, root_path=path, permissions=default_mask)
            page.build(page.short_name)
            page_path = os.path.join(page.short_name, "index.html")

    if not page_path:
        msg = "The current page's name isn't in the specs json."
        raise RuntimeError(msg)

    copy_and_edit_path(path, default_mask)

    return page_path

def build_viewer(index_path="index.json", diag_name="Output Viewer", default_mask=None):
    """
    Build the viewer based on the index_path.
    """
    spec = open_specs(index_path)

    if "title" in spec:
        diag_name = spec["title"]
    menu = OrderedDict()

    if "menu" in spec:
        for m in spec["menu"]:
            if "url" not in m:
                menu[m["title"]] = OrderedDict()
                for menu_item in m["items"]:
                    menu[m["title"]][menu_item["title"]] = menu_item["url"]
            else:
                menu[m["title"]] = m["url"]

    spec = spec["specification"]

    path = os.path.dirname(index_path)

    pages = []
    for ind, plotspec in enumerate(spec):
        page = Page(plotspec, root_path=path, permissions=default_mask)
        page_name = page.short_name if page.short_name else "set_%d" % (ind + 1)
        pages.append((page, page_name))

    doc = Document(diag_name)

    toolbar = BootstrapNavbar(diag_name, "index.html", menu)

    doc.append(toolbar)
    container = doc.append_tag("div", class_="container")
    row = container.append_tag("div", class_="row")
    col = row.append_tag("div", class_="col-sm-5 col-sm-offset-1")
    table = Table(class_="table")
    col.append(table)
    col = row.append_tag('div', class_="col-sm-5")
    grid = col.append_tag('div', class_="img_links")
    table.append_header().append_cell("Output Sets")

    for page, page_name in pages:
        page.build(page_name, toolbar)
        page_path = os.path.join(page_name, "index.html")
        l = Link(href=page_path)
        l.append(page.name)
        if page.icon:
            cell = grid.append_tag("div", class_="img_cell")
            cell.append_tag("a", href=page_path).append_tag('img', src=page.icon)
        table.append_row().append_cell(l)

    with open(os.path.join(path, "index.html"), "w") as f:
        toolbar.setLevel(0)
        f.write(doc.build())
        if default_mask is not None:
            os.chmod(os.path.join(path, "index.html"), default_mask)

    copy_and_edit_path(path, default_mask)
