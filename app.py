#!/usr/bin/env python3

import os
import stat

from flask import Flask, send_file, abort, jsonify
from flask_cors import CORS
import magic

app = Flask(__name__)
# This is to prevent cors errors relating to files being served from localhost.
cors = CORS(app)


@app.route("/api/browse/", defaults={"subpath": ""})
@app.route("/api/browse/<path:subpath>")
def browse(subpath):
    path = "/" + subpath
    if not os.access(path, os.F_OK):
        abort(404, "File not found.")
    if not os.access(path, os.R_OK):
        abort(502, "The server doesn't have read permissions to the file/dir.")
    if stat.S_ISDIR(os.stat(path).st_mode):
        return get_directory(path)
    filetype = magic.from_file(path, mime=True)
    if filetype[:5] in ["audio", "video"]:
        return send_file("/" + subpath, conditional=True)
    return send_file("/" + subpath)


def get_directory(path):
    dirlist = []
    for item in os.scandir(path):
        item_info = {}
        dirlist.append(item_info)
        item_info["name"] = item.name
        item_info["path"] = item.path
        item_info["permissions"] = stat.filemode(item.stat().st_mode)
        if item.is_file():
            item_info["type"] = "file"
            if os.access(item.path, os.R_OK):
                filetype = magic.from_file(item.path, mime=True)
                item_info["filetype"] = filetype
                if filetype[:5] in ["audio", "video"]:
                    item_info["type"] = "media"
        else:
            item_info["type"] = "directory"
    return jsonify(dirlist)
