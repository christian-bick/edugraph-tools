import ForceGraph3D from "3d-force-graph";
import SpriteText from "three-spritetext";

function eliminateDuplicates(list) {
    const uniqueObjectsMap = new Map();
    for (const obj of list) {
        uniqueObjectsMap.set(obj.id, obj); // Store the original object to preserve order if needed
    }
    return Array.from(uniqueObjectsMap.values());
}

function taxonomyToGraph(name, taxonomy, { color = '#ffffff' }) {
    let nodes = [{id: name, label: name}]
    let links = []
    for (const root of taxonomy) {
        nodes = nodes.concat(collectNodes(root))
        links = links.concat({ source: name, target: root.name})
        links = links.concat(collectLinks(root))
    }
    nodes = eliminateDuplicates(nodes)
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
export default function renderOntology(domElement, json) {
    const graphData1 = taxonomyToGraph("Areas", json.taxonomy.areas, { color: '#fb8500' })
    const graphData2 = taxonomyToGraph("Abilities", json.taxonomy.abilities, { color: '#219ebc' })
    const graphData3 = taxonomyToGraph("Scopes", json.taxonomy.scopes, { color: '#5cb85c' })
    const graph = new ForceGraph3D(domElement)
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
