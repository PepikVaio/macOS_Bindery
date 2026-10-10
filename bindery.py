# ╭─ Info ─────────────────────────────────────────────────────────────────────────╮
# │ Bindery makes a PDF and an EPUB book from a folder with your text files.       │
# │ It is used on the desktop (Mac, Windows) and by the web server (flask_app.py). │
# │                                                                                │
# │ How to start it:                                                               │
# │  - Run the script: python3 bindery.py                                          │
# │  - Or make the Mac or Win app: ./build.sh                                      │
# ╰────────────────────────────────────────────────────────────────────────────────╯

import html
import locale
import markdown
import os
import pymupdf
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

from datetime import datetime
from io import BytesIO
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.xmp import XmpInformation
from weasyprint import HTML


def clean_Name_File(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', ' ', filename).strip()
    filename = filename.rstrip(". ")

    if not filename:
        filename = "book"

    return filename


def copy_Files(DIR_BASE, DIR_TEMP):
    DIR_FONTS = os.path.join(DIR_BASE, "Fonts")
    DIR_MISC = os.path.join(DIR_BASE, "Misc")
    DIR_IMAGES = os.path.join(DIR_BASE, "Images")

    shutil.copytree(DIR_FONTS, os.path.join(DIR_TEMP, "Fonts"), dirs_exist_ok=True)
    shutil.copytree(DIR_MISC, os.path.join(DIR_TEMP, "Misc"), dirs_exist_ok=True)
    shutil.copytree(DIR_IMAGES, os.path.join(DIR_TEMP, "Images"), dirs_exist_ok=True)


def create_Cover(DIR_TEMP, preview=False):
    file_Html = os.path.join(DIR_TEMP, "Text", "cover.html")
    file_Cover = None

    for extension in ["png", "jpg", "jpeg"]:
        path = os.path.join(DIR_TEMP, "Images", f"cover.{extension}")

        if os.path.exists(path):
            file_Cover = path
            break

    if not file_Cover:
        raise FileNotFoundError("Obálka nebyla nalezena.")

    with open(file_Html, "r", encoding="utf-8") as input:
        html = input.read()

    html = html.replace("</head>", "<style>.cover .background { background-image: none !important; }</style></head>")
    text_Pdf = BytesIO()

    HTML(string=html, base_url=os.path.dirname(file_Html)).write_pdf(text_Pdf)
    text_Pdf.seek(0)

    pdf = pymupdf.open(stream=text_Pdf.getvalue(), filetype="pdf")
    pixmap = pdf[0].get_pixmap(matrix=pymupdf.Matrix(96 / 72, 96 / 72), alpha=True)
    text_Image = Image.frombytes("RGBA", (pixmap.width, pixmap.height), pixmap.samples)

    with Image.open(file_Cover) as original:
        cover = original.convert("RGBA")

    text_Image = text_Image.resize(cover.size, Image.Resampling.LANCZOS)

    cover.alpha_composite(text_Image)

    if preview:
        file_Preview = os.path.join(DIR_TEMP, "Preview", "page_01.png")
        os.makedirs(os.path.dirname(file_Preview), exist_ok=True)
        cover.save(file_Preview)
        file_Cover = file_Preview
    else:
        extension = os.path.splitext(file_Cover)[1].lower()

        if extension == ".png":
            cover.save(file_Cover)
        else:
            cover.convert("RGB").save(file_Cover, quality=95)

    pdf.close()

    return file_Cover


def create_Css(DIR_PAGES, DIR_STYLES, DIR_TEMP):
    print("", flush=True)
    print("CSS", flush=True)
    print("────────────────────────────────────", flush=True)

    print("Načítám knihu...", flush=True)
    book, page_Width, page_Height, file_Cover, file_Background, file_Width, file_Height = load_Data(DIR_BASE, DIR_TEMP)

    settings = load_Settings(DIR_BASE)

    replacements = {
        "PAGE_WIDTH": page_Width,
        "PAGE_HEIGHT": page_Height,
        "FILE_COVER": os.path.basename(file_Cover),
        "FILE_BACKGROUND": os.path.basename(file_Background) if file_Background else "",
        "IMAGE_SIZE": settings["image_size"]
    }

    files = [
        file
        for file in os.listdir(DIR_STYLES)
        if file.lower().endswith(".css")
    ]

    for file in sorted(files):

        print(f"Generuji styl: {file}", flush=True)
        source = os.path.join(DIR_STYLES, file)

        destination = os.path.join(DIR_TEMP, "Styles", file)

        with open(source, "r", encoding="utf-8") as input:
            style = input.read()

        for key, value in replacements.items():
            style = style.replace(f"{{{{{key}}}}}", value)

        with open(destination, "w", encoding="utf-8") as output:
            output.write(style)


def create_Html(DIR_PAGES, DIR_TEMP, DIR_STYLES, DIR_TEMPLATES):
    print("", flush=True)
    print("HTML", flush=True)
    print("────────────────────────────────────", flush=True)

    print("Načítám knihu...", flush=True)
    book, page_Width, page_Height, file_Cover, file_Background, file_Width, file_Height = load_Data(DIR_BASE, DIR_TEMP)

    settings = load_Settings(DIR_BASE)

    print("Načítám kapitoly...", flush=True)
    pages = load_Markdown(DIR_PAGES)

    replacements = {
        "LANGUAGE": book["language"],
        "TITLE": book["title"],
        "SUBTITLE": book["subtitle"],
        "AUTHOR": book["author"],
        "PAGE_WIDTH": page_Width,
        "PAGE_HEIGHT": page_Height,
        "FILE_COVER": os.path.basename(file_Cover),
        "FILE_WIDTH": f"{file_Width}",
        "FILE_HEIGHT": f"{file_Height}",
        "TYPE": settings["type"]
    }

    def replace_template_values(document_Html, styles=None, content=None):
        if styles is not None:
            document_Html = document_Html.replace("{{STYLES}}", styles)

        if content is not None:
            document_Html = document_Html.replace("{{CONTENT}}", content)

        protected_code_blocks = []

        def protect_code_block(match):
            protected_code_blocks.append(match.group(0))
            return f"@@BINDERY_PROTECTED_CODE_{len(protected_code_blocks) - 1}@@"

        document_Html = re.sub(r"<pre\b[^>]*>[\s\S]*?</pre>", protect_code_block, document_Html)

        for key, value in replacements.items():
            document_Html = document_Html.replace(f"{{{{{key}}}}}", str(value))

        for index, code_block in enumerate(protected_code_blocks):
            document_Html = document_Html.replace(f"@@BINDERY_PROTECTED_CODE_{index}@@", code_block)

        return document_Html

    template = load_Template("cover", DIR_TEMPLATES)
    styles = load_Styles("cover", DIR_STYLES)
    document_Html = replace_template_values(template, styles=styles)
    file_Html = os.path.join(DIR_TEMP, "Text", "cover.html")

    print("Generuji: cover.html", flush=True)
    with open(file_Html, "w", encoding="utf-8") as output:
        output.write(document_Html)

    template = load_Template("chapter", DIR_TEMPLATES)
    styles = load_Styles("chapter", DIR_STYLES)

    for file, text_Markdown in pages:
        code_blocks = []

        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"@@CODE_BLOCK_{len(code_blocks) - 1}@@"

        text_Markdown = re.sub(r'(?m)^(?:    (?![-*+]\s|\d+\.\s).*(?:\n|$))+', save_code_block, text_Markdown)
        text_Markdown = re.sub(r'```[\s\S]*?```', save_code_block, text_Markdown)

        inline_codes = []

        def save_inline_code(match):
            inline_codes.append(match.group(0))
            return f"@@INLINE_CODE_{len(inline_codes) - 1}@@"

        text_Markdown = re.sub(r'(`+)([^\n]*?)\1', save_inline_code, text_Markdown)
        images = []

        def save_image(match):
            images.append(match.groups())
            return f"@@IMAGE_{len(images) - 1}@@"

        text_Markdown = re.sub(r'!\[([^|\]]+)(?:\|(\d+(?:\.\d+)?)%)?\]\(([^)]+)\)', save_image, text_Markdown)
        text_Markdown = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text_Markdown)
        text_Markdown = text_Markdown.replace("\u00a0", " ")

        for index, inline_code in enumerate(inline_codes):
            text_Markdown = text_Markdown.replace(f"@@INLINE_CODE_{index}@@", inline_code)

        lines = text_Markdown.splitlines()
        new_lines = []

        for index, line in enumerate(lines):
            if (line.strip() == "" and not line.startswith(("    ", "\t")) and index > 0 and index + 1 < len(lines)):
                previous_line = lines[index - 1]
                next_line = lines[index + 1]

                if (re.match(r'^\s*(?:[-*+]|\d+\.)\s+', previous_line) and re.match(r'^\s*(?:[-*+]|\d+\.)\s+', next_line)):
                    new_lines.append("<!-- LIST_BREAK -->")
                    continue

                if (previous_line.startswith(">") and next_line.startswith(">")):
                    new_lines.append("<!-- QUOTE_BREAK -->")
                    continue

            new_lines.append(line)

        text_Markdown = "\n".join(new_lines)

        content = markdown.markdown(text_Markdown, extensions=["extra", "tables", "fenced_code", "sane_lists"])
        content = content.replace("<!-- LIST_BREAK -->", "")
        content = content.replace("<!-- QUOTE_BREAK -->", "")
        content = re.sub(r'(?<![=\w])"([^"\n]+)"', r'<span class="quote">"\1"</span>', content)

        for index, image in enumerate(images):
            alt, width, source = image

            if width:
                image_html = (
                    f'<img src="{source}" alt="{alt}" '
                    f'class="img_Width_{width.replace(".", "_")}" />'
                )
            else:
                image_html = f'<img src="{source}" alt="{alt}" />'

            content = content.replace(f'@@IMAGE_{index}@@', image_html)

        for index, code_block in enumerate(code_blocks):
            code_content = code_block

            if code_content.startswith("```"):
                code_content = re.sub(r'^```[^\n]*\n?', '', code_content)
                code_content = re.sub(r'\n?```$', '', code_content)

            elif code_content.startswith("    "):
                code_content = "\n".join(line[4:]
                                         if line.startswith("    ")
                                         else line for line in code_content.splitlines())

            code_content = code_content.rstrip("\n")
            code_html = (f'</p><pre><code>{html.escape(code_content)}</code></pre><p>')
            content = content.replace(f'<p>@@CODE_BLOCK_{index}@@</p>', code_html)
            content = content.replace(f'@@CODE_BLOCK_{index}@@', code_html)

        content = content.replace("<p></p>", "")
        content = content.replace("\n</code></pre>", "</code></pre>")

        document_Html = replace_template_values(template, styles=styles, content=content)
        name_Html = os.path.splitext(file)[0] + ".html"
        file_Html = os.path.join(DIR_TEMP, "Text", name_Html)

        print(f"Generuji: {name_Html}", flush=True)
        with open(file_Html, "w", encoding="utf-8") as output:
            output.write(document_Html)


