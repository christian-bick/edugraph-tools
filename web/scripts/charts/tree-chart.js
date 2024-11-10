import {autoFontSize, autoWidth} from "./chart-scaling.js";

export default function updateTreeChart({visual, entities}) {
    const mapEntity = (entity) => {
        return {
            name: entity.natural_name,
            label: {
                width: autoWidth() + 20,
            },
        }
    }
    const mapEntities = (entities) => {
        return entities.map(entity => {
            const obj = mapEntity(entity);
            if (entity.children && entity.children.length) {
                obj.children = mapEntities(entity.children)
            }
            return obj
        })
    }
    const chartOptions = {
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'tree',
                data: mapEntities(entities),
                symbol: 'circle',
                symbolSize: 15,
                initialTreeDepth: 5,
                expandAndCollapse: false,
                emphasis: {
                    focus: 'descendant'
                },
                orient: 'TB',
                label: {
                    fontSize: autoFontSize() + 2,
                    position: 'top',
                    verticalAlign: 'middle',
                    align: 'middle',
                    offset: [0, -5]
                },
                leaves: {
                    label: {
                        position: 'bottom',
                        offset: [0, 5]
                    }
                },
            }
        ]
    }
    visual.clear();
    visual.setOption(chartOptions);
}
