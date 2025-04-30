<template>
  <div ref="networkContainer" class="w-full h-96"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  nodes: {
    type: Array,
    default: () => []
  },
  links: {
    type: Array,
    default: () => []
  }
})

const networkContainer = ref(null)

const drawNetwork = () => {
  if (!props.nodes.length) return

  const width = networkContainer.value.clientWidth
  const height = 400

  // Clear previous
  d3.select(networkContainer.value).selectAll('*').remove()

  // Create SVG
  const svg = d3.select(networkContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // Simulation
  const simulation = d3.forceSimulation(props.nodes)
    .force('link', d3.forceLink(props.links).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))

  // Draw links
  const link = svg.append('g')
    .selectAll('line')
    .data(props.links)
    .join('line')
    .attr('stroke', '#9CA3AF')
    .attr('stroke-width', 1)

  // Draw nodes
  const node = svg.append('g')
    .selectAll('circle')
    .data(props.nodes)
    .join('circle')
    .attr('r', 8)
    .attr('fill', d => d.color || '#9945FF')
    .call(drag(simulation))

  // Update positions
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
  })
}

const drag = (simulation) => {
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    event.subject.fx = event.subject.x
    event.subject.fy = event.subject.y
  }

  function dragged(event) {
    event.subject.fx = event.x
    event.subject.fy = event.y
  }

  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0)
    event.subject.fx = null
    event.subject.fy = null
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended)
}

onMounted(drawNetwork)
watch(() => [props.nodes, props.links], drawNetwork)
</script>