def create_Epub(DIR_OUTPUT, DIR_BASE, DIR_TEMP):
    print("", flush=True)
    print("EPUB", flush=True)
    print("────────────────────────────────────", flush=True)

    print("Načítám knihu...", flush=True)
    book = load_Description(DIR_BASE)

    DIR_TEXT = os.path.join(DIR_TEMP, "Text")
    DIR_STYLES = os.path.join(DIR_TEMP, "Styles")
    DIR_IMAGES = os.path.join(DIR_TEMP, "Images")
    DIR_FONTS = os.path.join(DIR_TEMP, "Fonts")
    DIR_MISC = os.path.join(DIR_TEMP, "Misc")

    print("Načítám kapitoly...", flush=True)
    file_Htmls = [
        file
        for file in os.listdir(DIR_TEXT)
        if file.lower().endswith(".html")
    ]

    def epub_Order(file):
        name = os.path.splitext(file)[0].lower()

        if name == "cover":
            return (0, 0)

        if name == "prolog":
            return (1, 0)

        if name.startswith("chapter_"):
            match = re.search(r"chapter_(\d+)", name)

            if match:
                return (2, int(match.group(1)))

        if name == "epilog":
            return (3, 0)

        return (4, name)

    file_Htmls.sort(key=epub_Order)
    file_Epub = os.path.join(DIR_OUTPUT, clean_Name_File(book["title"]) + ".epub")

    with zipfile.ZipFile(file_Epub, "w") as epub:
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0"
    xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf"
            media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        )

        manifest = []
        spine = []
        toc = []

        print("", flush=True)
        print("Generuji: cover...", flush=True)

        file_Cover = create_Cover(DIR_TEMP)
        cover_file = os.path.basename(file_Cover)
        cover_path = file_Cover

        print(f"Přidávám: Images/{cover_file}", flush=True)
        epub.write(cover_path, f"OEBPS/Images/{cover_file}")

        cover_Extension = os.path.splitext(cover_file)[1].lower()
        cover_Media_Type = "image/png" if cover_Extension == ".png" else "image/jpeg"

        manifest.append(
            f'<item id="cover-image" '
            f'href="Images/{cover_file}" '
            f'media-type="{cover_Media_Type}"/>'
        )

        font_Types = {
            ".ttf": "font/ttf",
            ".otf": "font/otf",
            ".woff": "font/woff",
            ".woff2": "font/woff2"
        }

        for root, directories, files in os.walk(DIR_FONTS):
            for file in files:
                source = os.path.join(root, file)
                relative = os.path.relpath(source, DIR_FONTS).replace("\\", "/")
                path_Epub = f"OEBPS/Fonts/{relative}"

                print(f"Přidávám: Fonts/{relative}", flush=True)
                epub.write(source, path_Epub)

                extension = os.path.splitext(file)[1].lower()
                type_Media = font_Types.get(extension)

                if type_Media:
                    manifest.append(
                        f'<item id="font_{len(manifest)}" '
                        f'href="Fonts/{relative}" '
                        f'media-type="{type_Media}"/>'
                    )

        for root, directories, files in os.walk(DIR_MISC):
            for file in files:
                source = os.path.join(root, file)
                relative = os.path.relpath(source, DIR_MISC).replace("\\", "/")
                path_Epub = f"OEBPS/Misc/{relative}"

                print(f"Přidávám: Misc/{relative}", flush=True)
                epub.write(source, path_Epub)

                manifest.append(
                    f'<item id="misc_{len(manifest)}" '
                    f'href="Misc/{relative}" '
                    f'media-type="text/plain"/>'
                )

        for file in sorted(os.listdir(DIR_STYLES)):

            if not file.lower().endswith(".css"):
                continue

            source = os.path.join(DIR_STYLES, file)
            path_Epub = f"OEBPS/Styles/{file}"

            print(f"Přidávám: Styles/{file}", flush=True)
            with open(source, "r", encoding="utf-8") as file_css:
                content_css = file_css.read()

            content_css = re.sub(r'((?:p|li|blockquote|h[1-6])\s*\{[^}]*?)font-size\s*:[^;]+;?', r'\1', content_css, flags=re.IGNORECASE | re.DOTALL)
            
            epub.writestr(path_Epub, content_css)
            manifest.append(
                f'<item id="style_{len(manifest)}" '
                f'href="Styles/{file}" '
                f'media-type="text/css"/>'
            )

        for index, file_Html in enumerate(file_Htmls):
            id_File = f"chapter_{index + 1}"
            source = os.path.join(DIR_TEXT, file_Html)

            with open(source, "r", encoding="utf-8") as file:
                content = file.read()

            if file_Html == "cover.html":
                content = re.sub(r'<body\b[^>]*>.*?</body>', f'<body>\n    <img src="../Images/{cover_file}" />\n</body>', content, flags=re.IGNORECASE | re.DOTALL)

            else:
                content = re.sub(r'<img\b[^>]*>', '', content, flags=re.IGNORECASE)
                content = re.sub(r'<p>\s*</p>', '', content, flags=re.IGNORECASE)

            if file_Html != "cover.html":
                headings = list(
                    re.finditer(
                        r'<h([1-6])>(.*?)</h\1>',
                        content,
                        flags=re.IGNORECASE | re.DOTALL
                    )
                )

                toc_headings = []

                for heading_index, heading in enumerate(headings):
                    level = int(heading.group(1))
                    title = re.sub(r'<[^>]+>', '', heading.group(2)).strip()
                    title = re.sub(r'\s+', ' ', title).strip()
                    heading_id = f"toc_{os.path.splitext(file_Html)[0]}_{heading_index + 1}"

                    toc_headings.append({
                        "level": level,
                        "title": title,
                        "file": file_Html,
                        "id": heading_id
                    })

                for heading_index in range(len(toc_headings) - 1, -1, -1):
                    heading = headings[heading_index]
                    toc_heading = toc_headings[heading_index]

                    content = (
                        content[:heading.start()]
                        + f'<h{toc_heading["level"]} id="{toc_heading["id"]}">{heading.group(2)}</h{toc_heading["level"]}>'
                        + content[heading.end():]
                    )

                toc.extend(toc_headings)

            print(f"Přidávám: Text/{file_Html}", flush=True)
            epub.writestr(f"OEBPS/Text/{file_Html}", content)

            manifest.append(
                f'<item id="{id_File}" '
                f'href="Text/{file_Html}" '
                f'media-type="application/xhtml+xml"/>'
            )

            spine.append(f'<itemref idref="{id_File}"/>')

        rating = ""
        if book["rating"] and book["rating"] != "-":
            stars = book["rating"].count("*")
            rating = min(stars * 2, 10)

        identifier = book["identifier"]
        if identifier.lower().startswith("isbn:"):
            identifier = identifier[5:].strip()

        published = ""
        if book["published"] and book["published"].lower() != "none":
            published = datetime.strptime(book["published"], "%d/%m/%Y").strftime("%Y-%m-%d")

        description = html.escape(book["description"])

        print("", flush=True)
        print("Generuji: content.opf", flush=True)
        epub.writestr(
            "OEBPS/content.opf",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
    version="2.0" unique-identifier="book-id">

    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:identifier id="book-id">{identifier or "bindery-book"}</dc:identifier>
        <dc:title>{book["title"]}</dc:title>
        <dc:creator>{book["author"]}</dc:creator>
        <dc:language>{book["language"] or "cs"}</dc:language>
        <dc:publisher>{book["publisher"]}</dc:publisher>
        <dc:date>{published}</dc:date>
        <dc:description>{description}</dc:description>
        <dc:subject>{book["tags"]}</dc:subject>
        <meta name="calibre:series" content="{book["series"]}"/>
        <meta name="calibre:series_index" content="{book["number"]}"/>
        <meta name="calibre:rating" content="{rating}"/>
    </metadata>

    <manifest>
        {''.join(manifest)}
        <item id="ncx"
            href="toc.ncx"
            media-type="application/x-dtbncx+xml"/>
    </manifest>

    <spine toc="ncx">
        {''.join(spine)}
    </spine>

</package>"""
        )

        nav_points = []
        nav_stack = []

        for index, chapter in enumerate(toc):
            level = chapter["level"]

            while len(nav_stack) >= level:
                nav_stack.pop()

            nav_point = {
                "id": f"navPoint-{index + 1}",
                "playOrder": index + 1,
                "title": chapter["title"],
                "file": chapter["file"],
                "target": chapter["id"],
                "level": level,
                "children": []
            }

            if nav_stack:
                nav_stack[-1]["children"].append(nav_point)
            else:
                nav_points.append(nav_point)

            nav_stack.append(nav_point)

        def create_NavPoint(nav_point):
            children = "".join(
                create_NavPoint(child)
                for child in nav_point["children"]
            )

            target = f'Text/{nav_point["file"]}'

            if nav_point["target"]:
                target += f'#{nav_point["target"]}'

            return f'''<navPoint id="{nav_point["id"]}" playOrder="{nav_point["playOrder"]}">
    <navLabel>
        <text>{html.escape(nav_point["title"])}</text>
    </navLabel>
    <content src="{target}"/>
    {children}
</navPoint>'''

        navigation = "".join(
            create_NavPoint(nav_point)
            for nav_point in nav_points
        )

        print("Generuji: toc.ncx", flush=True)
        epub.writestr(
            "OEBPS/toc.ncx",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
    "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"
    version="2005-1">

    <head>
        <meta name="dtb:uid"
            content="{book["identifier"] or "bindery-book"}"/>
    </head>

    <docTitle>
        <text>{book["title"]}</text>
    </docTitle>

    <navMap>
        {navigation}
    </navMap>

</ncx>"""
        )

    print("", flush=True)
    print(f"Vytvořeno: {os.path.basename(file_Epub)}", flush=True)


