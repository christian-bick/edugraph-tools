import {autoFontSize, autoWidth} from "./chart-scaling.js";

export default function updateTaxonomyChart({name, entities, visual, color, color2, highlighted}) {
    const isHighlighted = (entity) => {
        return highlighted.map(h => h.natural_name).includes(entity.natural_name)
    }
    const isHighlightedSubTree = (entity) => {
        if (isHighlighted(entity)) {
            return true
        } else if (entity.children && entity.children.length) {
            return entity.children.map(isHighlightedSubTree).reduce((acc, value) => {
                return acc || value
            }, false);
        } else {
            return false
        }
    }
    const mapEntity = (entity) => {
        const obj = {
            name: entity.natural_name,
            label: {
                overflow: 'break',
                width: autoWidth() + 20,
                show: false,
            },
            itemStyle: {
                color: color
            }
        }
        if (entity.children && entity.children.length) {
        } else {
            obj.value = 1
        }
        if (isHighlightedSubTree(entity)) {
            obj.label.show = true
            obj.itemStyle.color = 'red'
        }
        return obj
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
    const chartData = [{
        name: name,
        label: {
            fontSize: autoFontSize() + 2,
            fontWeight: 'bold',
            color: 'white',
        },
        itemStyle: {
            color: color2
        },
        children: mapEntities(entities),
    }]
    const chartOptions = {
        series: {
            type: 'sunburst',
            nodeClick: false,
            emphasis: {
                focus: 'ancestor'
            },
            data: chartData,
            radius: [0, '98%'],
            label: {
                rotate: null,
                fontSize: autoFontSize()
            },
            itemStyle: {
                borderColor: color2,
                borderWidth: 1,
                borderType: 'solid'
            }
        }
    };
    visual.clear();
    visual.setOption(chartOptions);
}

