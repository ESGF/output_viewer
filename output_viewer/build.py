from htmlbuilder import Document, BootstrapNavbar, Table, Link
import shutil
import json
import sys
from page import Page
from collections import OrderedDict
import datetime
import os
import stat
from utils import rechmod


def build_viewer(index_path="index.json", diag_name="Output Viewer", default_mask=None):
    try:
        with open(index_path) as index_file:
            spec = json.load(index_file)
    except Exception as e:
        raise e
        print "Unable to load index file at '%s'. Please make sure it's a valid JSON file." % index_path
        sys.exit()

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

    if "version" in spec:
        version = spec["version"]
    else:
        version = datetime.datetime.today().strftime("%Y-%m-%d")

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
    icons = []

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
        os.chmod(os.path.join(path, "index.html"), default_mask)

    static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")
    viewer_dir = os.path.join(path, "viewer")

    if os.path.exists(viewer_dir):
        shutil.rmtree(viewer_dir)

    shutil.copytree(static_dir, viewer_dir)

    if default_mask is not None:
        rechmod(viewer_dir, default_mask)