def create_Pdf(DIR_OUTPUT, DIR_BASE, DIR_PAGES, DIR_TEMP):
    print("", flush=True)
    print("PDF", flush=True)
    print("────────────────────────────────────", flush=True)

    print("Načítám knihu...", flush=True)
    book = load_Description(DIR_BASE)

    print("Načítám kapitoly...", flush=True)
    pages = load_Markdown(DIR_PAGES)
    writer = PdfWriter()
    chapters = []

    file_Html = os.path.join(DIR_TEMP, "Text", "cover.html")
    pdf_data = BytesIO()

    print("", flush=True)
    print("Generuji: cover.pdf", flush=True)
    HTML(filename=file_Html, base_url=os.path.dirname(file_Html)).write_pdf(pdf_data)

    pdf_data.seek(0)

    cover_reader = PdfReader(pdf_data)

    for page in cover_reader.pages:
        writer.add_page(page)

    for file, _ in pages:
        name_Html = os.path.splitext(file)[0] + ".html"

        file_Html = os.path.join(DIR_TEMP, "Text", name_Html)

        print(f"Generuji: {os.path.splitext(name_Html)[0]}.pdf", flush=True)
        pdf_data = BytesIO()
        HTML(filename=file_Html, base_url=os.path.dirname(file_Html)).write_pdf(pdf_data)

        pdf_data.seek(0)

        reader = PdfReader(pdf_data)

        page_offset = len(writer.pages)

        for page in reader.pages:
            writer.add_page(page)

        name = os.path.splitext(file)[0].lower()

        if name.startswith("chapter_"):

            with open(file_Html, "r", encoding="utf-8") as input:
                html = input.read()

            chapter_titles = list(
                re.finditer(
                    r"<h([1-6])>(.*?)</h\1>",
                    html,
                    flags=re.IGNORECASE | re.DOTALL
                )
            )

            pdf = pymupdf.open(stream=pdf_data.getvalue(), filetype="pdf")

            for chapter_title in chapter_titles:
                level = int(chapter_title.group(1))
                title = re.sub(r"<[^>]+>", "", chapter_title.group(2)).strip()
                title = re.sub(r"\s+", " ", title).strip()

                page = None

                for index, pdf_page in enumerate(pdf):
                    text = pdf_page.get_text()
                    text = re.sub(r"\s+", " ", text).strip()

                    if title in text:
                        page = page_offset + index
                        break

                if page is None:
                    page = page_offset

                chapters.append({
                    "level": level,
                    "title": title,
                    "page": page
                })

            pdf.close()

    print("Generuji: TOC...", flush=True)

    outline = []

    for chapter in chapters:
        while len(outline) >= chapter["level"]:
            outline.pop()

        parent = outline[-1] if outline else None

        item = writer.add_outline_item(
            chapter["title"],
            chapter["page"],
            parent=parent
        )

        outline.append(item)

    safe_title = clean_Name_File(book["title"])
    OUTPUT_FILE = os.path.join(DIR_OUTPUT, f"{safe_title}.pdf")

    print("", flush=True)
    print("Nastavuji metadata...", flush=True)
    writer.add_metadata({
        "/Title": book["title"],
        "/Author": book["author"],
        "/CreationDate": datetime.now().astimezone().strftime("D:%Y%m%d%H%M%S%z")
    })

    xmp = XmpInformation.create()

    if book["title"]:
        xmp.dc_title = {"x-default": book["title"]}

    if book["author"]:
        xmp.dc_creator = [book["author"]]

    if book["tags"]:
        tags = [
            tag.strip()
            for tag in book["tags"].split(",")
            if tag.strip()
        ]

        xmp.dc_subject = tags

    if book["identifier"] and book["identifier"].lower() != "none":
        identifier = book["identifier"]

        if identifier.lower().startswith("isbn:"):
            isbn = identifier[5:].strip()
            namespace = "http://prismstandard.org/namespaces/basic/2.0/"
            prefix = "prism"

            description = xmp._get_or_create_description()
            description.setAttributeNS("http://www.w3.org/2000/xmlns/", f"xmlns:{prefix}", namespace)

            document = xmp.rdf_root.ownerDocument

            element = document.createElementNS(namespace, f"{prefix}:isbn")
            element.appendChild(document.createTextNode(isbn))

            description.appendChild(element)
            xmp._update_stream()

        else:
            xmp.dc_identifier = identifier

    if book["published"] and book["published"].lower() != "none":
        published = datetime.strptime(book["published"], "%d/%m/%Y")
        xmp.dc_date = [published.strftime("%Y-%m-%dT00:00:00+00:00")]

    if book["date"] and book["date"].lower() != "none":
        xmp.dc_date = [book["date"]]

    if book["publisher"] and book["publisher"].lower() != "none":
        xmp.dc_publisher = [book["publisher"]]

    if book["language"] and book["language"].lower() != "none":
        xmp.dc_language = [book["language"]]

    if book["description"]:
        xmp.dc_description = {"x-default": book["description"]}

    set_Calibre_Series(xmp, book["series"], book["number"])
    set_Calibre_Rating(xmp, book["rating"])

    xmp.dc_format = "application/pdf"
    writer.xmp_metadata = xmp

    with open(OUTPUT_FILE, "wb") as output:
        writer.write(output)

    print("", flush=True)
    print(f"Vytvořeno: {os.path.basename(OUTPUT_FILE)}", flush=True)


