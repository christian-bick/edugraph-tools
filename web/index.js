import "./index.scss";
import initOntology from "./scripts/ontology.js";
import renderOntology from "./scripts/force-graph.js"

function handleOntologyProgress() {
    console.log('Ontology Progress');
}

function handleOntologySuccess(json) {
    const graphContainer = document.getElementById("graph-container")
    renderOntology(graphContainer, json)
    const graphLoader = document.getElementById("graph-loader")
    graphLoader.style.display = 'none'
    }

function handleOntologyError(err) {
    console.error('Ontology Error:', err);
}

function init() {
    initOntology({handleOntologyProgress, handleOntologySuccess, handleOntologyError})
}

init()
