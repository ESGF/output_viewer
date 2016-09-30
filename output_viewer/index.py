import json
from collections import OrderedDict


class OutputIndex(object):
    def __init__(self, title, version=None, menu=None):
        self.title = title
        self.pages = []
        self.version = version
        self.menu = menu

    def addPage(self, page):
        self.pages.append(page)

    def toJSON(self, path):
        obj = {"title": self.title, "specification": [page.toDict() for page in self.pages]}
        if self.version:
            obj["version"] = self.version
        obj["output_viewer_version"] = "1"
        if self.menu:
            menus = []
            for m in self.menu:
                menus.append(m.toDict())
            obj["menu"] = menus
        with open(path, "w") as fp:
            json.dump(obj, fp)


class OutputPage(object):
    def __init__(self, title, columns=None, description=None, icon=None, short_name=None):
        """
        Represents a single page of the output.

        :param title: The title of the page.
        :type title: str
        :param columns: The titles of the columns of the output for this page.
        :type columns: list (of str)
        :param description: Long description of this page.
        :type description: str
        :param icon: Path to an icon to represent this page.
        :type icon: str
        :param short_name: Short name for machine usage; will default to the first word of the title, lowercase.
        :type short_name: str
        """
        self.title = title
        if columns is not None:
            self.columns = columns
        else:
            self.columns = []
        self.desc = description
        if short_name is None:
            self.short_name = title.split()[0].lower()
        else:
            self.short_name = short_name
        self.icon = icon
        self.rows = []
        self._menu = None
        self.groups = []

    def addGroup(self, group):
        self.groups.append(group)
        self.rows.append([])

    def addRow(self, row, group_ind):
        self.rows[group_ind].append(row)

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def set_menu(self, menu):
        if self._menu is not None:
            self._menu.removePage(self)
        menu.addPage(self)
        self._menu = menu

    def toDict(self):
        obj = {
            "title": self.title,
            "short_name": self.short_name,
            "rows": [[r.toDict() for r in row] for row in self.rows],
            "groups": [group.toDict() for group in self.groups],
            "columns": self.columns,
        }

        if self.menu:
            obj["menu"] = {"title": self.menu.title, "index": self.menu.indexOf(self)}
        if self.icon:
            obj["icon"] = self.icon
        if self.desc:
            obj["description"] = self.desc
        return obj


class OutputGroup(object):
    def __init__(self, title, columns=None):
        self.title = title
        self.columns = columns

    def toDict(self):
        obj = {
            "title": self.title,
            "columns": self.columns
        }
        if obj["columns"] is None:
            del obj["columns"]
        return obj


class OutputRow(object):
    def __init__(self, title, columns):
        self.title = title
        self.columns = columns

    def toDict(self):
        columns = []
        for col in self.columns:
            if isinstance(col, OutputFile):
                columns.append(col.toDict())
            else:
                columns.append(col)

        return {
            "title": self.title,
            "columns": columns,
        }


class OutputFile(object):
    def __init__(self, path, meta=None, title=None, other_files=None):
        self.path = path
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

        self.title = title
        self.other_files = other_files
        if self.other_files is None:
            self.other_files = []

    def toDict(self):
        return {
            "path": self.path,
            "title": self.title,
            "meta": self.meta,
            "files": self.other_files
        }


class OutputMenu(object):
    def __init__(self, title, items=None):
        self.title = title
        self.url = None
        self.items = items

    def addPage(self, page):
        if page not in self.items:
            self.items.append(page)

    def removePage(self, page):
        if page in self.items:
            self.items.remove(page)

    def indexOf(self, page):
        return self.items.index(page)

    def toDict(self):
        obj = {"title": self.title}
        if self.url is not None:
            obj["url"] = self.url
        if isinstance(self.items, dict):
            obj["items"] = [{"title": t, "url": self.items[t]} for t in self.items]
        elif isinstance(self.items, list):
            items = []
            for i in self.items:
                if isinstance(i, OutputPage):
                    items.append({"title": i.title, "url": "/".join([i.short_name, "index.html"])})
                else:
                    items.append(i)
            obj["items"] = items
        return obj
