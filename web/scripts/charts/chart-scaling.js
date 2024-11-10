function getContainer() {
    return document.getElementById('visual-container');
}

export function autoFontSize() {
    let width = getContainer().offsetWidth;
    return Math.min(Math.max(6, Math.round(width / 80)), 16);
}

export function autoWidth() {
    let width = getContainer().offsetWidth;
    return Math.max(50, Math.round(width / 10));
}
