#!/usr/bin/env python

import requests
import argparse
import json
import getpass
import hashlib
import hmac
import sys
import os
from output_viewer.utils import slugify
from output_viewer.config import ViewerConfig
from output_viewer.diagsviewer import DiagnosticsViewerClient
import resource
import time



def upload_pkg(directory, client):
    index = os.path.join(directory, "index.json")
    with open(index) as f:
        index = json.load(f)
    version = slugify(index["version"])

    cwd_cache = os.getcwd()
    os.chdir(os.path.dirname(directory))
    file_root = os.path.basename(directory)
    files = ["index.json"]
    for spec in index["specification"]:
        for group in spec["rows"]:
            for row in group:
                for col in row["columns"]:
                    if isinstance(col, dict) and "path" in col:
                        if col["path"] == '':
                            continue
                        if os.path.exists(os.path.join(directory, col['path'])):
                            files.append(col['path'])
                    else:
                        if os.path.exists(os.path.join(directory, col)) and col != '':
                            files.append(col)
        if "icon" in spec and os.path.exists(os.path.join(directory, spec["icon"])):
            files.append(spec["icon"])
    print files
    files = [os.path.join(file_root, filename) for filename in files]
    client.upload_files(version, files)
    os.chdir(cwd_cache)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload an output set to an instance of DiagnosticsViewer.")
    parser.add_argument("output", help="Path to directory containing an index.json file and the output it refers to.")
    parser.add_argument("--user", help="Username to log into server with. If previously logged in to the targeted server, not needed. You will be prompted for your password.")
    parser.add_argument("--server", help="Server to send files to. Will use whatever server was used last, or https://acme-ea.ornl.gov (default)", default=None)
    parser.add_argument("--cert", help="Path to a certificate to use to authenticate request (useful if at LLNL or other firewalled institution). Will attempt to reuse last one if SSL errors occur. Set to False if you want to skip verification (not recommended).")
    args = parser.parse_args()

    directory = args.output
    directory = os.path.abspath(os.path.expanduser(directory))

    cfg = ViewerConfig()

    if args.server is not None:
        server = args.server
    else:
        server = cfg.get("upload", "last_server")

        if server is None:
            server = "https://diags-viewer.llnl.gov"

    cfg.set("upload", "last_server", server)

    if args.cert is not None:
        cert = args.cert
    else:
        cert = cfg.get("certificate", "last_cert")

    if cert is not None and cert.lower() == "false":
        cert = False

    client = DiagnosticsViewerClient(server, cert=cert)

    if args.user is not None:
        password = getpass.getpass("Password: ")

        user_id, user_key = client.login(args.user, password)

        cfg.set(server, "id", user_id)
        cfg.set(server, "key", user_key)
    else:
        user_id = cfg.get(server, "id")
        user_key = cfg.get(server, "key")

        if None in (user_id, user_key):
            print "No username/password provided and no cached credentials available for server %s. To provide username/password, use the --user option and enter your password when prompted." % server
            sys.exit(1)

        client.id = user_id
        client.key = user_key

    cfg.save()

    upload_pkg(directory, client)