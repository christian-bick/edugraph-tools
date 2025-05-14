import "./index.scss";
import initOntology from "./scripts/ontology.js";
import renderOntology from "./scripts/force-graph.js"

function handleOntologyProgress() {
    console.log('Ontology Progress');
}

let graphContainer;
let graphLoader;
let heroTitle;
let scrollContainer;
let scrollButton;

let minInitTimePassed = false;

function switchHeroView(json) {
    renderOntology(graphContainer, json)
    graphLoader.style.display = 'none'
    heroTitle.style.display = 'none'
    scrollContainer.style.display = 'flex'
}

function handleOntologySuccess(json) {
    if (minInitTimePassed) {
        switchHeroView(json)
    } else {
        setTimeout(() => handleOntologySuccess(json), 10)
    }
}

function handleOntologyError() {
    graphLoader.style.display = 'none'
    scrollContainer.style.display = 'flex'
}

function setInitTime() {
    setTimeout(() => minInitTimePassed = true, 1500)
    setTimeout(handleOntologyError, 15000)
}

function init() {
    setInitTime()
    graphContainer = document.getElementById("graph-container")
    graphLoader = document.getElementById("graph-loader")
    heroTitle = document.getElementById("hero-title")
    scrollContainer = document.getElementById("scroll-container")
    scrollButton = document.getElementById('scroll-button')

    initOntology({handleOntologyProgress, handleOntologySuccess, handleOntologyError})
    const main = document.getElementById('header')
    scrollButton.addEventListener('click', () => scrollToElementTop(main))
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
