import "./style.scss";
import * as echarts from 'echarts';
import initClassification from "./scripts/file-classification.js";
import initChartNavigation from "./scripts/chart-navigation.js";
import initOntology from "./scripts/ontology.js";

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

    initOntology({ handelOntologyProgress, handelOntologySuccess, handelOntologyError })
    initClassification({ handelClassificationProgress, handleClassificationSuccess, handleClassificationError })
}

function handelOntologyProgress() {
    switchView(viewUploadStart, viewUploadProgress)
}

function handelOntologySuccess(json) {
    onto = json
    switchView(viewUploadProgress, viewUploadStart)
}

function handelOntologyError(err) {
    console.error('Ontology Error:', err);
}

function handelClassificationProgress() {
    switchView(viewUploadStart, viewUploadProgress)
}

function handleClassificationSuccess(file, json) {
    const result = {
        classifiedEntities: json["classification"],
        areaExtension: json["expansion"]["areas"]
    };
    switchView(viewClassificationInput, viewClassificationResult)
    initVisual(result)
    previewFile(file)
}

function handleClassificationError(err) {
    console.error('Classification Error:', err);
    switchView(viewUploadProgress, viewUploadError);

    setTimeout(() => {
        switchView(viewUploadError, viewUploadStart);
    }, 3000)
}

function initVisual({classifiedEntities, areaExtension}) {

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

function previewFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        viewClassificationResult.style['background-image'] = `url(${e.target.result})`;
    }
    reader.readAsDataURL(file);
}

document.addEventListener("DOMContentLoaded", init);
