import { computed, ref, shallowRef } from 'vue'
import type { AssetFeature, DisplayPointCollection, InventorySummary } from '../types/assets'
import { createAssetRepository } from '../services/assetData'
import { defaultFilters, filterAssets, selectionCounts, uniqueInventoryFeatures } from '../utils/filterAssets'
import { selectedDisplayPoints } from '../utils/substationPresentation'
export function useAssetFilters() {
  const repository = createAssetRepository()
  const baseFeatures = shallowRef<AssetFeature[]>([]), reviewFeatures = shallowRef<AssetFeature[]>([])
  const pointFeatures = shallowRef<AssetFeature[]>([])
  const displayPoints = shallowRef<DisplayPointCollection>({ type: 'FeatureCollection', features: [] })
  const summary = shallowRef<InventorySummary | null>(null), filters = ref(defaultFilters())
  const loading = ref(true), error = ref(''), reviewLoading = ref(false), reviewError = ref('')
  const pointLoading = ref(false), pointError = ref('')
  const selectedFeatures = computed(() => uniqueInventoryFeatures(filterAssets([...baseFeatures.value, ...reviewFeatures.value, ...pointFeatures.value], filters.value)))
  const selectedSymbols = computed(() => selectedDisplayPoints(displayPoints.value, selectedFeatures.value))
  const counts = computed(() => selectionCounts(selectedFeatures.value))
  async function load() {
    loading.value = true; error.value = ''
    try {
      const data = await repository.loadBase()
      baseFeatures.value = [...data.lines.features, ...data.primary.features, ...data.powerPlants.features]; summary.value = data.summary
      displayPoints.value = data.displayPoints
    } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Inventory could not be loaded.' }
    finally { loading.value = false }
  }
  async function loadReview() {
    if (reviewLoading.value) return
    reviewLoading.value = true; reviewError.value = ''
    try {
      const collection = await repository.loadReview()
      if (summary.value && collection.features.length !== summary.value.datasets.review.count) throw new Error('Review candidate count differs from summary.json. Redeploy the complete dataset.')
      reviewFeatures.value = collection.features
    } catch (cause) { reviewError.value = cause instanceof Error ? cause.message : 'Candidates could not be loaded.' }
    finally { reviewLoading.value = false }
  }
  async function loadPointCandidates() {
    if (pointLoading.value) return
    pointLoading.value = true; pointError.value = ''
    try {
      const collection = await repository.loadPointCandidates()
      if (summary.value && collection.features.length !== summary.value.datasets.point_candidates.count) throw new Error('Point-only count differs from summary.json. Use the complete dataset from one preprocessing run.')
      pointFeatures.value = collection.features
    } catch (cause) { pointError.value = cause instanceof Error ? cause.message : 'Point-only candidates could not be loaded.' }
    finally { pointLoading.value = false }
  }
  return { filters, summary, loading, error, reviewLoading, reviewError, pointLoading, pointError, selectedFeatures, selectedSymbols, counts, load, loadReview, loadPointCandidates, reset: () => { filters.value = defaultFilters() } }
}