def create_Preview(DIR_BOOK, DIR_TEMP, page=None):

    global DIR_BASE
    DIR_BASE = DIR_BOOK

    DIR_PAGES = os.path.join(DIR_BOOK, "Pages")
    DIR_STYLES = os.path.join(DIR_BOOK, "Styles")
    DIR_TEMPLATES = os.path.join(DIR_BOOK, "Templates")

    if page is not None:

        preview_File = os.path.join(DIR_TEMP, "Preview", f"page_{page:02d}.png")

        if not os.path.exists(preview_File):

            return {
                "type": "error",
                "message": "Náhled stránky neexistuje.",
                "status": 404
            }

        return {
            "type": "file",
            "file": preview_File
        }

    try:

        sync_Book(DIR_BOOK, DIR_PAGES, "web")
        prepare_Folder(DIR_TEMP)

        copy_Files(DIR_BOOK, DIR_TEMP)
        create_Html(DIR_PAGES, DIR_TEMP, DIR_STYLES, DIR_TEMPLATES)
        create_Css(DIR_PAGES, DIR_STYLES, DIR_TEMP)
        create_Cover(DIR_TEMP, preview=True)

        preview_Dir = os.path.join(DIR_TEMP, "Preview")

        os.makedirs(preview_Dir, exist_ok=True)

        page_Number = 2

        for file, text in load_Markdown(DIR_PAGES):

            name = os.path.splitext(file)[0]

            if not name.startswith("chapter_"):
                continue

            html_File = os.path.join(DIR_TEMP, "Text", f"{name}.html")

            if not os.path.exists(html_File):
                continue

            pdf_File = os.path.join(DIR_TEMP, f"{name}.pdf")

            HTML(filename=html_File).write_pdf(pdf_File)

            document = pymupdf.open(pdf_File)

            for pdf_Page in document:

                if page_Number >= 7:
                    break

                pixmap = pdf_Page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
                image_File = os.path.join(preview_Dir, f"page_{page_Number:02d}.png")

                pixmap.save(image_File)

                page_Number += 1

            document.close()
            os.remove(pdf_File)

            if page_Number >= 7:
                break

        pages = []

        for number in range(1, page_Number):

            image_File = os.path.join(preview_Dir, f"page_{number:02d}.png")

            if os.path.exists(image_File):
                pages.append(number)

        return {
            "type": "success",
            "pages": pages
        }

    except Exception as error:

        return {
            "type": "error",
            "message": f"<pre>{error}</pre>",
            "status": 500
        }


