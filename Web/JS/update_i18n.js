// ╭─ INFO ───────────────────────────────────────────────────────────────────────────────────────────────╮
// │ This script updates the translations of Bindery in one step.                                         │
// │ It finds all data-i18n keys in the HTML files.                                                       │
// │ It saves them in ONE Markdown file (one block for each key).                                         │
// │ Each block has: the main language, English, and then the other languages (A to Z).                   │
// │ Then it makes the file i18n.js for the web app.                                                      │
// │ You can translate the Markdown file by hand or with AI. The web app does not read it.                │
// │ If a translation is missing, i18n.js uses English. If English is missing, it uses the main language. │
// ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯


//     __   __        _      _    _        
//     \ \ / /_ _ _ _(_)__ _| |__| |___ ___
//      \ V / _` | '_| / _` | '_ \ / -_|_-<
//       \_/\__,_|_| |_\__,_|_.__/_\___/__/
//                                         

const fs = require('fs');
const path = require('path');

const CONFIG = {
    // Main language and all languages
    // (if you remove a language from the list, it is removed from the Markdown file at the next update)
    LANG_MAIN: 'cs',
    LANGS: ['cs', 'en'],

    // Main folder (the script looks for HTML files here) and the folder for translations
    DIR_MAIN: path.resolve(__dirname, '../../'),
    DIR_I18N: path.resolve(__dirname, '../i18n'),

    // File type of the HTML files
    EXT_HTML: '.html',

    // The ONE Markdown file with translations and the new i18n.js file for the web app
    PATH_MARKDOWN: path.resolve(__dirname, '../i18n/i18n.md'),
    PATH_OUTPUT: path.resolve(__dirname, 'i18n.js')
};

const { LANG_MAIN, LANGS, DIR_MAIN, DIR_I18N, EXT_HTML, PATH_MARKDOWN, PATH_OUTPUT } = CONFIG;


//      ___             _   _             
//     | __|  _ _ _  __| |_(_)___ _ _  ___
//     | _| || | ' \/ _|  _| / _ \ ' \(_-<
//     |_| \_,_|_||_\__|\__|_\___/_||_/__/
//                                        

// Make the text of the Markdown file
function create_Markdown(entries, data, order) {
    const result = [];

    result.push('# i18n');
    result.push('');
    result.push('```');
    result.push('╭─ Info ─────────────────────────────────────────────────────────────────────────────────╮');
    result.push('│ Change the word MISSING to your translation.                                           │');
    result.push('│ Do not change the words in curly brackets, for example {format} and {progress}.        │');
    result.push('│ After you save this file, type this in the Terminal: node ${path.basename(__filename)} │');
    result.push('│ Then the web app shows your changes (the file ${path.basename(PATH_OUTPUT)} is made).  │');
    result.push('╰────────────────────────────────────────────────────────────────────────────────────────╯');
    result.push('```');
    result.push('');

    const dirMarkdown = path.dirname(PATH_MARKDOWN);

    for (const fileEntry of entries) {
        const linkPath = path.relative(dirMarkdown, path.join(DIR_MAIN, fileEntry.file)).split(path.sep).join('/');

        result.push(`### [${fileEntry.file}](${linkPath})`);
        result.push('');

        for (const item of fileEntry.keys) {
            result.push(`> line: \`${item.line}\``);
            result.push(`> data-i18n: \`${item.key}\``);

            for (const lang of order) {
                result.push(`  - ${lang}: \`${data[item.key][lang]}\``);
            }

            result.push('');
        }
    }

    return result.join('\n');
}

