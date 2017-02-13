import requests
from output_viewer.utils import slugify
import time
import os
import resource
import hmac
import hashlib
import json

class DiagnosticsViewerClient(object):
    def __init__(self, server, user_id=None, user_key=None, cert=True):
        """
        Create an instance of DiagnosticsViewerClient.
        """

        self.server = server
        self.id = user_id
        self.key = user_key
        self.cert = cert

    def login(self, username, password):
        credentials = requests.post(self.server + "/ea_services/credentials/%s/" % username, data={"password": password}, verify=self.cert)
        if credentials.status_code != 200:
            raise ValueError("Unable to login: Status Code %d; message:\n%s\n" % (credentials.status_code, credentials.text))

        creds = credentials.json()
        self.id = creds["id"]
        self.key = creds["key"]

        return self.id, self.key

    def upload_package(self, directory):
        index = os.path.join(directory, "index.json")
        with open(index) as f:
            index = json.load(f)
        version = slugify(index["version"])

        cwd_cache = os.getcwd()
        if directory[-1] == "/":
            directory = directory[:-1]
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
                            if "files" in col:
                                for f in col["files"]:
                                    if os.path.exists(os.path.join(directory, f["url"])):
                                        files.append(f["url"])
                        else:
                            if os.path.exists(os.path.join(directory, col)) and col != '':
                                files.append(col)
            if "icon" in spec and os.path.exists(os.path.join(directory, spec["icon"])):
                files.append(spec["icon"])

        files = [os.path.join(file_root, filename) for filename in files]
        ds_id = self.upload_files(version, files)
        os.chdir(cwd_cache)
        return ds_id

    def upload_files(self, dataset, files):
        files_remaining = list(files)
        s = requests.Session()
        ds_id = None
        while len(files_remaining) > 0:
            total_size = 0
            files_to_send = {}
            while files_remaining and total_size < 2 * 1024 * 1024 and len(files_to_send) < resource.getrlimit(resource.RLIMIT_NOFILE)[0] / 2:
                fname = files_remaining.pop()
                files_to_send[fname] = open(fname, "rb")
                total_size += os.path.getsize(fname)

            prepped = requests.Request("POST", self.server + "/ea_services/upload/%s/" % dataset, files=files_to_send).prepare()
            h = hmac.new(self.key, prepped.body, hashlib.sha256)
            prepped.headers["X-Signature"] = h.hexdigest()
            prepped.headers["X-UserId"] = self.id

            resp = s.send(prepped, verify=self.cert)
            if resp.status_code != 200:
                raise ValueError("Failed to upload files: %s" % resp.content)
            if ds_id is None:
                ds_id = resp.json().get("dataset", None)
            for f in files_to_send:
                files_to_send[f].close()
            time.sleep(.01)
        return ds_id
