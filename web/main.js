import "./style.scss";
import {Dropzone} from "dropzone";

const UPLOAD_URL = "/api/upload"

const switchView = (oldId, newId) => {
    document.getElementById(newId).style.display = "flex";
    document.getElementById(oldId).style.display = "none";
}

const init = () => {
    setTimeout(() => switchView('view-init', 'view-classification'), 1000)
    const dropzone = new Dropzone("#upload-dropzone", { url: UPLOAD_URL });

}

document.addEventListener("DOMContentLoaded", init);