def find_Output(directory, extension):
    files = []

    for root, directories, filenames in os.walk(directory):
        for filename in filenames:

            if filename.lower().endswith(extension):
                files.append(os.path.join(root, filename))

    if not files:
        return None

    return max(files, key=os.path.getmtime)


def get_Language():
    if sys.platform == "darwin":
        result = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True, text=True)
        match = re.search(r'"([a-z]{2})', result.stdout)

        if match:
            language = match.group(1)
        else:
            language = "en"

    else:
        language = locale.getlocale()[0]

        if language:
            language = language[:2]

        if language not in TEXTS:
            language = "en"

    return language


def generate_Book(DIR_BASE, DIR_TEMP, format):

    if not os.path.isdir(DIR_BASE):
        return {
            "type": "error",
            "message": "Kniha neexistuje.",
            "status": 404
        }

    DIR_PAGES = os.path.join(DIR_BASE, "Pages")
    DIR_OUTPUT = os.path.join(DIR_TEMP, "Output")

    os.makedirs(DIR_OUTPUT, exist_ok=True)

    try:

        if format == "pdf":
            create_Pdf(DIR_OUTPUT, DIR_BASE, DIR_PAGES, DIR_TEMP)
            extension = ".pdf"
            mimetype = "application/pdf"

        else:
            create_Epub(DIR_OUTPUT, DIR_BASE, DIR_TEMP)
            extension = ".epub"
            mimetype = "application/epub+zip"

        output_file = find_Output(DIR_OUTPUT, extension)

        if not output_file:

            return {
                "type": "error",
                "message": format.upper() + " nebylo vytvořeno.",
                "status": 500
            }

        book = load_Metadata(DIR_BASE)

        filename = (clean_Name_File(book["title"]) + extension)

        return {
            "type": "file",
            "file": output_file,
            "filename": filename,
            "mimetype": mimetype
        }

    except Exception as error:

        return {
            "type": "error",
            "message": f"<pre>{error}</pre>",
            "status": 500
        }


