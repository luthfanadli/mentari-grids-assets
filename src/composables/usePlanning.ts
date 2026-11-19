import { computed, reactive, ref, shallowRef, watch, type Ref } from 'vue'
import type { AssetFilters } from '../types/assets'
import { planningKinds, type PlanningCatalog, type PlanningKind, type ProjectFeature } from '../types/planning'
import type { createAssetRepository } from '../services/assetData'
import { defaultPlanFilters, matchesProject } from '../utils/planning'

export function usePlanning(repository: ReturnType<typeof createAssetRepository>, filters: Ref<AssetFilters>) {
  const catalog = shallowRef<PlanningCatalog | null>(null)
  const catalogError = ref('')
  const records = shallowRef<Partial<Record<PlanningKind, ProjectFeature[]>>>({})
  const loading = reactive<Partial<Record<PlanningKind, boolean>>>({})
  const errors = reactive<Partial<Record<PlanningKind, string>>>({})
  const enabled = ref<PlanningKind[]>([])
  const criteria = ref(defaultPlanFilters())
  const matching = computed(() => {
    const select = (kind: PlanningKind) => (records.value[kind] ?? []).filter(f => matchesProject(f, filters.value, criteria.value))
    return { transmission: select('transmission'), substations: select('substations'), generators: select('generators') }
  })
  const visible = computed(() => enabled.value.flatMap(kind => matching.value[kind]))
  async function loadCatalog() {
    catalogError.value = ''
    try { catalog.value = await repository.loadPlanningCatalog() }
    catch (cause) { catalogError.value = cause instanceof Error ? cause.message : 'Planning catalogue unavailable.' }
  }
  async function loadLayer(kind: PlanningKind) {
    if (records.value[kind] || loading[kind]) return
    loading[kind] = true
    errors[kind] = ''
    try {
      const collection = await repository.loadProjects(kind)
      records.value = { ...records.value, [kind]: collection.features }
      if (!catalog.value) await loadCatalog()
    } catch (cause) {
      errors[kind] = cause instanceof Error ? cause.message : 'Planning layer unavailable.'
    } finally { loading[kind] = false }
  }
  watch(enabled, kinds => kinds.forEach(kind => void loadLayer(kind)), { deep: true })
  function loadAll() {
    void loadCatalog()
    for (const kind of planningKinds) void loadLayer(kind)
  }
  function reset() {
    enabled.value = []
    criteria.value = defaultPlanFilters()
  }
  return { catalog, catalogError, enabled, criteria, loading, errors, matching, visible, loadCatalog, loadLayer, loadAll, reset }
}
