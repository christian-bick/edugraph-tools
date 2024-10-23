import "./style.scss";
import * as echarts from 'echarts';

const API_URL = import.meta.env.PROD ? "https://edu-graph-api-575953891979.europe-west3.run.app" : "http://localhost:8080"

const UPLOAD_URL = `${API_URL}/classify`
const ONTOLOGY_URL = `${API_URL}/ontology`

let onto;

let viewInit;
let viewClassification;
let viewUploadStart;
let viewUploadProgress;
let viewUploadResult;
let viewClassificationResult;

let visualContainer;

let filePreview;
let filePreviewMore;

let visualClassification;

const classifiedEntitiesDefault = {
    areas: [{natural_name: "Area"}],
    abilities: [{natural_name: "Abilities"}],
    scopes: [{natural_name: "Scopes"}],
}

let classifiedEntities = null;

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
    viewUploadResult = document.getElementById('view-upload-result');

    filePreview = document.getElementById('file-preview');
    filePreviewMore = document.getElementById('file-preview-more');
    filePreviewMore.onclick = () => {
        deactivateView(viewClassificationResult)
        switchView(viewUploadResult, viewUploadStart)
        classifiedEntities = null
    };

    initFileUpload()
    initExampleUpload()
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

function updateClassificationChart({visual, entities: {areas, abilities, scopes}}) {
    const mapEntities = (entities) => {
        return entities.map(entity => ({value: 1, name: entity.natural_name}))
    }
    const buildLevel = (level, name, entities) => {
        const backgroundColors = {
            1: "#ffb703",
            2: "#8acae6",
            3: "#87d387"
        }
        const fontColors = {
            1: "#60181A",
            2: "#023047",
            3: "#28603b"
        }
        const innerRadius = ((level - 1) * 30) + '%' // 0, 35, 70
        const outerRadius = ((level) * 30) - 5 + '%' // 30, 65, 100
        return {
            name: name,
            type: 'pie',
            selectedMode: 'none',
            padAngle: entities.length > 1 ? 3 : 0,
            radius: [innerRadius, outerRadius],
            label: {
                overflow: 'break',
                width: 120,
                position: level === 1 ? 'center' : 'inner',
                fontSize: 16,
                color: fontColors[level]
            },
            labelLine: {
                show: false
            },
            itemStyle: {
                color: backgroundColors[level]
            },
            data: mapEntities(entities),
        }
    }
    const chartOptions = {
        title: {
            text: 'Classification of Learning Material',
            left: 'center',
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a}'
        },
        series: [
            buildLevel(1, 'Area', areas),
            buildLevel(2, 'Ability', abilities),
            buildLevel(3, 'Scope', scopes),
        ]
    };
    visual.clear();
    visual.setOption(chartOptions);
}

function createTaxonomyChart({name, entities, visual, color, highlighted}) {
    const isHighlighted = (entity) => {
        return highlighted.map(h => h.natural_name).includes(entity.natural_name)
    }
    const mapEntity = (entity) => {
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
                blur: {
                    show: true,
                },
            }
        }
        if (isHighlighted(entity)) {
            obj.label = {
                show: true,
            }
            obj.itemStyle = {
                color: 'red'
            }
        }
        return obj
    }
    const mapEntities = (entities) => {
        return entities.map(entity => {
            const obj = mapEntity(entity, highlighted);
            if (entity.children && entity.children.length) {
                obj.children = mapEntities(entity.children, highlighted)
            }
            return obj
        })
    }
    const chartData = [{
        name: name,
        children: mapEntities(entities, highlighted),
    }]
    const chartOptions = {
        series: {
            type: 'sunburst',
            nodeClick: false,
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
    visual.clear();
    visual.setOption(chartOptions);
}

function initVisuals() {

    if (!visualClassification) {
        visualClassification = echarts.init(visualContainer);
    }

    updateClassificationChart({
        visual: visualClassification,
        entities: classifiedEntitiesDefault
    })

    visualClassification.on('click', (source) => {
        const highlightedEntities = classifiedEntities || classifiedEntitiesDefault
        if (source.seriesName === 'Area') {
            createTaxonomyChart({
                name: 'Area Taxonomy',
                entities: onto.areas,
                visual: visualClassification,
                color: "#ffb703",
                highlighted: highlightedEntities.areas
            });
        } else if (source.seriesName === 'Ability') {
            createTaxonomyChart({
                name: 'Ability Taxonomy',
                entities: onto.abilities,
                visual: visualClassification,
                color: "#8acae6",
                highlighted: highlightedEntities.abilities
            });
        } else if (source.seriesName === 'Scope') {
            createTaxonomyChart({
                name: 'Scope Taxonomy',
                entities: onto.scopes,
                visual: visualClassification,
                color: "#87d387",
                highlighted: highlightedEntities.scopes
            });
        } else if (source.name === 'Area Taxonomy' || source.name === 'Ability Taxonomy' || source.name === 'Scope Taxonomy') {
            updateClassificationChart({
                visual: visualClassification,
                entities: highlightedEntities
            });
        }
    })
}

function showClassification() {
    activateView(viewClassificationResult)
    initVisuals()
    updateClassificationChart({
        visual: visualClassification,
        entities: classifiedEntities || classifiedEntitiesDefault
    })
}

function initExampleUpload() {
    const uploadExample = document.getElementById('upload-example');
    const imageElements = uploadExample.getElementsByTagName('img');
    for (let imageEl of imageElements) {
        imageEl.onclick = (e) => {
            const url = e.target.currentSrc
            const name = url.split('/').pop()
            const ending = 'image/' + name.split('.').pop()
            const type = ending === 'jpg' ? 'jpeg' : ending
            fetch(url)
                .then(response => response.blob())
                .then(blob => new File([blob], name, {type}))
                .then(uploadFile)
            ;
        }
    }
}

function previewFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        filePreview.src = e.target.result;
        filePreview.alt = file.name;
        switchView(viewUploadProgress, viewUploadResult)
    }
    reader.readAsDataURL(file);
}

function uploadFile(file) {
    let formData = new FormData();
    formData.append('file', file);

    switchView(viewUploadStart, viewUploadProgress)

    return fetch(UPLOAD_URL, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            classifiedEntities = data;
            previewFile(file)
            showClassification()
        })
        .catch(error => {
            console.error('Error:', error);
            switchView(viewUploadProgress, viewUploadStart)
        });
}

function initFileUpload() {
    const uploadDropzone = document.getElementById('upload-dropzone');
    const uploadInput = document.getElementById('upload-input');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadDropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
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
        return handleFiles(files);
    }

    // Handle files from input element
    uploadInput.addEventListener('change', handleFiles, false);

    function handleFiles(files) {
        return uploadFile(files[0]);
    }
}

document.addEventListener("DOMContentLoaded", init);