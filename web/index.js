import "./style.scss";
import initOntology from "./scripts/ontology.js";

function handleOntologyProgress() {
    console.log('Ontology Progress');
}

function handleOntologySuccess(json) {
    console.log('Ontology Success');
    console.log(json)
}

function handleOntologyError(err) {
    console.error('Ontology Error:', err);
}

function init() {
    initOntology({ handleOntologyProgress, handleOntologySuccess, handleOntologyError })
}

init()
