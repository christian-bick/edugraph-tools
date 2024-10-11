import "./style.scss";

const switchView = (oldId, newId) => {
    document.getElementById(newId).style.display = "flex";
    document.getElementById(oldId).style.display = "none";
}

const init = () => {
    setTimeout(() => switchView('view-init', 'view-credentials'), 1000)
}

document.addEventListener("DOMContentLoaded", init);