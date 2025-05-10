import ForceGraph3D from '3d-force-graph';
import SpriteText from 'three-spritetext';

import "./style.scss";
import initOntology from "./scripts/ontology.js";

function handleOntologyProgress() {
    console.log('Ontology Progress');
}

function taxonomyToGraph(name, taxonomy, { color = '#ffffff' }) {
    console.log(taxonomy)
    let nodes = [{id: name, label: name}]
    let links = []
    for (const root of taxonomy) {
        nodes = nodes.concat(collectNodes(root))
        links = links.concat({ source: name, target: root.name})
        links = links.concat(collectLinks(root))
    }
    return {
        nodes: nodes.map(node => ({...node, color})),
        links
    }
}

function collectNodes(tree) {
    let nodes = [{id: tree.name, label: tree.natural_name}]
    if (tree.children) {
        for (const child of tree.children) {
            nodes = nodes.concat(collectNodes(child))
        }
    }
    return nodes
}

function collectLinks(tree) {
    let links = []
    if (tree.children) {
        for (const child of tree.children) {
            links.push({source: tree.name, target: child.name, value: 1})
            links = links.concat(collectLinks(child))
        }
    }
    return links
}

function concatGraphs(graphDataArrays) {
    let nodes = []
    let links = []
    for (const graphData of graphDataArrays) {
        nodes = nodes.concat(graphData.nodes)
        links = links.concat(graphData.links)
    }
    return { nodes, links }
}

function handleOntologySuccess(json) {
    console.log('Ontology Success');
    const graphData1 = taxonomyToGraph("Areas", json.taxonomy.areas, { color: '#fb8500' })
    const graphData2 = taxonomyToGraph("Abilities", json.taxonomy.abilities, { color: '#219ebc' })
    const graphData3 = taxonomyToGraph("Scopes", json.taxonomy.scopes, { color: '#5cb85c' })
    console.log(graphData1)
    const myDOMElement = document.getElementById("main")
    const graph = new ForceGraph3D(myDOMElement)
        .graphData(concatGraphs([graphData1, graphData2, graphData3]))
        .nodeAutoColorBy('group')
        .nodeThreeObject(node => {
            const sprite = new SpriteText(node.label);
            sprite.material.depthWrite = false; // make sprite background transparent
            sprite.color = node.color;
            sprite.textHeight = 8;
            return sprite;
        });
    graph.d3Force('charge').strength(-120);
}

function handleOntologyError(err) {
    console.error('Ontology Error:', err);
}

function init() {
    initOntology({handleOntologyProgress, handleOntologySuccess, handleOntologyError})
}

init()
