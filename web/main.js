import "./style.scss";
import * as echarts from 'echarts';
import updateTaxonomyChart from "./scripts/charts/taxonomy-chart.js";
import updateClassificationChart from "./scripts/charts/classification-chart.js";
import updateTreeChart from "./scripts/charts/tree-chart.js";
import {initExampleUpload, initFileUpload} from "./scripts/classify-file.js";

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

let visualContainer;
let visualClassification;

let filePreview;
let filePreviewMore;

let previousChartButton;
let nextChartButton;

const chartMap = {
    classification: {
        switch: () => {
            updateClassificationChart({
                visual: visualClassification,
                entities: classifiedEntities || classifiedEntitiesDefault
            })
        },
        previous: 'abilityExtension',
        next: 'areaTaxonomy',
    },
    areaTaxonomy: {
        switch: () => {
            updateTaxonomyChart({
                name: 'Areas',
                entities: onto.taxonomy.areas,
                visual: visualClassification,
                color: "#ffb703",
                color2: "#60181A",
                highlighted: classifiedEntities.areas
            });
        },
        previous: 'classification',
        next: 'abilityTaxonomy',
    },
    abilityTaxonomy: {
        switch: () => {
            updateTaxonomyChart({
                name: 'Abilities',
                entities: onto.taxonomy.abilities,
                visual: visualClassification,
                color: "#8acae6",
                color2: "#023047",
                highlighted: classifiedEntities.abilities
            });
        },
        previous: 'areaTaxonomy',
        next: 'scopeTaxonomy',
    },
    scopeTaxonomy: {
        switch: () => {
            updateTaxonomyChart({
                name: 'Scopes',
                entities: onto.taxonomy.scopes,
                visual: visualClassification,
                color: "#87d387",
                color2: "#28603b",
                highlighted: classifiedEntities.scopes
            });
        },
        previous: 'abilityTaxonomy',
        next: 'abilityExtension',
    },
    abilityExtension: {
        switch: () => {
            updateTreeChart({
                visual: visualClassification,
                entities: areaExtension,
            })
        },
        previous: 'scopeTaxonomy',
        next: 'classification',
    }
}

const classifiedEntitiesDefault = {
    areas: [{natural_name: "Area"}],
    abilities: [{natural_name: "Abilities"}],
    scopes: [{natural_name: "Scopes"}],
}

let classifiedEntities = null;
let areaExtension = null;

function switchChart(name) {
    const chartNavigation = chartMap[name]
    chartNavigation.switch();
    previousChartButton.onclick = () => {
        switchChart(chartNavigation.previous)
    };
    nextChartButton.onclick = () => {
        switchChart(chartNavigation.next)
    };
}

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

    visualContainer = document.getElementById('visual-container');

    viewUploadStart = document.getElementById('view-upload-start');
    viewUploadProgress = document.getElementById('view-upload-progress');
    viewUploadError = document.getElementById('view-upload-error');
    viewClassificationInput = document.getElementById('view-classification-input');

    filePreview = document.getElementById('file-preview');
    filePreviewMore = document.getElementById('file-preview-more');
    filePreviewMore.onclick = () => {
        switchView(viewClassificationResult, viewClassificationInput)
        switchView(viewUploadProgress, viewUploadStart)
        classifiedEntities = null
    };

    previousChartButton = document.getElementById('previous-chart-button');
    nextChartButton = document.getElementById('next-chart-button');

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

function initVisuals() {

    if (!visualClassification) {
        visualClassification = echarts.init(visualContainer);
    }

    window.addEventListener('resize', function () {
        visualClassification.resize({
            width: 'auto',
            height: 'auto'
        });
    });

    switchChart('classification')

    visualClassification.on('click', (source) => {
        if (source.seriesName === 'Area') {
            switchChart('areaTaxonomy')
        } else if (source.seriesName === 'Ability') {
            switchChart('abilityTaxonomy')
        } else if (source.seriesName === 'Scope') {
            switchChart('scopeTaxonomy')
        } else if (source.name === 'Areas' || source.name === 'Abilities' || source.name === 'Scopes') {
            switchChart('classification')
        }
    })
}

function showUploadError() {
    switchView(viewUploadProgress, viewUploadError);

    setTimeout(() => {
        switchView(viewUploadError, viewUploadStart);
    }, 3000)
}

function showClassification() {
    switchView(viewClassificationInput, viewClassificationResult)
    initVisuals()
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
            classifiedEntities = data["classification"];
            areaExtension = data["expansion"]["areas"]
            previewFile(file)
            showClassification()
        })
        .catch(error => {
            console.error('Error:', error);
            showUploadError()
        });
}

document.addEventListener("DOMContentLoaded", init);
