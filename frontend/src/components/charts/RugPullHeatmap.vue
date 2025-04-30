<template>
  <div ref="heatmapContainer" class="w-full h-96"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const heatmapContainer = ref(null)

const drawHeatmap = () => {
  if (!props.data.length) return

  const width = heatmapContainer.value.clientWidth
  const height = 400
  const margin = { top: 30, right: 30, bottom: 60, left: 60 }

  // Clear previous
  d3.select(heatmapContainer.value).selectAll('*').remove()

  // Create SVG
  const svg = d3.select(heatmapContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // Create scales
  const xScale = d3.scaleBand()
    .domain(props.data.map(d => d.time))
    .range([margin.left, width - margin.right])

  const yScale = d3.scaleBand()
    .domain(props.data.map(d => d.token))
    .range([margin.top, height - margin.bottom])

  const colorScale = d3.scaleSequential(d3.interpolateReds)
    .domain([0, d3.max(props.data, d => d.value)])

  // Draw cells
  svg.selectAll('rect')
    .data(props.data)
    .join('rect')
    .attr('x', d => xScale(d.time))
    .attr('y', d => yScale(d.token))
    .attr('width', xScale.bandwidth())
    .attr('height', yScale.bandwidth())
    .attr('fill', d => colorScale(d.value))

  // Add axes
  svg.append('g')
    .attr('transform', `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(xScale))

  svg.append('g')
    .attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(yScale))
}

onMounted(drawHeatmap)
watch(() => props.data, drawHeatmap)
</script>