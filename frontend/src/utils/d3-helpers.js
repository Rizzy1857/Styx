import * as d3 from 'd3'

export const createSimulation = (nodes, edges, width, height) =>
  d3
    .forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((node) => node.id).distance(90).strength(0.7))
    .force('charge', d3.forceManyBody().strength(-280))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(28))

export const getNodeColor = (node) => {
  if (node.type === 'service') return '#93C5FD'
  if (node.status === 'ACTIVE') return '#10B981'
  if (node.status === 'DEPRECATED') return '#EAB308'
  if (node.status === 'ZOMBIE') return '#DC2626'
  if (node.status === 'SHADOW') return '#8B5CF6'
  return '#CADCFC'
}

export const getLinkWidth = (weight) => Math.max(1, Math.min(6, weight / 40))

export const setupZoom = (svg, g) => {
  const zoom = d3.zoom().scaleExtent([0.5, 3]).on('zoom', (event) => {
    g.attr('transform', event.transform)
  })
  svg.call(zoom)
}
