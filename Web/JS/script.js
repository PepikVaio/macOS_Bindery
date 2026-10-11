//  ╭─ INFO ──────────────────────────────────────────────────────────────────────────╮
//  │ This is the code of the web page of Bindery. It runs in the browser.            │
//  │                                                                                 │
//  │ What it does:                                                                   │
//  │  - It lets the user choose a book folder, or load the Bindery guide.            │
//  │  - It sends the files to the server (flask_app.py) one by one.                  │
//  │  - It shows the preview pages, the book information, and the number of files.   │
//  │  - It shows the status of every step (waiting, uploading, ready, error).        │
//  │  - It downloads the PDF or EPUB file when the user clicks the button.           │
//  │  - It changes the language of the page (CS and EN) with the texts from i18n.js. │
//  │                                                                                 │
//  │ This file needs:                                                                │
//  │  - index.html (the buttons and texts with these ids and data-i18n keys)         │
//  │  - i18n.js (the translations, it must load BEFORE this file)                    │
//  │  - flask_app.py on the server (it answers the requests)                         │
//  ╰─────────────────────────────────────────────────────────────────────────────────╯


//     __   __        _      _    _        
//     \ \ / /_ _ _ _(_)__ _| |__| |___ ___
//      \ V / _` | '_| / _` | '_ \ / -_|_-<
//       \_/\__,_|_| |_\__,_|_.__/_\___/__/
//                                         

let lang_Current = localStorage.getItem("lang_Bindery") || "en";
let files_Last = null;
let index_Preview = 0;
let pages_Previews = [];
let type_Book = null;
let upload_Finished = false;

const toggle_Lang = document.getElementById("toggle_Lang");

const input_Folder = document.getElementById("input_Folder");
const button_Folder = document.getElementById("button_Folder");
const status_Indicator = document.getElementById("status_Indicator");
const status_Text = document.getElementById("status_Text");

const container_Cover = document.getElementById("container_Cover");
const text_Placeholder_Sidebar = document.getElementById("text_Placeholder_Sidebar");
const image_Cover = document.getElementById("image_Cover");
const pages_Preview = document.getElementById("pages_Preview");
const button_Previous = document.getElementById("button_Previous");
const button_Next = document.getElementById("button_Next");

const metadata_01 = document.getElementById("metadata_01");
const metadata_02 = document.getElementById("metadata_02");
const metadata_03 = document.getElementById("metadata_03");
const metadata_04 = document.getElementById("metadata_04");
const metadata_05 = document.getElementById("metadata_05");
const metadata_06 = document.getElementById("metadata_06");
const metadata_07 = document.getElementById("metadata_07");
const metadata_08 = document.getElementById("metadata_08");
const metadata_09 = document.getElementById("metadata_09");
const metadata_10 = document.getElementById("metadata_10");
const metadata_11 = document.getElementById("metadata_11");
const metadata_12 = document.getElementById("metadata_12");

const button_Generate_EpubButton = document.getElementById("button_Generate_Epub");
const button_Generate_PdfButton = document.getElementById("button_Generate_Pdf");
const button_Load_Guide = document.getElementById("button_Load_Guide");


//      ___             _   _             
//     | __|  _ _ _  __| |_(_)___ _ _  ___
//     | _| || | ' \/ _|  _| / _ \ ' \(_-<
//     |_| \_,_|_||_\__|\__|_\___/_||_/__/
//                                        

function enabled_Preview() {

    if (pages_Previews.length) {

        show_Pages_Preview(index_Preview);
        container_Cover.classList.remove("lock_Preview");

    } else {

        button_Next.disabled = true;
        button_Previous.disabled = true;
        container_Cover.classList.add("lock_Preview");
    }
}