def load_Data(DIR_BASE, DIR_TEMP):
    book = load_Description(DIR_BASE)
    settings = load_Settings(DIR_BASE)
    format_Book = settings["format"].strip()

    formats = {
        "A0": ("841mm", "1189mm"),
        "A1": ("594mm", "841mm"),
        "A2": ("420mm", "594mm"),
        "A3": ("297mm", "420mm"),
        "A4": ("210mm", "297mm"),
        "A5": ("148mm", "210mm"),
        "A6": ("105mm", "148mm"),
        "A7": ("74mm", "105mm"),
        "A8": ("52mm", "74mm"),
        "A9": ("37mm", "52mm"),
        "A10": ("26mm", "37mm"),
        "B0": ("1000mm", "1414mm"),
        "B1": ("707mm", "1000mm"),
        "B2": ("500mm", "707mm"),
        "B3": ("353mm", "500mm"),
        "B4": ("250mm", "353mm"),
        "B5": ("176mm", "250mm"),
        "B6": ("125mm", "176mm"),
        "B7": ("88mm", "125mm"),
        "B8": ("62mm", "88mm"),
        "B9": ("44mm", "62mm"),
        "B10": ("31mm", "44mm")
    }

    if format_Book.upper() in formats:
        page_Width, page_Height = formats[format_Book.upper()]

    else:
        match = re.fullmatch(r"(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)px", format_Book, flags=re.IGNORECASE)

        if not match:
            raise ValueError(f"Neplatný formát knihy: {format_Book}")

        page_Width = match.group(1)
        page_Height = match.group(2)

    DIR_IMAGES = os.path.join(DIR_TEMP, "Images")

    file_Cover = next(
        os.path.join(DIR_IMAGES, file)
        for file in os.listdir(DIR_IMAGES)
        if file.lower() in ["cover.png", "cover.jpg", "cover.jpeg"]
    )

    file_Background = next(
        (
            os.path.join(DIR_IMAGES, file)
            for file in os.listdir(DIR_IMAGES)
            if file.lower() in ["background.png", "background.jpg", "background.jpeg"]
        ),
        None
    )

    with Image.open(file_Cover) as image:
        file_Width, file_Height = image.size

    return (book, page_Width, page_Height, file_Cover, file_Background, file_Width, file_Height)


def load_Description(DIR_BASE):
    description_file = os.path.join(DIR_BASE, "description.md")

    if not os.path.exists(description_file):
        return {
            "title": "",
            "subtitle": "",
            "author": "",
            "series": "",
            "number": "",
            "rating": "",
            "tags": [],
            "identifier": "",
            "date": "",
            "published": "",
            "publisher": "",
            "language": "",
            "description": ""
        }

    text_Markdown = open(description_file, "r", encoding="utf-8").read()
    sections = {}
    current_section = None
    current_lines = []

    for line in text_Markdown.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)

        if match:
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()

            current_section = match.group(1).strip().lower()
            current_lines = []

            continue

        if current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(current_lines).strip()

    description_markdown = sections.get("description", "")
    description = markdown.markdown(description_markdown, extensions=["extra", "tables", "fenced_code"])

    return {
        "title": sections.get("title", ""),
        "subtitle": sections.get("subtitle", ""),
        "author": sections.get("author", ""),
        "series": sections.get("series", ""),
        "number": sections.get("number", ""),
        "rating": sections.get("rating", ""),
        "tags": sections.get("tags", ""),
        "identifier": sections.get("identifier", ""),
        "date": sections.get("date", ""),
        "published": sections.get("published", ""),
        "publisher": sections.get("publisher", ""),
        "language": sections.get("language", ""),
        "description": description
    }


def load_Markdown(DIR_PAGES):
    files = [
        file
        for file in os.listdir(DIR_PAGES)
        if file.lower().endswith(".md")
    ]

    def sort_key(file):
        name = os.path.splitext(file)[0].lower()
        match = re.match(r"chapter_(\d+)$", name)

        if match:
            return (0, int(match.group(1)))

        return (1, name)

    files.sort(key=sort_key)

    pages = []

    for file in files:
        text_Markdown = open(os.path.join(DIR_PAGES, file), "r", encoding="utf-8").read()

        pages.append((file, text_Markdown))

    return pages


def load_Metadata(directory):

    description_file = os.path.join(directory, "description.md")

    if not os.path.isfile(description_file):

        return {
            "title": "",
            "subtitle": "",
            "author": "",
            "series": "",
            "number": "",
            "rating": "",
            "tags": [],
            "identifier": "",
            "date": "",
            "published": "",
            "publisher": "",
            "language": "",
            "description": ""
        }

    with open(description_file, "r", encoding="utf-8") as source:
        markdown_text = source.read()

    sections = {}
    current_section = None
    current_lines = []

    for line in markdown_text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)

        if match:

            if current_section is not None:

                sections[current_section] = ("\n".join(current_lines).strip())

            current_section = (match.group(1).strip().lower())
            current_lines = []
            continue

        if current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        sections[current_section] = ("\n".join(current_lines).strip())

    tags = [
        tag.strip()
        for tag in sections.get("tags", "").split(",")
        if tag.strip()
    ]

    description = markdown.markdown(sections.get("description", ""),
        extensions=[
            "extra",
            "tables",
            "fenced_code"
        ]
    )

    return {
        "title": sections.get("title", ""),
        "subtitle": sections.get("subtitle", ""),
        "author": sections.get("author", ""),
        "series": sections.get("series", ""),
        "number": sections.get("number", ""),
        "rating": sections.get("rating", ""),
        "tags": tags,
        "identifier": sections.get("identifier", ""),
        "date": sections.get("date", ""),
        "published": sections.get("published", ""),
        "publisher": sections.get("publisher", ""),
        "language": sections.get("language", ""),
        "description": description
    }


def load_Settings(DIR_BASE):
    settings_file = os.path.join(DIR_BASE, "settings.md")

    if not os.path.exists(settings_file):
        return {
            "format": "",
            "type": "",
            "image_size": ""
        }

    text_Markdown = open(settings_file, "r", encoding="utf-8").read()
    sections = {}
    current_section = None
    current_lines = []

    for line in text_Markdown.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)

        if match:
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()

            current_section = match.group(1).strip().lower()
            current_lines = []

            continue

        if current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(current_lines).strip()

    return {
        "format": sections.get("format", ""),
        "type": sections.get("type", ""),
        "image_size": sections.get("image size", "")
    }


