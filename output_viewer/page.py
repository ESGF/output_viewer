from .htmlbuilder import Document, Table, TableCell, Link, Span, HTMLBuilder
import os
from .examine import is_img, is_data
from .utils import slugify, nuke_and_pave, rechmod


file_extensions = {
    ".nc": "NetCDF File",
    ".pdf": "PDF",
    ".svg": "Vector Image",
    ".png": "Bitmap Image"
}


class Column(object):
    def __init__(self, row, spec):
        self.row = row
        self.path = spec.get("path", None)
        self.title = spec.get("title", None)
        if self.title is None:
            self.title = os.path.basename(os.path.splitext(self.path)[0])
        self.meta = spec.get("meta", {})
        self.files = spec.get("files", [])

    def build(self, toolbar):
        doc = Document(title=self.title, level=3)
        if toolbar is not None:
            doc.append(toolbar)

        for col_ind, col in self.row.cols.iteritems():
            if col == self:
                break

        container = doc.append_tag("div", class_="container")
        row = container.append_tag("div", class_="row")

        if col_ind > min(self.row.cols.keys()):
            back = doc.append_tag("form", action=self.row.cols[col_ind - 1].getFileName(), class_="col_link back")
            link_back = back.append_tag("button", type="submit", data={"arrow": "left"})
            link_back.append("<")

        if col_ind < max(self.row.cols.keys()):
            n = doc.append_tag("form", action=self.row.cols[col_ind + 1].getFileName(), class_="col_link next")
            link_next = n.append_tag("button", type="submit", data={"arrow": "right"})
            link_next.append(">")

        title = row.append_tag("h1", class_="img_title")
        title.append(self.title)

        row = container.append_tag('div', class_="row")
        col = row.append_tag("div", class_="col-sm-12")

        file_div = col.append_tag("div", class_="img_display")
        file_url = os.path.join("..", "..", "..", self.path)
        if is_img(self.path):
            file_div.append_tag("img", src=file_url)

        all_files = [{"title": "File Shown", "url": self.path}] + self.files

        file_downloads = file_div.append_tag("div")
        file_downloads.append_tag("label").append("Files:")
        s = file_downloads.append_tag("select", class_="form-control download_urls")
        download_link = file_downloads.append_tag("a", class_="btn btn-primary download_link", download="")
        download_link.append("Download")
        for i, f in enumerate(all_files):
            # Root/Page/Group/Row/this.html
            file_url = os.path.join("..", "..", "..", f["url"])
            if i == 0:
                download_link._attrs["href"] = file_url
            option = s.append_tag("option", value=file_url)
            t = f.get("title")
            if t is None:
                _, t = os.path.splitext(f["url"])
                if t in file_extensions:
                    t = file_extensions[t]
                else:
                    t += " File"
            option.append(t)

        disclose_div = container.append_tag("div", class_="disclosable row", data={"title": "Output Metadata"})
        table = Table(class_="table")
        header = table.append_header()
        header.append_cell("Metadata Key", style="min-width: 15%;")
        header.append_cell("Metadata Value")
        for k, v in self.meta.iteritems():
            r = table.append_row()
            r.append_cell(k)
            r.append_cell(v)

        disclose_div.append(table)

        html_path = os.path.join(self.row.group.dirpath, self.row.title, slugify(self.title) + ".html")
        with open(html_path, "w") as out:
            if toolbar is not None:
                toolbar.setLevel(3)
            out.write(doc.build())

    def getFileName(self):
        return slugify(self.title) + ".html"

    def getURL(self):
        return os.path.join(self.row.dirname, self.getFileName())

    def getLink(self, level):
        path = os.path.join(os.path.dirname(os.path.dirname(self.row.group.dirpath)), self.path)
        if os.path.exists(path):
            l = Link(href=self.getURL(), data={"preview": os.path.join(*([".."] * level + [self.path]))})
        else:
            l = Span()
        l.append(self.title)
        return l


class Row(object):
    def __init__(self, group, spec):
        self.group = group
        self.title = slugify(spec["title"])
        self.cols = {}
        for i, c in enumerate(spec["columns"]):
            if isinstance(c, dict):
                self.cols[i] = Column(self, c)
            else:
                # We don't actually need to keep track of the "string" columns
                # They'll just be plain text
                continue
        self.dirname = os.path.join(self.group.dirname, self.title)

    def getLink(self, col_ind, level):
        if col_ind in self.cols:
            return self.cols[col_ind].getLink(level)
        else:
            return None

    def build(self, toolbar):
        nuke_and_pave(os.path.join(self.group.dirpath, self.title))
        for _, col in self.cols.iteritems():
            col.build(toolbar)


