import {ONTOLOGY_URL} from "./api.js";

export default function initOntology({ handleOntologyProgress, handleOntologySuccess, handleOntologyError }) {
    handleOntologyProgress()
    fetch(ONTOLOGY_URL, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(handleOntologySuccess)
        .catch(handleOntologyError);
}