async function generate_Book(format) {

    if (!upload_Finished) {
        return;
    }

    toogle_Controls_Disabled(true);
    container_Cover.classList.add("lock_Preview");

    const is_Pdf = format === "pdf";

    set_Status(is_Pdf ? "text_Sidebar_Status_08" : "text_Sidebar_Status_12", "blue");

    try {
        const response = await fetch("/generate",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ format: format })
            }
        );

        if (!response.ok) {
            throw new Error(await response.text());
        }

        set_Status(is_Pdf ? "text_Sidebar_Status_09" : "text_Sidebar_Status_13", "blue");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        const disposition = response.headers.get("Content-Disposition");
        let downloadName = is_Pdf ? "Bindery.pdf" : "Bindery.epub";

        if (disposition) {
            const match = disposition.match(/filename="?([^";]+)"?/);

            if (match) {
                downloadName = match[1];
            }
        }

        link.href = url;
        link.download = downloadName;

        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        set_Status(is_Pdf ? "text_Sidebar_Status_10" : "text_Sidebar_Status_14", "green");

    } catch (error) {
        set_Status(is_Pdf ? "text_Sidebar_Status_11" : "text_Sidebar_Status_15", "red");
    } finally {
        toogle_Controls_Disabled(false);
        enabled_Preview();
    }
}

function get_Translate(key, format, progress) {

    const language = I18N[lang_Current] || {};
    let text = language[key] || key;

    if (format) {
        text = text.replace("{format}", format);
    }

    if (progress !== undefined && progress !== null) {
        text = text.replace("{progress}", progress);
    }

    return text;
}

