# ╭─ INFO ──────────────────────────────────────────────────────────────────────────────────────────────────╮
# │ This is the web server of Bindery.                                                                      │
# │ It runs on PythonAnywhere (pythonanywhere.com).                                                         │
# │                                                                                                         │
# │ What it does:                                                                                           │
# │  - It shows the web page (index.html).                                                                  │
# │  - It gets the book files from the browser and saves them in the Book folder.                           │
# │  - It asks bindery.py to make the preview, the metadata, and the PDF or EPUB file.                      │
# │  - It sends the results back to the browser.                                                            │
# │                                                                                                         │
# │ The real work with the book is done in bindery.py. This file only connects the web page and bindery.py. │
# │                                                                                                         │
# │ Folders on the server:                                                                                  │
# │  - ~/Bindery/Book = the book files                                                                      │
# │  - ~/Bindery/TEMP = temporary files (preview, PDF, EPUB)                                                │
# │                                                                                                         │
# │ After you change this file, click the green "Reload" button in the "Web" tab on PythonAnywhere.         │
# │ Then the change starts to work.                                                                         │
# ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────╯


#      ___                     _      
#     |_ _|_ __  _ __  ___ _ _| |_ ___
#      | || '  \| '_ \/ _ \ '_|  _(_-<
#     |___|_|_|_| .__/\___/_|  \__/__/
#               |_|                   

import bindery
import os
import shutil

from flask import Flask, send_file, request, jsonify


#     __   __        _      _    _        
#     \ \ / /_ _ _ _(_)__ _| |__| |___ ___
#      \ V / _` | '_| / _` | '_ \ / -_|_-<
#       \_/\__,_|_| |_\__,_|_.__/_\___/__/
#                                         

app = Flask(__name__, static_folder=".", static_url_path="")

DIR_BINDERY = os.path.expanduser("~/Bindery")
DIR_BOOK = os.path.join(DIR_BINDERY, "Book")
DIR_TEMP = os.path.join(DIR_BINDERY, "TEMP")

os.makedirs(DIR_BINDERY, exist_ok=True)


#      ___             _   _             
#     | __|  _ _ _  __| |_(_)___ _ _  ___
#     | _| || | ' \/ _|  _| / _ \ ' \(_-<
#     |_| \_,_|_||_\__|\__|_\___/_||_/__/
#                                        

# Make the preview of the book.
# Send back the list of preview pages (page 1 is the cover).
@app.route("/preview_cover", methods=["GET"])
def preview_Cover():
    result = bindery.create_Preview(DIR_BOOK, DIR_TEMP)

    if result["type"] == "error":
        return result["message"], result["status"]

    return jsonify({
        "success": True,
        "pages": result["pages"]
    })

# Send one preview page (an image) to the browser.
@app.route("/preview_page/<int:page>", methods=["GET"])
def preview_Page(page):
    result = bindery.create_Preview(DIR_BOOK, DIR_TEMP, page)

    if result["type"] == "file":
        return send_file(result["file"], max_age=0)

    if result["type"] == "error":
        return result["message"], result["status"]

    return jsonify(result)

# Make the PDF or EPUB file and send it to the browser.
# The browser says which format: "pdf" or "epub".
@app.route("/generate", methods=["POST"])
def generate_Book():
    data = request.get_json(silent=True) or {}
    format = data.get("format", "pdf").lower()

    if format not in ("pdf", "epub"):
        return "Neplatný formát výstupu.", 400

    result = bindery.generate_Book(DIR_BOOK, DIR_TEMP, format)

    if result["type"] == "error":
        return result["message"], result["status"]

    return send_file(
        result["file"],
        mimetype=result["mimetype"],
        as_attachment=True,
        download_name=result["filename"]
    )

# Send the book information (title, author, tags ...) to the browser.
@app.route("/metadata", methods=["GET"])
def get_Matadata():
    result = bindery.load_Metadata(DIR_BOOK)
    settings = bindery.load_Settings(DIR_BOOK)


    result["type"] = settings["type"]

    return jsonify(result)

# Show the main page (index.html).
@app.route("/")
def show_Index():
    return open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8").read()

# Start a new upload.
# Delete the old book and the old temp files, then make an empty Book folder.
@app.route("/start_upload", methods=["POST"])
def start_Upload():

    for folder in (DIR_BOOK, DIR_TEMP):
        shutil.rmtree(folder, ignore_errors=True)

    os.makedirs(DIR_BOOK, exist_ok=True)

    return jsonify({"success": True})

# Save one file from the browser in the Book folder.
# Keep the folder path of the file. Skip unsafe parts of the path (like "..").
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    relative_path = request.form.get("relative_path", "")

    if file is None:
        return "Soubor nebyl přijat.", 400

    if not relative_path:
        relative_path = file.filename

    relative_path = relative_path.replace("\\", "/")

    parts = [
        part
        for part in relative_path.split("/")
        if part not in ("", ".", "..")
    ]

    if not parts:
        return "Neplatná cesta souboru.", 400

    output_path = os.path.join(DIR_BOOK, *parts)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    file.save(output_path)

    return jsonify({"success": True})


#      ___ _            _   
#     / __| |_ __ _ _ _| |_ 
#     \__ \  _/ _` | '_|  _|
#     |___/\__\__,_|_|  \__|
#                           

if __name__ == "__main__":
    app.run()
