import argparse
from output_viewer import index as viewer
from output_viewer.build import build_viewer
import os
import glob
import datetime
import json


parser = argparse.ArgumentParser()
parser.add_argument("image_directory", default=os.getcwd(), nargs="?", help="Path to the directory containing output. Defaults to current directory.")
parser.add_argument("--separator", default="_", help="Character that separates relevant components of the filename")
parser.add_argument("--order", default=None, help="Order of filename components to group the output")
parser.add_argument("--group", default=None, help="Components to combine")
parser.add_argument("--suffix_sep", default=".", help="Character that separates suffixes (multiple files for one col)")
parser.add_argument("--suffix", default=None, help="Suffix to use as the default output file for a given column.")
parser.add_argument("--title", default=None, help="Title of package (defaults to directory name)")
parser.add_argument("--dataset", default=None, help="Input dataset name; defaults to current date.")
args = parser.parse_args()

files = [f for f in os.listdir(args.image_directory) if f[0] != '.' and not f.endswith(".html") and f != "index.json" and not os.path.isdir(os.path.join(args.image_directory, f))]
indexed = {}
for f in files:
    parts = f.split(args.separator)
    c = parts[-1].split(args.suffix_sep)
    parts[-1] = c[0]

    if args.group and len(parts) > 4:
        group = [int(i) for i in args.group.split(",")]
        p = [parts[g] for g in group]
        p = " ".join(p)
        merged = []
        for i in range(len(parts)):
            if i not in group:
                merged.append(parts[i])
            elif p is not None:
                merged.append(p)
                p = None
        parts = merged

    if args.order:
        order = [int(i) for i in args.order.split(",")]
        fix = []
        for o in order:
            while o >= len(parts):
                o -= 1
            fix.append(o)
        order = fix
        reordered = [parts[i] for i in order]
        for i in range(len(parts)):
            if i not in order:
                reordered.append(parts[i])
        parts = reordered

    subdict = indexed
    for p in parts[:-1]:
        d = subdict.get(p, {})
        subdict[p] = d
        subdict = d
    files = subdict.get(parts[-1], [])
    files.append(f)
    subdict[parts[-1]] = files

title = args.title
if title is None:
    title = os.path.basename(os.path.abspath(args.image_directory))

dataset = args.dataset
if dataset is None:
    d = datetime.date.today()
    dataset = "%d-%d-%d" % (d.year, d.month, d.day)

index = viewer.OutputIndex(title, version=dataset)
for page, groups in list(indexed.items()):
    p = viewer.OutputPage(page)
    index.addPage(p)
    for group, rows in list(groups.items()):
        g = viewer.OutputGroup(group)
        group_ind = len(p.groups)
        p.addGroup(g)
        for row, columns in list(rows.items()):
            cols = []
            for col, files in list(columns.items()):
                default_file = None
                for f in files:
                    if args.suffix:
                        if f.endswith(args.suffix):
                            default_file = f
                            break
                    else:
                        if default_file is None or len(f) < len(default_file):
                            default_file = f
                f = viewer.OutputFile(default_file, title=col, other_files=[{"url": f} for f in files if f != default_file])
                cols.append(f)
            r = viewer.OutputRow(row, cols)
            p.addRow(r, group_ind)

index_path = os.path.abspath(args.image_directory + "/index.json")
index.toJSON(index_path)
build_viewer(index_path)
should_open = input("Open viewer in browser? [y]/n: ")
if should_open != "n":
    import webbrowser
    webbrowser.open("file://" + os.path.abspath(args.image_directory + "/index.html"))
