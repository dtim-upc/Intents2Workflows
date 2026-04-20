<template>
  <div style="height: 70vh">
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      fit-view-on-init
      class="vue-flow-basic-example"
      :default-zoom="1.5"
      :min-zoom="0.2"
      :max-zoom="4"
    >
      <Background pattern-color="#aaa" :gap="8" />

      <MiniMap />

      <Controls />

      <template #node-custom="nodeProps">
        <CustomNode v-bind="nodeProps" />
      </template>

      <template #edge-custom="edgeProps">
        <CustomEdge v-bind="edgeProps" />
      </template>
    </VueFlow>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { VueFlow, useVueFlow, type Node, type Edge, Position} from '@vue-flow/core'
import CustomNode from './CustomNode.vue'
import CustomEdge from './CustomEdge.vue'
import ELK from 'elkjs/lib/elk.bundled.js'

const props = defineProps(['plan', 'cols'])
const { onConnect, addEdges } = useVueFlow()

/* Reference structure of the nodes and edges
const nodes = ref<Node[]>([
  { id: 'https://extremexp.eu/ontology/cbox#DataLoading', type: 'input', label: 'DataLoading', position: { x: 0, y: 0 }, sourcePosition: Position.Right, class: 'grey-node'},
  { id: 'https://extremexp.eu/ontology/cbox#DataStoring', type: 'output', label: 'DataStoring', position: { x: 800, y: 0 }, targetPosition: Position.Left, class: 'grey-node'},
  { id: 'https://extremexp.eu/ontology/cbox#DecisionTree', label: 'DecisionTree', position: { x: 600, y: 0 }, sourcePosition: Position.Right, targetPosition: Position.Left, class: 'grey-node'},
  { id: 'https://extremexp.eu/ontology/cbox#DecisionTree-Train', label: 'DecisionTree Train', position: { x: 400, y: 60 }, sourcePosition: Position.Right, targetPosition: Position.Left, class: 'grey-node' },
  { id: 'https://extremexp.eu/ontology/cbox#Partitioning', label: 'Partitioning', position: { x: 200, y: 0 }, sourcePosition: Position.Right, targetPosition: Position.Left, class: 'grey-node' },
])

const edges = ref<Edge[]>([
  { id: 'e0', source: 'https://extremexp.eu/ontology/cbox#DataLoading', target: 'https://extremexp.eu/ontology/cbox#Partitioning', type: 'input', animated: true },
  { id: 'e1', source: 'https://extremexp.eu/ontology/cbox#Partitioning', target: 'https://extremexp.eu/ontology/cbox#DecisionTree-Train', type: 'input', animated: true },
  { id: 'e2', source: 'https://extremexp.eu/ontology/cbox#Partitioning', target: 'https://extremexp.eu/ontology/cbox#DecisionTree', type: 'input', animated: true },
  { id: 'e3', source: 'https://extremexp.eu/ontology/cbox#DecisionTree-Train', target: 'https://extremexp.eu/ontology/cbox#DecisionTree', type: 'input', animated: true },
  { id: 'e4', source: 'https://extremexp.eu/ontology/cbox#DecisionTree', target: 'https://extremexp.eu/ontology/cbox#DataStoring', type: 'input', animated: true },
])*/

const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])

const elk = new ELK({
  defaultLayoutOptions: {
    'elk.algorithm': 'layered',
    'org.eclipse.elk.spacing.nodeNode': '20',
    'org.eclipse.elk.layered.spacing.edgeNodeBetweenLayers': '20',
    'org.eclipse.elk.spacing.edgeNode': '20',
  }
})

function toTitleCase(str: string): string {
  return str.replace(
    /\w\S*/g,
    function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substring(1);
    }
  );
}



async function plan_layout(plan: Array<[string, string[]]>, cols: Record<string, string[]>) {
  try {
    let nodes_plan = [];
    for (let component of plan){
      let node_id = component[0].split('#').at(-1)!;
      let label = toTitleCase(node_id.replaceAll('_', ' ').replaceAll('-', ' ').replace('component ', ''));
      let width = 125;
      let lines = measureTextLines(label, width)
      let height = Math.max(40, 20+ lines * 20);
      let description = cols[component[0]]
      let result = description?.map((c: string) => c.split('#').pop() ?? c);
      if (result == undefined) result = []
      nodes_plan.push({
        id: component[0],
        node_id: node_id,
        data: {
            label: label,
            description: result,
            width: width,
            height: height,
            color: "#d8cece"
        },
        width: width,
        height: height,
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      })
    }

    //console.log(nodes_plan)

    let edges_plan = [];
    let i = 0;
    for (let source of plan) {
      for (let target of source[1]) {
        edges_plan.push({
          id: 'e' + i,
          sources: [source[0]],
          targets: [target],
          source: source[0],
          target: target,
          arrow: true,
        });
        i++;
      }
    }

    //console.log(edges_plan)

    const graph = {
      id: "root",
      children: nodes_plan,
      edges: edges_plan
    }
    console.log("GRAPH:", graph)
    const layout = await elk.layout(graph);
    console.log("LAYOUT:", layout)

    nodes.value = layout.children!.map(node => {
    const nodeData = nodes_plan.find(n => n.id === node.id)?.data

    return {
      id: node.id, 
      position: {
        x: node.x as number,
        y: node.y as number,
      },
      data: {
        label: nodeData?.label,
        description: nodeData?.description,
        width: nodeData?.width,
        height: nodeData?.height,
        color: nodeData?.color,
        x : node.x as number,
        y: node.y as number
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      class: 'grey-node',
      type: 'custom'
    }
  })

    edges.value = layout.edges!.map(edge => ({
    id: edge.id,
    source: edge.sources[0] as string,
    target: edge.targets[0] as string,
    }))

  }
  catch (error) {
    console.error('Layout failed:', error);
    // Fallback to manual positioning
  }

}

function measureTextLines(label:string, width:number, fontSize = 12, fontFamily = 'Roboto', padding=10) {
  // Create canvas context for accurate measurement
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const realWidth = width - 2*padding
  if(ctx) ctx.font = `${fontSize}px ${fontFamily}`;
  
  const words = label.split(' ');
  let lines = 1;
  let currentLine = words[0];
  
  for (let i = 1; i < words.length; i++) {
    const testLine = currentLine + ' ' + words[i];
    const metrics = ctx? ctx.measureText(testLine): {width: 0}
    
    if (metrics.width > realWidth) {
      lines++;
      currentLine = words[i];
    } else {
      currentLine = testLine;
    }
  }

  console.log("lines of", label, lines)
  
  return lines
}


plan_layout(props.plan, props.cols)

onConnect((params) => {
  addEdges([params])
})
</script>

<style>
.grey-node {
  background: #d8cece;
}
</style>