class Group(object):
    def __init__(self, root, parent, spec, rows):
        title = spec["title"]
        self.dirname = slugify(title)
        self.parent = parent
        self.dirpath = os.path.join(root, parent, self.dirname)
        self.rows = []
        for row in rows:
            self.rows.append(Row(self, row))

    def getLink(self, row_ind, col_ind, level):
        return self.rows[row_ind].getLink(col_ind, level)

    def build(self, toolbar):
        nuke_and_pave(self.dirpath)

        for r in self.rows:
            r.build(toolbar)


class Page(object):
    def __init__(self, spec, root_path="./", permissions=None):
        self.name = spec.get("title", "")
        self.short_name = spec.get("short_name", None)

        columns = spec.get("columns", [])

        self.number_of_cols = len(columns)

        groups = spec.get("groups", [])
        self.groups = []
        for g in groups:
            if isinstance(g, (str, unicode)):
                self.groups.append({"title": g, "columns": columns})
            elif isinstance(g, dict):
                if "columns" not in g:
                    g["columns"] = columns
                self.number_of_cols = max(len(g["columns"]), self.number_of_cols)
                self.groups.append(g)
        self.root_path = root_path
        self.permissions = permissions
        self.description = spec.get("description", "")
        self.icon = spec.get("icon", None)
        self.rows = spec.get("rows", [])
        self.long_desc = spec.get("long_description", "")

    def build(self, dirname, toolbar=None):
        nuke_and_pave(os.path.join(self.root_path, dirname))

        doc = Document(title=self.name, level=1)
        if toolbar is not None:
            doc.append(toolbar)
        # Build the header, title, subtitle, etc.
        container = doc.append_tag("div", class_="container")
        row = container.append_tag("div", class_="row")
        title = row.append_tag("h1")
        if self.icon is not None and os.path.exists(os.path.join(self.root_path, self.icon)):
            title.append_tag("img", src="../" + self.icon, width="200px", alt=self.name)
        title.append(self.name)
        if self.description:
            subtitle = row.append_tag("h2")
            subtitle.append(self.description)
        if self.long_desc:
            b = row.append_tag('b')
            b.append_formatted(self.long_desc)
        row.append_tag("hr")

        # Area for the group combobox
        row = container.append_tag("div", class_="row")
        col = row.append_tag("div", class_="col-sm-12")
        label = col.append_tag("label")
        label.append("Jump To:")
        select = col.append_tag("select", class_="form-control group_navigator")

        # Start the actual body of the output set
        row = container.append_tag("div", class_="row")
        col = row.append_tag("div", class_="col-sm-12")
        table = Table(class_="table")
        col.append(table)

        for group_ind, rows in enumerate(self.rows):
            group = self.groups[group_ind]
            column_names = group["columns"]
            group_title = group["title"]
            select.append_tag("option", value="group_%d" % group_ind).append(group_title)

            # Pad the columns so they're appropriately spaced
            column_widths = [1 for i in range(len(column_names) + 1)]
            difflen = self.number_of_cols - len(column_names)
            col_ind = len(column_widths) - 1
            while difflen > 0:
                column_widths[col_ind] += 1
                difflen -= 1
                col_ind = (col_ind - 1) % len(column_widths)

            header = table.append_header()
            column_widths = [str(i) for i in column_widths]
            header.append_cell(group_title, id="group_%d" % group_ind)
            for col_ind in range(len(column_names)):
                header.append_cell(column_names[col_ind], colspan=column_widths[col_ind])

            group_obj = Group(self.root_path, dirname, group, rows)

            for row_ind, r in enumerate(rows):
                tr = table.append_row(class_="output-row")
                cell = TableCell()
                cell.append_formatted("<span>%s</span>" % r["title"])
                tr.append(cell)
                for col_ind, col in enumerate(r["columns"]):
                    l = group_obj.getLink(row_ind, col_ind, 1)
                    if l is None:
                        l = col
                    try:
                        tr.append_cell(l, colspan=column_widths[col_ind])
                    except IndexError:
                        print column_widths, col_ind
            group_obj.build(toolbar)

        with open(os.path.join(self.root_path, dirname, "index.html"), "w") as outfile:
            if toolbar is not None:
                toolbar.setLevel(1)

            outfile.write(doc.build())

        if self.permissions is not None:
            rechmod(os.path.join(self.root_path, dirname), self.permissions)
