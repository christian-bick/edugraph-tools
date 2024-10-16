import "./style.scss";
import * as echarts from 'echarts';

const API_URL = import.meta.env.PROD ? "https://edu-graph-api-575953891979.europe-west3.run.app" : "/api"

const UPLOAD_URL = `${API_URL}/classify`
const ONTOLOGY_URL = `${API_URL}/ontology`

let onto;

let viewInit;
let viewClassification;
let viewUpload;
let viewProgress;
let viewResult;

let visualAreas;
let visualAbilities;
let visualScopes;

function switchView(oldEl, newEl)  {
    newEl.style.display = "flex";
    oldEl.style.display = "none";
}

function init() {
    viewInit = document.getElementById('view-init')
    viewClassification = document.getElementById('view-init')
    viewUpload = document.getElementById('view-upload');
    viewProgress = document.getElementById('view-progress');
    viewResult = document.getElementById('view-result');

    setTimeout(() => switchView(viewInit, viewClassification), 1000)
    initFileUpload()
    initOntology()
}

function initOntology() {
    fetch(ONTOLOGY_URL, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            onto = data
            initVisuals()
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function mapEntity(entity, highlighted = []) {
    const obj = {
        name: entity.natural_name,
    }
    if (entity.children && entity.children.length) {
        obj.label = {
            show: false,
        }
    } else {
        obj.value = 1
        obj.label = {
            show: false,
        }
    }
    if (highlighted.includes(entity.name)) {
        obj.itemStyle = {
            color: 'red'
        }
    }
    return obj
}

function mapEntities(entities,  highlighted = []) {
    return entities.map(entity => {
        const obj = mapEntity(entity, highlighted);
        if (entity.children && entity.children.length) {
            obj.children = mapEntities(entity.children, highlighted)
        }
        return obj
    })
}

function createChart(name, entities, element, color, highlighted = []) {
    const chartArea = echarts.init(element);
    const chartData = [{
        name: name,
        children: mapEntities(entities, highlighted),
    }]
    const chartOptions = {
        series: {
            type: 'sunburst',
            emphasis: {
                focus: 'ancestor'
            },
            data: chartData,
            radius: [0, '100%'],
            label: {
                rotate: null,
                fontSize: '14',
                fontWeight: 'bold',
            },
            itemStyle: {
                color: color
            },
        }
    };
    chartArea.setOption(chartOptions);
}

function initVisuals() {
    visualAreas = document.getElementById('visual-areas')
    visualAbilities = document.getElementById('visual-abilities')
    visualScopes = document.getElementById('visual-scopes')
    updateVisuals()
}

function updateVisuals(classified = { areas: [], abilities: [], scopes: [] }) {
    createChart('Areas', onto.areas, visualAreas, "#ffb703", classified.areas)
    createChart('Abilities', onto.abilities, visualAbilities, "#8acae6", classified.abilities)
    createChart('Scopes', onto.scopes, visualScopes, "#87d387", classified.scopes)
}

function initFileUpload() {
    const viewUpload = document.getElementById('view-upload');
    const viewProgress = document.getElementById('view-progress');
    const viewResult = document.getElementById('view-result');

    const uploadDropzone = document.getElementById('upload-dropzone');
    const uploadInput = document.getElementById('upload-input');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, unhighlight,
            false);
    });

    function highlight() {
        uploadDropzone.classList.add('highlight');
    }

    function unhighlight() {
        uploadDropzone.classList.remove('highlight');
    }

    // Handle dropped files
    uploadDropzone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        let dt = e.dataTransfer;

        let files = dt.files;

        handleFiles(files);
    }

    // Handle files from input element
    uploadInput.addEventListener('change', handleFiles, false);

    function handleFiles(files) {
        uploadFile(files[0]);
    }

    function previewFile(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            viewResult.innerHTML = `<img class="file-preview" src="${e.target.result}" alt="${file.name}"/>`;
            switchView(viewProgress, viewResult)
        }
        reader.readAsDataURL(file);
    }

    function uploadFile(file) {
        let formData = new FormData();
        formData.append('file', file);

        switchView(viewUpload, viewProgress)

        fetch(UPLOAD_URL, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                previewFile(file)
                updateVisuals(data)
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

document.addEventListener("DOMContentLoaded", init);