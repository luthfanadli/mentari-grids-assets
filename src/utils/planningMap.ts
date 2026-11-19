import type { FeatureCollection } from 'geojson'
import type { Map as LibreMap } from 'maplibre-gl'
import type { ProjectFeature, ProjectGeometry } from '../types/planning'
import { projectKind } from './planning'

export const projectSource = 'planning-projects'
export const projectHitLayers = ['planning-generators', 'planning-substations', 'planning-line-hit']
const planColor = '#975211'

export function projectMapData(projects: ProjectFeature[]): FeatureCollection<ProjectGeometry> {
  return {
    type: 'FeatureCollection',
    features: projects.flatMap(project => project.geometry ? [{
      type: 'Feature' as const, id: project.id, geometry: project.geometry,
      properties: { feature_id: project.id, kind: projectKind(project) },
    }] : []),
  }
}

export function addProjectLayers(map: LibreMap, projects: ProjectFeature[]) {
  map.addSource(projectSource, {
    type: 'geojson', data: projectMapData(projects),
    attribution: '<a href="https://indonesiapowermap.com/#data" target="_blank" rel="noopener">Indonesia Power Map</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>',
  })
  map.addLayer({ id: 'planning-lines', type: 'line', source: projectSource, filter: ['==', ['get', 'kind'], 'transmission'],
    paint: { 'line-color': planColor, 'line-width': ['interpolate', ['linear'], ['zoom'], 3, 1.7, 12, 4], 'line-dasharray': [3, 2] },
  }, 'primary-symbols')
  map.addLayer({ id: 'planning-line-hit', type: 'line', source: projectSource, filter: ['==', ['get', 'kind'], 'transmission'],
    paint: { 'line-width': 12, 'line-opacity': 0 },
  }, 'primary-symbols')
  const icon = document.createElement('canvas')
  icon.width = icon.height = 28
  const context = icon.getContext('2d')!
  context.fillStyle = '#fff9ed'
  context.fillRect(4, 4, 20, 20)
  context.strokeStyle = planColor
  context.lineWidth = 4
  context.strokeRect(4, 4, 20, 20)
  map.addImage('substation-work', context.getImageData(0, 0, 28, 28), { pixelRatio: 2 })
  map.addLayer({ id: 'planning-substations', type: 'symbol', source: projectSource, filter: ['==', ['get', 'kind'], 'substations'],
    layout: { 'icon-image': 'substation-work', 'icon-size': 0.9, 'icon-allow-overlap': true, 'icon-ignore-placement': true } })
  map.addLayer({ id: 'planning-generators', type: 'circle', source: projectSource, filter: ['==', ['get', 'kind'], 'generators'],
    paint: { 'circle-radius': 4.8, 'circle-color': '#fff9ed', 'circle-stroke-color': planColor, 'circle-stroke-width': 2 } })
  map.addLayer({ id: 'project-highlight-line', type: 'line', source: projectSource, filter: ['==', ['get', 'feature_id'], ''],
    paint: { 'line-color': '#edb42c', 'line-width': 6, 'line-opacity': 0.8 } }, 'planning-lines')
  map.addLayer({ id: 'project-highlight-point', type: 'circle', source: projectSource, filter: ['==', ['get', 'feature_id'], ''],
    paint: { 'circle-radius': 10, 'circle-opacity': 0, 'circle-stroke-color': '#e6a60a', 'circle-stroke-width': 3 } })
}