// Make the text of the i18n.js file
function create_Output(data, order) {
    const keys = Object.keys(data);
    const output = [];


    output.push('// ╭─ Info ───────────────────────────╮');
    output.push('// │ This file is made automatically. │');
    output.push('// │ Do not edit it by hand.          │');
    output.push('// │ Use `node update_i18n.js`.       │');
    output.push('// ╰──────────────────────────────────╯');
    output.push('');
    output.push('const I18N = {');

    order.forEach((lang, langIndex) => {
        output.push(`  ${JSON.stringify(lang)}: {`);

        let previousPrefix = '';

        keys.forEach((key, index) => {
            const prefix = key.split(/[_.]/)[0];

            // Put an empty line between groups of keys
            if (previousPrefix !== '' && prefix !== previousPrefix) {
                output.push('');
            }

            const comma = index < keys.length - 1 ? ',' : '';

            output.push(`    ${JSON.stringify(key)}: ${JSON.stringify(get_Text(data[key], lang))}${comma}`);

            previousPrefix = prefix;
        });

        output.push(`  }${langIndex < order.length - 1 ? ',' : ''}`);

        if (langIndex < order.length - 1) {
            output.push('');
        }
    });

    output.push('};');

    return output.join('\n') + '\n';
}

// Collect the keys of all HTML files
// Result: [{ file: 'index.html', keys: [{ key, line }, ...] }, ...]
function get_Entries() {
    const result = [];
    const usedKeys = new Set();

    for (const filePath of get_Files_HTML(DIR_MAIN)) {
        const file = path.relative(DIR_MAIN, filePath).split(path.sep).join('/');
        const keys = [];

        for (const item of get_Texts_HTML(filePath)) {

            // Every key can be used only one time
            if (usedKeys.has(item.key)) {
                console.warn(`Warning: the key "${item.key}" is used two times (file: ${file}). The second one is skipped.`);
                continue;
            }

            usedKeys.add(item.key);
            keys.push(item);
        }

        if (keys.length > 0) {
            result.push({ file, keys });
        }
    }

    return result;
}

// Find all HTML files in a folder and in its subfolders (skip node_modules and the i18n folder)
function get_Files_HTML(dir) {
    const result = [];

    const items = fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));

    for (const item of items) {
        const fullPath = path.join(dir, item.name);

        if (item.name === 'node_modules' || fullPath === DIR_I18N) {
            continue;
        }

        if (item.isDirectory()) {
            result.push(...get_Files_HTML(fullPath));
        } else if (item.isFile() && path.extname(item.name).toLowerCase() === EXT_HTML) {
            result.push(fullPath);
        }
    }

    return result;
}

// Order of languages: main language, then English (if it is not the main language), then the others (A to Z)
function get_LangOrder() {
    const langs = [...new Set(LANGS)];
    const second = LANG_MAIN !== 'en' && langs.includes('en') ? ['en'] : [];
    const others = langs.filter((lang) => lang !== LANG_MAIN && lang !== 'en').sort((a, b) => a.localeCompare(b));

    return [LANG_MAIN, ...second, ...others];
}

// Text for i18n.js: the own text first, then English, then the main language
function get_Text(entry, lang) {

    for (const value of [entry[lang], entry.en, entry[LANG_MAIN]]) {

        if (!is_Missing(value)) {
            return value;
        }

    }

    return 'MISSING';
}

// Find all data-i18n keys in one HTML file and save the line number of each key
function get_Texts_HTML(filePath) {
    const html = fs.readFileSync(filePath, 'utf8');
    const regex = /\bdata-i18n\s*=\s*["']([^"']+)["']/g;
    const result = [];

    let match;

    while ((match = regex.exec(html)) !== null) {
        result.push({
            key: match[1],
            line: html.slice(0, match.index).split('\n').length
        });
    }

    return result;
}

// One-time import of the old files (cs.md, en.md, de.md ...) if the new file does not exist yet
function import_Files_Old() {
    const result = {};

    for (const lang of LANGS) {
        const data = read_File(path.join(DIR_I18N, `${lang}.md`));

        let currentKey = '';

        for (const rawLine of data.split(/\r?\n/)) {
            const line = rawLine.trim();

            const keyMatch = line.match(/^>\s*([^:\s]+):\s*$/);

            if (keyMatch) {
                currentKey = keyMatch[1];
                continue;
            }

            const textMatch = line.match(/^-\s*([^:]+):\s*`(.*)`$/);

            if (!textMatch) {
                continue;
            }

            const name = textMatch[1].trim();

            if (lang === LANG_MAIN) {
                // Old main file: "- key: `text`"
                result[name] = result[name] || {};
                result[name][lang] = textMatch[2];
            } else if (currentKey && name === lang) {
                // Old language file: "> key:" and below it "- language: `text`"
                result[currentKey] = result[currentKey] || {};
                result[currentKey][lang] = textMatch[2];
            }
        }
    }

    return result;
}

