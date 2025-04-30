<template>
  <div ref="chartContainer" class="w-full h-96"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import * as d3Sankey from 'd3-sankey'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const chartContainer = ref(null)

const drawChart = () => {
  if (!props.data?.nodes) return

  const width = chartContainer.value.clientWidth
  const height = 400

  // Clear previous
  d3.select(chartContainer.value).selectAll('*').remove()

  // Create SVG
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // Sankey generator
  const sankey = d3Sankey.sankey()
    .nodeWidth(15)
    .nodePadding(10)
    .size([width, height])

  const { nodes, links } = sankey(props.data)

  // Draw links
  svg.append('g')
    .selectAll('path')
    .data(links)
    .join('path')
    .attr('d', d3Sankey.sankeyLinkHorizontal())
    .attr('stroke', d => d.color || '#9945FF')
    .attr('stroke-width', d => Math.max(1, d.width))
    .attr('fill', 'none')

  // Draw nodes
  const node = svg.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')

  node.append('rect')
    .attr('x', d => d.x0)
    .attr('y', d => d.y0)
    .attr('height', d => d.y1 - d.y0)
    .attr('width', d => d.x1 - d.x0)
    .attr('fill', d => d.color || '#00FFA3')

  // Add labels
  node.append('text')
    .attr('x', d => d.x0 - 6)
    .attr('y', d => (d.y1 + d.y0) / 2)
    .attr('text-anchor', 'end')
    .text(d => d.name)
    .attr('font-size', 10)
    .attr('fill', '#fff')
}

onMounted(drawChart)
watch(() => props.data, drawChart)
</script>