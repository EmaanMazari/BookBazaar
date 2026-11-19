const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const marked = require('./marked.min.js');

const CHROME_PATH = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';
const WORKSPACE = 'C:\\Users\\Microsoft\\Desktop\\fypfinal';
const ARTIFACT_DIR = 'C:\\Users\\Microsoft\\.gemini\\antigravity\\brain\\1ac430bc-e982-491a-8e92-1681315c87b0';

const CSS = `
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {
        content: counter(page);
    }
}

body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.55;
    color: #1e293b;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4, h5 {
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.4em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h1 {
    font-size: 20pt;
    color: #064e3b;
    border-bottom: 2px solid #059669;
    padding-bottom: 4px;
    margin-top: 1.8em;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
    margin-top: 0;
}

h2 {
    font-size: 14pt;
    color: #047857;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3px;
}

h3 {
    font-size: 12pt;
    color: #0f172a;
}

h4 {
    font-size: 11pt;
}

p, ul, ol {
    margin-top: 0.4em;
    margin-bottom: 0.7em;
}

ul, ol {
    padding-left: 20px;
}

li {
    margin-bottom: 0.25em;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #cbd5e1;
    padding: 6px 10px;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    background-color: #f1f5f9;
    color: #0f766e;
    padding: 1px 4px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}

pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 12px 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.45;
    margin: 0.8em 0;
    page-break-inside: avoid;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
}

blockquote {
    border-left: 4px solid #059669;
    background-color: #ecfdf5;
    margin: 0.8em 0;
    padding: 8px 14px;
    color: #065f46;
    border-radius: 0 6px 6px 0;
    font-size: 10pt;
}

hr {
    border: 0;
    height: 1px;
    background-color: #cbd5e1;
    margin: 1.5em 0;
}

.cover-header {
    text-align: center;
    padding: 40px 20px 20px 20px;
    page-break-after: always;
}

.cover-header h1 {
    border: none;
    font-size: 26pt;
    color: #064e3b;
    margin-bottom: 8px;
}

.cover-header h2 {
    border: none;
    font-size: 16pt;
    color: #334155;
    font-weight: 500;
}

.cover-meta {
    margin-top: 50px;
    font-size: 11pt;
    line-height: 1.8;
}

.tag-badge {
    display: inline-block;
    background-color: #d1fae5;
    color: #065f46;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 10pt;
    margin-bottom: 15px;
}
`;

function buildHtmlDocument(title, markdownContent) {
    const rawHtml = marked.parse(markdownContent);
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>${title}</title>
    <style>${CSS}</style>
</head>
<body>
    ${rawHtml}
</body>
</html>`;
}

function convertMdToPdf(mdFilename, pdfFilename, title) {
    const mdPath = path.join(WORKSPACE, mdFilename);
    const htmlFilename = mdFilename.replace('.md', '.html');
    const htmlPath = path.join(WORKSPACE, htmlFilename);
    const pdfPath = path.join(WORKSPACE, pdfFilename);

    console.log(`Reading ${mdFilename}...`);
    const content = fs.readFileSync(mdPath, 'utf8');

    console.log(`Generating HTML ${htmlFilename}...`);
    const html = buildHtmlDocument(title, content);
    fs.writeFileSync(htmlPath, html, 'utf8');

    console.log(`Printing to PDF via Chrome Headless -> ${pdfFilename}...`);
    const cmd = `"${CHROME_PATH}" --headless=new --disable-gpu --run-all-compositor-stages-before-draw --print-to-pdf="${pdfPath}" "${htmlPath}"`;
    execSync(cmd, { stdio: 'inherit' });

    if (fs.existsSync(pdfPath)) {
        const stats = fs.statSync(pdfPath);
        console.log(`[SUCCESS] Created ${pdfFilename} (${(stats.size / 1024).toFixed(1)} KB)`);

        // Copy to artifact directory
        const artifactPdfPath = path.join(ARTIFACT_DIR, pdfFilename);
        fs.copyFileSync(pdfPath, artifactPdfPath);
        console.log(`[COPIED] ${pdfFilename} copied to artifacts directory.`);
    } else {
        console.error(`[ERROR] Failed to create ${pdfFilename}`);
    }
}

console.log("=== STARTING PDF GENERATION FOR BOOKBAZAAR SRS & SDD ===");
convertMdToPdf('BookBazaar_SRS_v2.0.md', 'BookBazaar_SRS_v2.0.pdf', 'BookBazaar SRS v2.0 - Software Requirements Specification');
convertMdToPdf('BookBazaar_SDD_v2.0.md', 'BookBazaar_SDD_v2.0.pdf', 'BookBazaar SDD v2.0 - Software Design Document');
console.log("=== PDF GENERATION COMPLETE! ===");
