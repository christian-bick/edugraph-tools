import {autoFontSize, autoWidth} from "./chart-scaling.js";

export default function updateClassificationChart({visual, entities: {areas, abilities, scopes}}) {
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
                width: autoWidth(),
                position: level === 1 ? 'center' : 'inner',
                fontSize: autoFontSize(),
                color: fontColors[level],
                show: true,
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
