#!/usr/bin/env python
import getpass
import requests
import argparse
from output_viewer.config import ViewerConfig
from output_viewer.diagsviewer import DiagnosticsViewerClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log in to a DiagnosticsViewer server and cache credentials locally.")
    parser.add_argument("--user", help="Username to log into server with. If previously logged in to the targeted server, not needed. You will be prompted for your password.")
    parser.add_argument("server", nargs="?", help="Server to login. Will use whatever server was used last if not provided.", default="https://diags-viewer.llnl.gov")
    parser.add_argument("--cert", help="Path to a certificate to use to authenticate request (useful if at LLNL or other firewalled institution). Will attempt to reuse last one if SSL errors occur. Set to False if you want to skip verification (not recommended).")
    args = parser.parse_args()

    cfg = ViewerConfig()

    server = args.server

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
            print("No username/password provided and no cached credentials available for server %s. To provide username/password, use the --user option and enter your password when prompted." % server)
            sys.exit(1)

        client.id = user_id
        client.key = user_key

    cfg.save()