def load_Styles(document_name, DIR_STYLES):
    files = []

    for file in os.listdir(DIR_STYLES):
        if not file.lower().endswith(".css"):
            continue

        style_name = os.path.splitext(file)[0].lower()

        if not style_name.startswith("style_"):
            continue

        style_name = style_name[6:]

        if style_name in ["cover", "chapter"] and style_name != document_name:
            continue

        files.append(file)

    links = []

    for file in sorted(files):
        links.append(f'{"    " if links else ""}<link rel="stylesheet" type="text/css" href="../Styles/{file}" />')

    return "\n".join(links)


def load_Template(document_name, DIR_TEMPLATES):
    template_file = f"template_{document_name}.html"
    path = os.path.join(DIR_TEMPLATES, template_file)

    print(f"Načítám šablonu: {template_file}", flush=True)
    with open(path, "r", encoding="utf-8") as input:
        template = input.read()

    return template


def prepare_Folder(DIR_TEMP):
    if os.path.exists(DIR_TEMP):
        shutil.rmtree(DIR_TEMP)

    os.makedirs(os.path.join(DIR_TEMP, "Text"))
    os.makedirs(os.path.join(DIR_TEMP, "Styles"))
    os.makedirs(os.path.join(DIR_TEMP, "Fonts"))
    os.makedirs(os.path.join(DIR_TEMP, "Images"))
    os.makedirs(os.path.join(DIR_TEMP, "Misc"))


def remove_DS_Store(DIR_TEMP):
    for root, directories, files in os.walk(DIR_TEMP):
        for file in files:
            if file == ".DS_Store":
                os.remove(os.path.join(root, file))


def remove_Temp(DIR_TEMP):
    if os.path.exists(DIR_TEMP):
        shutil.rmtree(DIR_TEMP)


def select_Folder(title):
    if sys.platform == "darwin":
        script = f'''
            tell application "System Events"
                activate
                set selectedFolder to choose folder with prompt "{title}"
                return POSIX path of selectedFolder
            end tell
        '''

        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

        if result.returncode != 0:
            sys.exit()

        return result.stdout.strip()

    if sys.platform == "win32":
        script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $dialog.Description = "{title}"
            $dialog.ShowNewFolderButton = $true

            if ($dialog.ShowDialog() -eq "OK") {{
                Write-Output $dialog.SelectedPath
            }}
        '''

        result = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True)

        if result.returncode != 0 or not result.stdout.strip():
            sys.exit()

        return result.stdout.strip()

    raise RuntimeError(TEXTS[LANGUAGE]["error_Unsupported_Os"])


def set_Calibre_Rating(xmp, value):
    if not value or value.lower() == "none":
        return

    stars = value.count("*")

    if stars == 0:
        return

    rating = min(stars * 2, 10)

    namespace = "http://calibre-ebook.com/xmp-namespace"
    prefix = "calibre"
    description = xmp._get_or_create_description()
    description.setAttributeNS("http://www.w3.org/2000/xmlns/", f"xmlns:{prefix}", namespace)
    document = xmp.rdf_root.ownerDocument
    element = document.createElementNS(namespace, f"{prefix}:rating")

    element.appendChild(document.createTextNode(str(rating)))
    description.appendChild(element)
    xmp._update_stream()


def set_Calibre_Series(xmp, series, number):

    if not series or series.lower() == "none":
        return

    namespace = "http://calibre-ebook.com/xmp-namespace"
    series_index_namespace = ("http://calibre-ebook.com/xmp-namespace-series-index")
    description = xmp._get_or_create_description()

    description.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:calibre", namespace)
    description.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:calibreSI", series_index_namespace)

    document = xmp.rdf_root.ownerDocument

    series_element = document.createElementNS(namespace, "calibre:series")
    series_element.setAttributeNS("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:parseType", "Resource")
    value_element = document.createElementNS("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:value")

    value_element.appendChild(document.createTextNode(series))
    series_element.appendChild(value_element)

    if number and number.lower() != "none":
        number_element = document.createElementNS(series_index_namespace, "calibreSI:series_index")
        number_element.appendChild(document.createTextNode(number))
        series_element.appendChild(number_element)

    description.appendChild(series_element)
    xmp._update_stream()


def show_Message(message):
    if sys.platform == "darwin":
        icon_path = os.path.join(sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__)), "Bindery.icns")

        script = f'''
            tell application "System Events"
                activate
                display dialog "{message}" with title "Bindery" buttons {{"OK"}} default button "OK" with icon POSIX file "{icon_path}"
            end tell
        '''

        subprocess.run(["osascript", "-e", script])

    elif sys.platform == "win32":
        base_path = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "Bindery.ico")
        message = message.replace('"', '\\"')

        script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing

            $form = New-Object System.Windows.Forms.Form
            $form.Text = "Bindery"
            $form.StartPosition = "CenterScreen"
            $form.FormBorderStyle = "FixedDialog"
            $form.MaximizeBox = $false
            $form.MinimizeBox = $false
            $form.AutoSize = $true
            $form.AutoSizeMode = "GrowAndShrink"
            $form.Padding = New-Object System.Windows.Forms.Padding(25)

            $form.Icon = New-Object System.Drawing.Icon("{icon_path}")

            $label = New-Object System.Windows.Forms.Label
            $label.Text = "{message}"
            $label.AutoSize = $true
            $label.MaximumSize = New-Object System.Drawing.Size(500, 0)
            $label.Font = New-Object System.Drawing.Font("Segoe UI", 10)
            $label.Margin = New-Object System.Windows.Forms.Padding(0, 0, 0, 20)

            $button = New-Object System.Windows.Forms.Button
            $button.Text = "OK"
            $button.Width = 80
            $button.DialogResult = [System.Windows.Forms.DialogResult]::OK

            $panel = New-Object System.Windows.Forms.FlowLayoutPanel
            $panel.FlowDirection = "TopDown"
            $panel.AutoSize = $true
            $panel.WrapContents = $false
            $panel.Dock = "Fill"

            $panel.Controls.Add($label)
            $panel.Controls.Add($button)

            $form.Controls.Add($panel)
            $form.AcceptButton = $button

            $form.ShowDialog() | Out-Null
            $form.Dispose()
        '''

        subprocess.run(["powershell", "-NoProfile", "-Command", script])


