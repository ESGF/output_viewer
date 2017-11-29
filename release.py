#!/usr/bin/env python

import argparse
import yaml
import git

parser = argparse.ArgumentParser()
parser.add_argument("version")

args = parser.parse_args()

with open("conda_build/meta.yaml") as conda_info:
    conda_meta = yaml.load(conda_info)

conda_meta["package"]["version"] = args.version
conda_meta["source"]["git_rev"] = "v" + args.version

with open("conda_build/meta.yaml", "w") as conda_info:
    yaml.dump(conda_meta, conda_info, default_flow_style=False)

with open("setup.py") as setup:
    lines = []
    for l in setup:
        if l.startswith("version = "):
            l = "version = '%s'\n" % args.version
        lines.append(l)

with open("setup.py", "w") as setup:
    for l in lines:
        setup.write(l)

repo = git.Repo(".")
repo.index.add(["conda_build/meta.yaml", "setup.py"])
c = repo.index.commit("Bump to version %s." % args.version)

tag_message = ["Version %s\n\nChanges:" % args.version]

last_tag = repo.tags[-1]
last_tag_commit = last_tag.commit

commit = c.parents[0]
while (commit.binsha != last_tag_commit.binsha):
    tag_message.append(commit.message)
    if len(commit.parents) > 1:
        raise ValueError("Nonlinear history between this tag and last; aborting.")
    commit = commit.parents[0]

repo.create_tag("v" + args.version, ref=c, message="\n - ".join(tag_message))
print("Successfully created tag %s" % ("v" + args.version))
print("Please review the tag and push to GitHub.")
