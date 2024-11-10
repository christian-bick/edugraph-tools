import updateClassificationChart from "./charts/classification-chart.js";
import updateTaxonomyChart from "./charts/taxonomy-chart.js";
import updateTreeChart from "./charts/tree-chart.js";

export default function initChartNavigation({onto, visual, classifiedEntities, areaExtension }) {
    const chartNavigation = {
        classification: {
            activate: () => {
                updateClassificationChart({
                    visual, entities: classifiedEntities
                })
            }, previous: 'abilityExtension', next: 'areaTaxonomy',
        }, areaTaxonomy: {
            activate: () => {
                updateTaxonomyChart({
                    name: 'Areas',
                    entities: onto.taxonomy.areas,
                    visual,
                    color: "#ffb703",
                    color2: "#60181A",
                    highlighted: classifiedEntities.areas
                });
            }, previous: 'classification', next: 'abilityTaxonomy',
        }, abilityTaxonomy: {
            activate: () => {
                updateTaxonomyChart({
                    name: 'Abilities',
                    entities: onto.taxonomy.abilities,
                    visual,
                    color: "#8acae6",
                    color2: "#023047",
                    highlighted: classifiedEntities.abilities
                });
            }, previous: 'areaTaxonomy', next: 'scopeTaxonomy',
        }, scopeTaxonomy: {
            activate: () => {
                updateTaxonomyChart({
                    name: 'Scopes',
                    entities: onto.taxonomy.scopes,
                    visual,
                    color: "#87d387",
                    color2: "#28603b",
                    highlighted: classifiedEntities.scopes
                });
            }, previous: 'abilityTaxonomy', next: 'abilityExtension',
        }, abilityExtension: {
            activate: () => {
                updateTreeChart({
                    visual, entities: areaExtension,
                })
            }, previous: 'scopeTaxonomy', next: 'classification',
        }
    }

    const previousChartButton = document.getElementById('previous-chart-button');
    const nextChartButton = document.getElementById('next-chart-button');

    const switchChart = (name) => {
        const chart = chartNavigation[name]
        chart.activate();
        previousChartButton.onclick = () => {
            switchChart(chart.previous)
        };
        nextChartButton.onclick = () => {
            switchChart(chart.next)
        };
    }
    return switchChart;
}