def show_Notification(message):
    if sys.platform == "darwin":
        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "Bindery" sound name ""'])

    elif sys.platform == "win32":
        message = message.replace('"', '\\"')

        script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing

            $notify = New-Object System.Windows.Forms.NotifyIcon
            $notify.Icon = [System.Drawing.SystemIcons]::Information
            $notify.Visible = $true
            $notify.BalloonTipTitle = "Bindery"
            $notify.BalloonTipText = "{message}"
            $notify.ShowBalloonTip(5000)

            Start-Sleep -Seconds 5
            $notify.Dispose()
        '''

        subprocess.Popen(["powershell", "-NoProfile", "-Command", script])


def sync_Book(DIR_BASE, DIR_PAGES, type_Device):

    def sync(book_root):
        user_chapter_01 = os.path.join(DIR_PAGES, "chapter_01.md")
        has_user_chapter_01 = os.path.isfile(user_chapter_01)

        for root, directories, files in os.walk(book_root):

            relative_root = os.path.relpath(root, book_root)

            if relative_root == ".":
                user_root = DIR_BASE
            else:
                user_root = os.path.join(DIR_BASE, relative_root)

            os.makedirs(user_root, exist_ok=True)

            for file in files:
                if relative_root == "Pages":

                    name = os.path.splitext(file)[0].lower()

                    if has_user_chapter_01 and re.match(r"chapter_\d+$", name):
                        continue

                source = os.path.join(root, file)
                destination = os.path.join(user_root, file)

                if relative_root == "Images" and os.path.splitext(file)[0].lower() == "cover":

                    cover_exists = any(
                        os.path.splitext(existing)[0].lower() == "cover"
                        for existing in os.listdir(user_root)
                    )

                    if not cover_exists:
                        shutil.copy2(source, destination)

                else:

                    if not os.path.exists(destination):
                        shutil.copy2(source, destination)

    if type_Device == "desktop":

        if getattr(sys, "frozen", False):
            book_root = os.path.join(sys._MEIPASS, "Book")
        else:
            book_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Book")

        sync(book_root)

    else:
        url = "https://github.com/PepikVaio/macOS_Bindery/archive/refs/heads/main.zip"

        with tempfile.TemporaryDirectory() as temp_dir:

            zip_file = os.path.join(temp_dir, "Book.zip")
            extract_dir = os.path.join(temp_dir, "Extracted")

            print("", flush=True)
            print("Stahuji výchozí soubory z GitHubu...", flush=True)

            urllib.request.urlretrieve(url, zip_file)

            with zipfile.ZipFile(zip_file, "r") as archive:
                archive.extractall(extract_dir)

            book_root = os.path.join(extract_dir, "iPad_Test-main", "Book")

            if not os.path.isdir(book_root):
                raise FileNotFoundError("Ve staženém GitHub archivu nebyla nalezena složka Book.")

            sync(book_root)

if __name__ == "__main__":
    # Desktop: proměnná není nastavena -> zobrazí se výběr složky.
    # Web: Flask nastaví BINDERY_USER_DIR -> použije se tato složka.
    type_Device = "desktop" if not os.environ.get("BINDERY_USER_DIR") else "web"

    if type_Device == "desktop":
        from languages import INFO, TEXTS

        LANGUAGE = get_Language()
        DIR_BASE = select_Folder(TEXTS[LANGUAGE]["select_Folder"])
    else:
        DIR_BASE = os.environ["BINDERY_USER_DIR"]

    DIR_OUTPUT = DIR_BASE

    DIR_PAGES = os.path.join(DIR_BASE, "Pages")
    DIR_TEMP = os.path.join(DIR_BASE, "TEMP")
    DIR_STYLES = os.path.join(DIR_BASE, "Styles")
    DIR_TEMPLATES = os.path.join(DIR_BASE, "Templates")
    FILE_ERROR = os.path.join(DIR_BASE, "Bindery_Error.txt")

    if type_Device == "desktop":
        first_run = not os.path.isfile(os.path.join(DIR_BASE, "description.md"))

        if first_run:
            show_Message(INFO[LANGUAGE])

    sync_Book(DIR_BASE, DIR_PAGES, type_Device)

    if type_Device == "desktop":
        show_Notification(TEXTS[LANGUAGE]["info_Generating"])

    try:
        prepare_Folder(DIR_TEMP)
        copy_Files(DIR_BASE, DIR_TEMP)

        if type_Device == "desktop":
            settings = load_Settings(DIR_BASE)
            file_Format = "pdf"
            create_Html(DIR_PAGES, DIR_TEMP, DIR_STYLES, DIR_TEMPLATES)
            create_Css(DIR_PAGES, DIR_STYLES, DIR_TEMP)
            remove_DS_Store(DIR_TEMP)
            create_Pdf(DIR_OUTPUT, DIR_BASE, DIR_PAGES, DIR_TEMP)

            if not first_run and settings["type"].lower() == "book":
                file_Format = "epub"
                create_Html(DIR_PAGES, DIR_TEMP, DIR_STYLES, DIR_TEMPLATES)
                create_Css(DIR_PAGES, DIR_STYLES, DIR_TEMP)
                create_Cover(DIR_TEMP)
                remove_DS_Store(DIR_TEMP)
                create_Epub(DIR_OUTPUT, DIR_BASE, DIR_TEMP)

#            remove_Temp(DIR_TEMP)

        else:
            file_Format = os.environ.get("BINDERY_FORMAT", "pdf")
            
            create_Html(DIR_PAGES, DIR_TEMP, DIR_STYLES, DIR_TEMPLATES)
            create_Css(DIR_PAGES, DIR_STYLES, DIR_TEMP)

            if file_Format == "pdf":
                remove_DS_Store(DIR_TEMP)
                create_Pdf(DIR_OUTPUT, DIR_BASE, DIR_PAGES, DIR_TEMP)
            else:
                create_Cover(DIR_TEMP)
                remove_DS_Store(DIR_TEMP)
                create_Epub(DIR_OUTPUT, DIR_BASE, DIR_TEMP)

        if type_Device == "desktop":
            show_Notification(TEXTS[LANGUAGE]["info_Done"])

    except Exception as error:
        with open(FILE_ERROR, "w", encoding="utf-8") as output:
            output.write(repr(error))

        raise
