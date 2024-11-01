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

function updateTreeChart({ visual, entities }) {
    const mapEntity = (entity) => {
        return {
            name: entity.natural_name,
            label: {
                width: autoWidthSize() + 20,
            },
        }
    }
    const mapEntities = (entities) => {
        return entities.map(entity => {
            const obj = mapEntity(entity);
            if (entity.children && entity.children.length) {
                obj.children = mapEntities(entity.children)
            }
            return obj
        })
    }
    const chartOptions = {
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'tree',
                data: mapEntities(entities),
                symbol: 'circle',
                symbolSize: 15,
                initialTreeDepth: 5,
                expandAndCollapse: false,
                emphasis: {
                    focus: 'descendant'
                },
                orient: 'TB',
                label: {
                    fontSize: autoFontSize() + 2,
                    position: 'top',
                    verticalAlign: 'middle',
                    align: 'middle',
                    offset: [0, -5]
                },
                leaves: {
                    label: {
                        position: 'bottom',
                        offset: [0, 5]
                    }
                },
            }
        ]
    }
    visual.clear();
    visual.setOption(chartOptions);
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
                width: autoWidthSize(),
                position: level === 1 ? 'center' : 'inner',
                fontSize: autoFontSize(),
                color: fontColors[level]
            },
            labelLine: {
                show: false
            },
            itemStyle: {
                color: backgroundColors[level],
                borderWidth: '1',
                borderColor: fontColors[level]
            },
            data: mapEntities(entities),
        }
    }
    const chartOptions = {
        tooltip: {
            trigger: 'item',
            formatter: '{a}'
        },
        legend: {
            top: '2%',
            textStyle: {
                fontSize: autoFontSize(),
            },
            data: [{
                name: 'Area'
            }, {
                name: 'Ability'
            }, {
                name: 'Scope'
            }]
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

function updateTaxonomyChart({name, entities, visual, color, color2, highlighted}) {
    const isHighlighted = (entity) => {
        return highlighted.map(h => h.natural_name).includes(entity.natural_name)
    }
    const isHighlightedSubTree = (entity) => {
        if (isHighlighted(entity)) {
            return true
        } else if (entity.children && entity.children.length) {
            return entity.children.map(isHighlightedSubTree).reduce((acc, value) => {
                return acc || value
            }, false);
        } else {
            return false
        }
    }
    const mapEntity = (entity) => {
        const obj = {
            name: entity.natural_name,
            label: {
                overflow: 'break',
                width: autoWidthSize() + 20,
                show: false,
            },
            itemStyle: {
                color: color
            }
        }
        if (entity.children && entity.children.length) {
        } else {
            obj.value = 1
        }
        if (isHighlightedSubTree(entity)) {
            obj.label.show = true
            obj.itemStyle.color = 'red'
        }
        return obj
    }
    const mapEntities = (entities) => {
        return entities.map(entity => {
            const obj = mapEntity(entity);
            if (entity.children && entity.children.length) {
                obj.children = mapEntities(entity.children)
            }
            return obj
        })
    }
    const chartData = [{
        name: name,
        label: {
            fontSize: autoFontSize() + 2,
            fontWeight: 'bold',
            color: 'white',
        },
        itemStyle: {
            color: color2
        },
        children: mapEntities(entities),
    }]
    const chartOptions = {
        series: {
            type: 'sunburst',
            nodeClick: false,
            emphasis: {
                focus: 'ancestor'
            },
            data: chartData,
            radius: [0, '98%'],
            label: {
                rotate: null,
                fontSize: autoFontSize()
            },
            itemStyle: {
                borderColor: color2,
                borderWidth: 1,
                borderType: 'solid'
            }
        }
    };
    visual.clear();
    visual.setOption(chartOptions);
}

function autoFontSize() {
    let width = viewClassificationResult.offsetWidth;
    return Math.min(Math.max(6, Math.round(width / 80)), 16);
}

function autoWidthSize() {
    let width = viewClassificationResult.offsetWidth;
    return Math.max(50, Math.round(width / 10));
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

function initExampleUpload() {
    const uploadExample = document.getElementById('upload-example');
    const imageElements = uploadExample.getElementsByTagName('img');
    for (let imageEl of imageElements) {
        imageEl.onclick = (e) => {
            const url = e.target.currentSrc
            const name = url.split('/').pop()
            const ending = name.split('.').pop()
            const fixed_ending = ending === 'jpg' ? 'jpeg' : ending
            const type = 'image/' + fixed_ending
            fetch(url)
                .then(response => response.blob())
                .then(blob => new File([blob], name, {type}))
                .then(file => uploadFile(file))
            ;
        }
    }
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