// A translation is missing if it is not text, if it is "MISSING", or if it starts with "["
function is_Missing(value) {
    return (typeof value !== 'string' || value === 'MISSING' || value.startsWith('['));
}

// Load the keys from the HTML files and the old translations
function load_Data() {

    if (!LANGS.includes(LANG_MAIN)) {
        throw new Error(`The main language "${LANG_MAIN}" is not in the list of languages.`);
    }

    const order = get_LangOrder();
    const entries = get_Entries();

    // Old translations: from the new file, or from the old files at the first run
    const isFirstRun = !fs.existsSync(PATH_MARKDOWN);

    const old = isFirstRun ? import_Files_Old() : parse_Markdown(read_File(PATH_MARKDOWN));

    // All keys from the HTML files, all languages. What is missing gets "MISSING".
    const data = {};

    for (const fileEntry of entries) {

        for (const item of fileEntry.keys) {
            data[item.key] = {};

            for (const lang of order) {
                const value = old[item.key] && old[item.key][lang];

                data[item.key][lang] = typeof value === 'string' ? value : 'MISSING';
            }

        }

    }

    return { order, entries, data, old, isFirstRun };
}

// Read the Markdown file. Result: { key: { language: text } }
function parse_Markdown(data) {
    const result = {};

    let currentKey = '';

    for (const rawLine of String(data ?? '').split(/\r?\n/)) {
        const line = rawLine.trim();

        const keyMatch = line.match(/^>\s*data-i18n:\s*`?([^`]+?)`?\s*$/);

        if (keyMatch) {
            currentKey = keyMatch[1].trim();
            result[currentKey] = result[currentKey] || {};
            continue;
        }

        // A new "line:" or a heading ends the last key
        if (/^(>\s*line:|#)/.test(line)) {
            currentKey = '';
            continue;
        }

        const langMatch = line.match(/^-\s*([A-Za-z][\w-]*):\s*`(.*)`$/);

        if (langMatch && currentKey) {
            result[currentKey][langMatch[1]] = langMatch[2];
        }
    }

    return result;
}

// Read a file. If the file does not exist, return an empty text.
function read_File(filePath) {
    return fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8') : '';
}

// Save both files: the Markdown file and i18n.js
function save_Data(entries, data, order) {
    write_File(PATH_MARKDOWN, create_Markdown(entries, data, order));
    write_File(PATH_OUTPUT, create_Output(data, order));
}

// Run the update and show the result in the console
function update_I18n() {
    const { order, entries, data, old, isFirstRun } = load_Data();

    save_Data(entries, data, order);

    const keys = Object.keys(data);

    console.log('');
    console.log(`Main language: ${LANG_MAIN}`);
    console.log(`Texts found: ${keys.length}`);

    if (isFirstRun && Object.keys(old).length > 0) {
        console.log(`The translations came from the old files in ${DIR_I18N}. You can delete the old files now.`);
    }

    console.log('');
    console.log('Missing translations:');

    for (const lang of order) {
        const missing = keys.filter((key) => is_Missing(data[key][lang])).length;

        console.log(`  ${lang}: ${missing}`);
    }

    console.log('');
    console.log(`Done. These files are ready: ${path.basename(PATH_MARKDOWN)} and ${path.basename(PATH_OUTPUT)}`);
}

// Write a file. Make the folder first if it does not exist.
function write_File(filePath, content) {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, content, 'utf8');
}


//      ___ _            _   
//     / __| |_ __ _ _ _| |_ 
//     \__ \  _/ _` | '_|  _|
//     |___/\__\__,_|_|  \__|
//                           

console.log('');
console.log('========================================');
console.log('  Bindery - Translation update'          );
console.log('========================================');
console.log('This updates the translation file and makes the file i18n.js for the web app.');

try {
    update_I18n();
} catch (error) {
    console.error('');
    console.error('ERROR: The translation update did not work.');
    console.error(error.message);
    process.exit(1);
}