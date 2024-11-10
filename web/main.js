import "./style.scss";
import * as echarts from 'echarts';
import {initExampleUpload, initFileUpload} from "./scripts/file-upload.js";
import initChartNavigation from "./scripts/chart-navigation.js";

const API_URL = import.meta.env.PROD ? "https://edu-graph-api-575953891979.europe-west3.run.app" : "http://localhost:8080"

const UPLOAD_URL = `${API_URL}/classify`
const ONTOLOGY_URL = `${API_URL}/ontology`

let onto;

let viewInit;
let viewClassification;
let viewUploadStart;
let viewUploadProgress;
let viewClassificationResult;
let viewClassificationInput;
let viewUploadError;

let filePreview;
let filePreviewMore;

function switchView(oldEl, newEl) {
    activateView(newEl);
    deactivateView(oldEl);
}

function activateView(el) {
    el.style.display = 'flex';
}

function deactivateView(el) {
    el.style.display = 'none';
}

function init() {
    viewInit = document.getElementById('view-init')
    viewClassification = document.getElementById('view-classification')
    viewClassificationResult = document.getElementById('view-classification-result');

    viewUploadStart = document.getElementById('view-upload-start');
    viewUploadProgress = document.getElementById('view-upload-progress');
    viewUploadError = document.getElementById('view-upload-error');
    viewClassificationInput = document.getElementById('view-classification-input');

    filePreview = document.getElementById('file-preview');
    filePreviewMore = document.getElementById('file-preview-more');
    filePreviewMore.onclick = () => {
        switchView(viewClassificationResult, viewClassificationInput)
        switchView(viewUploadProgress, viewUploadStart)
    };

    initFileUpload(uploadFile)
    initExampleUpload(uploadFile)
    initOntology()
}

function initOntology() {
    fetch(ONTOLOGY_URL, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            onto = data
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function initVisual({ classifiedEntities, areaExtension }) {

    const visualContainer = document.getElementById('visual-container');
    const visual = echarts.init(visualContainer);

    const switchChart = initChartNavigation({
        onto,
        visual,
        classifiedEntities,
        areaExtension
    })

    window.addEventListener('resize', function () {
        visual.resize({
            width: 'auto',
            height: 'auto'
        });
    });

    switchChart('classification')
}

function showUploadError() {
    switchView(viewUploadProgress, viewUploadError);

    setTimeout(() => {
        switchView(viewUploadError, viewUploadStart);
    }, 3000)
}

function showClassification({ classifiedEntities, areaExtension }) {
    switchView(viewClassificationInput, viewClassificationResult)
    initVisual({ classifiedEntities, areaExtension })
}

function previewFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        viewClassificationResult.style['background-image'] = `url(${e.target.result})`;
    }
    reader.readAsDataURL(file);
}

function uploadFile(file) {
    const name = file.name;
    let formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);

    switchView(viewUploadStart, viewUploadProgress)

    return fetch(UPLOAD_URL, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const classifiedEntities = data["classification"];
            const areaExtension = data["expansion"]["areas"]
            previewFile(file)
            showClassification({ classifiedEntities, areaExtension })
        })
        .catch(error => {
            console.error('Error:', error);
            showUploadError()
        });
}

document.addEventListener("DOMContentLoaded", init);
