import {ONTOLOGY_URL} from "./api.js";

export default function initOntology({ handelOntologyProgress, handelOntologySuccess, handelOntologyError }) {
    handelOntologyProgress()
    fetch(ONTOLOGY_URL, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(handelOntologySuccess)
        .catch(handelOntologyError);
}