async function load_Book(files = null) {
    reset_View();

    type_Book = files ? null : "guide";

    toogle_Controls_Disabled(true);
    upload_Finished = false;

    if (files) {
        update_Files(files);
    } else {
        reset_FIles();
    }

    set_Status("text_Sidebar_Status_03", "blue");

    try {

        const startResponse = await fetch("/start_upload",
            { method: "POST" }
        );

        if (!startResponse.ok) {
            let serverText = "";

            try {
                serverText = (await startResponse.text()).slice(0, 300);
            } catch (e) {}

            throw new Error(
                "Nepodařilo se připravit knihu (/start_upload, HTTP " +
                startResponse.status +
                "). " +
                serverText
            );
        }

        if (files) {

            for (let i = 0; i < files.length; i++) {

                const file = files[i];
                const formData = new FormData();

                formData.append("file", file);

                const pathParts = (
                    file.webkitRelativePath ||
                    file.name
                ).split("/");

                formData.append(
                    "relative_path",
                    pathParts.slice(1).join("/")
                );

                const response = await fetch(
                    "/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );

                if (!response.ok) {
                    throw new Error("Nepodařilo se nahrát soubor.");
                }

                set_Status(
                    "text_Sidebar_Status_02",
                    "blue",
                    null,
                    `${i + 1} / ${files.length}`
                );
            }
        }

        set_Status("text_Sidebar_Status_04", "blue");

        const previewResponse = await fetch("/preview_cover");

        if (!previewResponse.ok) {

            let serverText = "";

            try {
                serverText = (await previewResponse.text()).slice(0, 300);
            } catch (e) {}

            throw new Error(
                "Nepodařilo se vytvořit náhled (/preview_cover, HTTP " +
                previewResponse.status +
                "). " +
                serverText
            );
        }

        const previewData = await previewResponse.json();

        if (
            !previewData.success ||
            !previewData.pages ||
            !previewData.pages.length
        ) {
            throw new Error("Náhled knihy nebyl vytvořen.");
        }

        pages_Previews = previewData.pages || [];
        index_Preview = 0;

        if (!pages_Previews.length) {
            throw new Error("Náhled knihy je prázdný.");
        }

        show_Pages_Preview(0);

        button_Previous.disabled = true;
        button_Next.disabled = true;

        set_Status("text_Sidebar_Status_05", "blue");

        try {
            await load_Metadata();
        } catch (metadataError) {
            console.error(metadataError);
        }

        upload_Finished = true;

        set_Status("text_Sidebar_Status_06", "green");

        button_Generate_PdfButton.disabled = false;
        button_Generate_EpubButton.disabled = type_Book !== "book";

    } catch (error) {

        set_Status("text_Sidebar_Status_07", "red");

        const errorMessage = error && error.message ? error.message : String(error);

        status_Text.textContent += " " + errorMessage;

        let tree = "";

        try {
            const debugResponse = await fetch("/debug_book");

            tree = await debugResponse.text();

        } catch (debugError) {
            tree = "(výpis /debug_book se nepodařilo načíst)";
        }

        alert(status_Text.textContent + "\n\n" + tree);

        button_Generate_PdfButton.disabled = true;
        button_Generate_EpubButton.disabled = true;

    } finally {

        toogle_Controls_Disabled(false);

        if (!upload_Finished) {
            button_Generate_PdfButton.disabled = true;
            button_Generate_EpubButton.disabled = true;
        }

        enabled_Preview();

        input_Folder.value = "";
    }
}

async function load_Metadata() {

    const response = await fetch("/metadata");

    if (!response.ok) {
        throw new Error("Nepodařilo se načíst metadata knihy.");
    }

    const data = await response.json();

    if (type_Book !== "guide") {
        type_Book = data.type?.toLowerCase() || null;
    }

    set_Metadata(data);
}

function reset_FIles() {

    document.querySelectorAll("#files_Own > div span:nth-child(2)").forEach(function (count) {
        count.textContent = "0";
    });
}

function reset_View() {

    files_Last = null;

    set_Metadata_Text(metadata_01, "", "text_Main_Title_01");
    set_Metadata_Text(metadata_02, "", "text_Main_Subtitle_01");
    set_Metadata_Text(metadata_03, "", "text_Main_Subtitle_02");

    metadata_07.textContent = "–";
    metadata_09.textContent = "–";
    metadata_05.textContent = "–";
    metadata_08.textContent = "–";
    metadata_10.textContent = "–";
    metadata_06.textContent = "–";
    metadata_04.textContent = "–";
    metadata_11.textContent = "–";

    metadata_12.dataset.i18n = "text_Main_Placeholder";
    metadata_12.textContent = get_Translate("text_Main_Placeholder");
    metadata_12.classList.add("placeholder-text");

    pages_Previews = [];
    index_Preview = 0;

    container_Cover.classList.add("lock_Preview");

    image_Cover.style.display = "none";
    image_Cover.removeAttribute("src");
    text_Placeholder_Sidebar.style.display = "block";
    pages_Preview.textContent = "0 / 0";
    button_Previous.disabled = true;
    button_Next.disabled = true;
}

function set_Language(lang) {

    if (!I18N[lang]) {
        return;
    }

    lang_Current = lang;
    localStorage.setItem("lang_Bindery", lang);
    document.documentElement.lang = lang;

    document.querySelectorAll(".lang-option").forEach(function (button) {
        button.classList.toggle("active", button.dataset.lang === lang);
    });

    document.querySelectorAll("[data-i18n]").forEach(function (element) {
        element.textContent = get_Translate(
            element.dataset.i18n,
            element.dataset.i18nFormat,
            element.dataset.i18nProgress
        );
    });

    if (files_Last) {
        update_Files(files_Last);
    }
}

function set_Metadata(data) {

    set_Metadata_Text(metadata_01, data.title, "text_Main_Title_01");
    set_Metadata_Text(metadata_02, data.subtitle, "text_Main_Subtitle_01");

    set_Metadata_Text(metadata_03, data.author ? get_Translate("text_Main_Subtitle_Prefix") + data.author : "", "text_Main_Subtitle_02");

    metadata_07.textContent = data.identifier || "–";
    metadata_09.textContent = data.language || "–";
    metadata_05.textContent = data.number || "–";
    metadata_08.textContent = data.published || "–";
    metadata_10.textContent = data.publisher || "–";
    metadata_06.textContent = data.rating ? String(data.rating) : "–";
    metadata_04.textContent = data.series || "–";
    metadata_11.textContent = data.tags?.length ? data.tags.join(", ") : "–";

    metadata_12.classList.remove("placeholder-text");
    metadata_12.removeAttribute("data-i18n");
    metadata_12.innerHTML = data.description || "";
}

function set_Metadata_Text(element, value, placeholderKey) {

    if (value) {

        element.textContent = value;
        element.classList.remove("placeholder-text");
        element.removeAttribute("data-i18n");

    } else {

        element.dataset.i18n = placeholderKey;
        element.textContent = get_Translate(placeholderKey);
        element.classList.add("placeholder-text");
    }
}

function set_Status(key, type, format, progress) {

    status_Text.dataset.i18n = key;

    if (format) {
        status_Text.dataset.i18nFormat = format;
    } else {
        delete status_Text.dataset.i18nFormat;
    }

    if (progress !== undefined && progress !== null) {
        status_Text.dataset.i18nProgress = progress;
    } else {
        delete status_Text.dataset.i18nProgress;
    }

    status_Text.textContent = get_Translate(key, format, progress);

    status_Indicator.classList.remove("blue", "green", "red");

    if (type) {
        status_Indicator.classList.add(type);
    }
}

function show_Pages_Preview(index) {

    if (!pages_Previews.length) {
        return;
    }

    index_Preview = Math.max(0, Math.min(index, pages_Previews.length - 1));

    const page = pages_Previews[index_Preview];

    image_Cover.src = "/preview_page/" + page + "?v=" + Date.now();
    image_Cover.style.display = "block";
    text_Placeholder_Sidebar.style.display = "none";
    pages_Preview.textContent = (index_Preview + 1) + " / " + pages_Previews.length;
    button_Previous.disabled = index_Preview === 0;
    button_Next.disabled = index_Preview === pages_Previews.length - 1;

    if (index_Preview + 1 < pages_Previews.length) {

        const preload = new Image();

        preload.src =
            "/preview_page/" +
            pages_Previews[index_Preview + 1] +
            "?v=" +
            Date.now();
    }
}

function toogle_Controls_Disabled(disabled) {

    button_Folder.disabled = disabled;
    button_Generate_EpubButton.disabled = disabled || type_Book !== "book";
    button_Generate_PdfButton.disabled = disabled || !upload_Finished;
    button_Load_Guide.disabled = disabled;
    button_Next.disabled = disabled;
    button_Previous.disabled = disabled;

    document.querySelectorAll(".lang-option").forEach(function (button) {
        button.disabled = disabled;
    });
}

function update_Files(files) {

    files_Last = files;

    const folderCounts = {
        Fonts: 0,
        Images: 0,
        Misc: 0,
        Other: 0,
        Pages: 0,
        Styles: 0,
        Templates: 0,
        Text: 0
    };

    for (const file of files) {

        const path = file.webkitRelativePath || file.name;
        const parts = path.split("/");
        const topFolder = parts.length > 2 ? parts[1] : null;

        if (!topFolder) {
            folderCounts.Other++;
            continue;
        }

        const folder = Object.keys(folderCounts).find(
            name => name.toLowerCase() === topFolder.toLowerCase()
        );

        if (folder) {
            folderCounts[folder]++;
        } else {
            folderCounts.Other++;
        }
    }

    document.querySelectorAll("#files_Own > div").forEach(function (row) {

        const folder = row.querySelector("span").textContent;

        row.querySelector("span:nth-child(2)").textContent =
            folderCounts[folder] || 0;
    });
}


//      ___      _   _               
//     | _ )_  _| |_| |_ ___ _ _  ___
//     | _ \ || |  _|  _/ _ \ ' \(_-<
//     |___/\_,_|\__|\__\___/_||_/__/
//                                   

toggle_Lang.addEventListener("click", function (event) {

    const button = event.target.closest(".lang-option");

    if (button && !button.disabled) {
        set_Language(button.dataset.lang);
    }
});

input_Folder.addEventListener("change", async function () {

    const files = Array.from(input_Folder.files);

    if (!files.length) {

        set_Status("text_Sidebar_Status_16", "red");

        return;
    }

    await load_Book(files);
});

button_Folder.addEventListener("click", function () {
    input_Folder.click();
});

button_Previous.addEventListener("click", function () {
    show_Pages_Preview(index_Preview - 1);
});

button_Next.addEventListener("click", function () {
    show_Pages_Preview(index_Preview + 1);
});

button_Generate_EpubButton.addEventListener("click", function () {
    generate_Book("epub");
});

button_Generate_PdfButton.addEventListener("click", function () {
    generate_Book("pdf");
});

button_Load_Guide.addEventListener("click", async function () {
    await load_Book();
});


//      ___ _            _   
//     / __| |_ __ _ _ _| |_ 
//     \__ \  _/ _` | '_|  _|
//     |___/\__\__,_|_|  \__|
//                           

set_Language(lang_Current);
reset_FIles();
