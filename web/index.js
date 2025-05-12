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
    const scrollTo = document.getElementById('scroll-button')
    const main = document.getElementById('header')
    scrollTo.addEventListener('click', () => scrollToElementTop(main))

    const onScroll = (listener) => {
        const element = document.getElementById('scroll-button')
        element.style.opacity = '0'
        removeEventListener('scroll', onScroll)
    }
     window.addEventListener('scroll', onScroll)
}

function scrollToElementTop(element) {
    if (!element) {
        console.error('Element is null or undefined');
        return;
    }

    const elementRect = element.getBoundingClientRect();
    const absoluteElementTop = elementRect.top + window.pageYOffset;

    window.scrollTo({
        top: absoluteElementTop,
        behavior: 'smooth' // Optional: smooth scrolling animation
    });
}

init()
