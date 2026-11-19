import { expect, test, type Page, type Route } from '@playwright/test'
import { readFileSync } from 'node:fs'
import type { AssetCollection, DisplayPointCollection } from '../../src/types/assets'
import type { ProjectCollection } from '../../src/types/planning'

const read = (file: string) => JSON.parse(readFileSync('public/data/' + file, 'utf8'))
const symbols: DisplayPointCollection = read('substation-display-points.geojson')
const plants: AssetCollection = read('power-plants.geojson')
const plannedStations: ProjectCollection = read('planning/substations.geojson')
const generators: ProjectCollection = read('planning/generators.geojson')
const map = (page: Page) => page.getByTestId('map')
async function nav(page: Page, name: string) {
  const dialog = page.locator('#data-report-dialog')
  if (await dialog.isVisible()) {
    if (name !== 'Map' && await dialog.getByRole('heading', { name, exact: true }).count()) return
    await dialog.getByRole('button', { name: 'Close report' }).click()
    if (name === 'Map') return
  }
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole(name === 'Map' ? 'link' : 'button', { name, exact: true }).click()
}
const rail = (page: Page) => page.getByRole('region', { name: 'Map layers', exact: true })
const details = (page: Page) => page.getByTestId('asset-details')
const osmTiles = 'https://tile.openstreetmap.org/**'

async function start(page: Page, path = '/') {
  await page.goto(path)
  await expect(map(page)).toHaveAttribute('data-ready', 'true')
}
async function openRail(page: Page) {
  if (!await rail(page).isVisible()) await page.getByRole('button', { name: 'Open map layers' }).click()
}
async function expand(page: Page, label: string) {
  await openRail(page)
  const summary = rail(page).locator('summary').filter({ hasText: label })
  if (await summary.locator('..').getAttribute('open') === null) await summary.click()
}
async function check(page: Page, label: string, value: boolean) {
  await rail(page).getByRole('checkbox', { name: label, exact: true }).setChecked(value)
}
async function searchMap(page: Page, value: string) {
  await openRail(page)
  await rail(page).getByRole('searchbox').fill(value)
}
async function reset(page: Page) { await rail(page).getByRole('button', { name: 'Reset filters' }).click() }

function projectCoordinate(lng: number, lat: number) {
  return [(lng + 180) / 360, (1 - Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360)) / Math.PI) / 2]
}
async function mapPosition(page: Page, coordinates: number[]) {
  const view = map(page)
  const box = (await view.boundingBox())!
  const center = projectCoordinate(Number(await view.getAttribute('data-center-lng')), Number(await view.getAttribute('data-center-lat')))
  const location = projectCoordinate(coordinates[0]!, coordinates[1]!)
  const size = 512 * 2 ** Number(await view.getAttribute('data-zoom'))
  return { x: box.width / 2 + (location[0]! - center[0]!) * size, y: box.height / 2 + (location[1]! - center[1]!) * size }
}

test('map opens full-height; navigation exposes summaries, project records and attribution', async ({ page }) => {
  const calls: string[] = []
  page.on('request', r => calls.push(r.url()))
  await start(page)
  await expect(rail(page)).toBeVisible()
  await expect(page.getByTestId('line-count')).not.toBeVisible()
  await expect(page.locator('.asset-table-card')).not.toBeVisible()
  await expect(rail(page).locator('.layers-footer')).toContainText('5,599 OSM')
  expect(calls.filter(url => /planning\/.*\.geojson|substations-(review|point-candidates)/.test(url))).toHaveLength(0)
  for (const width of [1366, 1920, 390, 320]) {
    await page.setViewportSize({ width, height: 844 })
    const bounds = (await map(page).boundingBox())!
    const header = (await page.locator('header').boundingBox())!
    expect(bounds.height + header.height).toBeCloseTo(844, 0)
    expect(bounds.x + bounds.width).toBeCloseTo(width, 0)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  }
  await nav(page, 'Summary')
  for (const [key, count] of Object.entries({ line: '4,345', primary: '621', plant: '633', review: '0', point: '0' })) {
    await expect(page.getByTestId(key + '-count')).toHaveText(count)
  }
  await expect(page.locator('.viewport-count')).toHaveText(/[1-9][\d,]* rendered in viewport/)
  const summaryPanel = page.getByRole('region', { name: 'Inventory summary', exact: true })
  await expect(summaryPanel.locator('tbody tr')).toHaveCount(10)
  await expect(summaryPanel.locator('.pagination')).toBeInViewport()
  await expect(summaryPanel.locator('.pagination')).toContainText('1–10 of 5,599')
  await page.getByRole('button', { name: 'Next page' }).click()
  await expect(page.locator('.pagination')).toContainText('Page 2')
  await expect(summaryPanel.locator('.pagination')).toContainText('11–20 of 5,599')
  await page.keyboard.press('Escape')
  await page.getByRole('button', { name: 'About the data' }).click()
  const about = page.getByRole('dialog', { name: 'About the data' })
  await expect(about).toContainText('IPM’s 15 November 2026 release')
  await expect(about.getByRole('link', { name: 'ODbL 1.0' })).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(about).not.toBeVisible()
  await nav(page, 'Summary')
  await nav(page, 'RUPTL plans')
  await expect(page.getByRole('heading', { name: 'Project register 4,057' })).toBeVisible()
  await page.goBack()
  await expect(page.locator('#data-report-dialog')).not.toBeVisible()
  await page.goBack()
  await expect(page.getByRole('dialog', { name: 'Summary', exact: true })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Inventory summary', exact: true }).locator('.pagination')).toContainText('Page 2')
})

test('an empty map retains its choices and search; OSM flags and candidates stay independent', async ({ page }) => {
  const calls: string[] = []
  page.on('request', r => calls.push(r.url()))
  await start(page)
  await expand(page, 'OSM status')
  await check(page, 'Tagged construction', true)
  await check(page, 'Tagged disused', true)
  await expand(page, 'Review candidates')
  await check(page, 'Review polygons', true)
  await check(page, 'Review polygons', false)
  await check(page, 'Review polygons', true)
  await nav(page, 'Summary')
  await expect(page.getByTestId('line-count')).toHaveText('4,374')
  await expect(page.getByTestId('primary-count')).toHaveText('622')
  await expect(page.getByTestId('plant-count')).toHaveText('643')
  await expect(page.getByTestId('review-count')).toHaveText('448')
  expect(calls.filter(url => url.endsWith('/substations-review.geojson'))).toHaveLength(1)
  await nav(page, 'Map')
  await check(page, 'Power-plant footprints', false)
  for (const kV of [70, 150, 275, 500]) await check(page, kV + ' kV', false)
  await expect(rail(page).locator('.layers-footer')).toContainText('37 OSM')
  await check(page, 'Unknown voltage', false)
  await expect(rail(page).locator('.layers-empty')).toContainText('No records match')
  await page.getByRole('button', { name: 'Collapse map layers' }).click()
  await page.getByRole('button', { name: 'Open map layers' }).press('Enter')
  await expect(rail(page).getByRole('checkbox', { name: 'Review polygons' })).toBeChecked()
  await expect(rail(page).getByRole('checkbox', { name: 'Unknown voltage' })).not.toBeChecked()
  await reset(page)
  await expect(rail(page).locator('.layers-footer')).toContainText('5,599 OSM')
})

test('failed candidate retries independently; an original point remains separate from primary polygons', async ({ page }) => {
  let fail = true, requests = 0
  await page.route('**/data/substations-point-candidates.geojson', route => {
    requests++
    return fail ? route.fulfill({ status: 503 }) : route.continue()
  })
  await start(page)
  expect(requests).toBe(0)
  await expand(page, 'Review candidates')
  await check(page, 'Point-only candidates', true)
  await expect(rail(page).getByRole('alert')).toContainText('substations-point-candidates.geojson')
  fail = false
  await rail(page).getByRole('button', { name: 'Retry point candidates' }).click()
  await nav(page, 'Summary')
  await expect(page.getByTestId('point-count')).toHaveText('32')
  await expect(page.getByTestId('review-count')).toHaveText('0')
  await expect(page.getByTestId('primary-count')).toHaveText('621')
  await nav(page, 'Map')
  await check(page, 'Point-only candidates', false)
  await check(page, 'Point-only candidates', true)
  await searchMap(page, '4465682088')
  await expect(map(page)).toHaveAttribute('data-rendered-point-candidates', '1')
  await rail(page).getByRole('button', { name: /Gardu Listrik/ }).click()
  await expect(details(page)).toContainText('original source location')
  await expect(details(page)).toContainText('Nearest source polygon')
  await page.getByRole('button', { name: 'Close feature details' }).click()
  await searchMap(page, '14305665334')
  await expect(rail(page).locator('.layers-empty')).toBeVisible()
  expect(requests).toBe(2)
})

for (const kind of ['substation', 'plant'] as const) {
  test(kind + ' overview symbol opens the original footprint and preserves a single viewport record', async ({ page }) => {
    const station = symbols.features.find(f => f.properties.source_id === '-18678451')!
    const plant = plants.features.find(f => f.properties.source_id === '-21724790')!
    const stationCase = kind === 'substation'
    const id = stationCase ? station.properties.source_id : plant.properties.source_id
    const coordinates = stationCase ? station.geometry.coordinates : plant.properties.plant_representative_point!
    await start(page)
    await searchMap(page, id)
    if (!stationCase) for (const kV of [70, 150, 275, 500]) await check(page, kV + ' kV', false)
    const countAttribute = stationCase ? 'data-rendered-symbols' : 'data-rendered-plant-symbols'
    await expect(map(page)).toHaveAttribute(countAttribute, '1')
    await page.locator('.maplibregl-canvas').click({ position: await mapPosition(page, coordinates) })
    await expect(details(page)).toContainText(id)
    await expect(details(page)).toContainText(stationCase ? '500000;150000;20000' : 'Unit unspecified')
    await expect(map(page)).toHaveAttribute('data-substation-mode', 'footprints')
    await expect(map(page)).toHaveAttribute(countAttribute, '0')
    await nav(page, 'Summary')
    await expect(page.getByTestId(stationCase ? 'primary-count' : 'plant-count')).toHaveText('1')
    await expect(page.locator('.viewport-count')).toHaveText('1 rendered in viewport')
  })
}

test('sidebar stays open during pan and zoom and restores keyboard focus when collapsed', async ({ page }) => {
  await start(page)
  await expect(rail(page)).toBeVisible()
  const bounds = (await map(page).boundingBox())!
  const x = bounds.x + bounds.width * .58, y = bounds.y + bounds.height * .45
  const before = await map(page).getAttribute('data-center-lng')
  await page.mouse.move(x, y); await page.mouse.down(); await page.mouse.move(x + 70, y - 30, { steps: 8 }); await page.mouse.up()
  await expect.poll(() => map(page).getAttribute('data-center-lng')).not.toBe(before)
  const zoom = Number(await map(page).getAttribute('data-zoom'))
  await page.mouse.wheel(0, -240)
  await expect.poll(async () => Number(await map(page).getAttribute('data-zoom'))).toBeGreaterThan(zoom)
  await expect(rail(page)).toBeVisible()
  await rail(page).getByRole('checkbox', { name: 'Mapped lines' }).focus()
  await page.keyboard.press('Escape')
  const open = page.getByRole('button', { name: 'Open map layers' })
  await expect(open).toBeFocused()
  await open.press('Space')
  await expect(rail(page).getByRole('searchbox')).toBeFocused()
})

test('mobile search and details fit inside the map and keep the selected footprint clear of the drawer', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await start(page)
  await expect(rail(page)).not.toBeVisible()
  await searchMap(page, '-18678451')
  await rail(page).getByRole('button', { name: /GITET Pedan/ }).click()
  await expect(rail(page)).not.toBeVisible()
  await expect(details(page)).toBeVisible()
  const xy = symbols.features.find(f => f.properties.source_id === '-18678451')!.geometry.coordinates
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 })
    await expect.poll(async () => {
      const pt = await mapPosition(page, xy), box = (await map(page).boundingBox())!, drawer = (await details(page).boundingBox())!
      return drawer.x >= box.x && drawer.x + drawer.width <= box.x + box.width &&
        pt.x > 10 && pt.x < box.width - 10 && pt.y > 15 && pt.y < drawer.y - box.y - 8
    }).toBe(true)
    const scale = (await page.locator('.maplibregl-ctrl-scale').boundingBox())!
    const credits = (await page.locator('.maplibregl-ctrl-attrib').boundingBox())!
    expect(scale.y + scale.height <= credits.y || scale.x + scale.width <= credits.x).toBe(true)
  }
  const fields = details(page).getByRole('region', { name: 'Asset attributes' })
  await fields.focus(); await fields.press('End')
  await expect.poll(() => fields.evaluate(e => e.scrollTop)).toBeGreaterThan(0)
  await fields.press('Escape')
  await expect(details(page)).not.toBeVisible()
})

test('inventory and basemap failures remain retryable without blocking the plan register', async ({ page }) => {
  let fail = true, requests = 0
  await page.route('**/data/power-plants.geojson', r => { requests++; return fail ? r.fulfill({ status: 404 }) : r.continue() })
  await page.route(osmTiles, r => r.abort())
  await start(page)
  await expect(page.getByRole('alert')).toContainText('power-plants.geojson')
  await nav(page, 'RUPTL plans')
  await expect(page.getByRole('heading', { name: 'Project register 4,057' })).toBeVisible()
  await nav(page, 'Map')
  fail = false
  await page.getByRole('button', { name: 'Retry inventory' }).click()
  await expect(rail(page).locator('.layers-footer')).toContainText('5,599 OSM')
  expect(requests).toBe(2)
  await page.getByRole('button', { name: /Change basemap/ }).click()
  const picker = page.getByRole('dialog', { name: 'Basemap options' })
  await expect(picker.getByRole('status')).toHaveText('Tiles unavailable')
  await picker.getByText('Plain background', { exact: true }).click()
  await expect(map(page)).toHaveAttribute('data-basemap', 'plain')
  await expect(map(page)).toHaveAttribute('data-ready', 'true')
})

test('tile status appears on repeated failures and clears on recovery', async ({ page }) => {
  const pending: Route[] = []
  let requests = 0
  await page.route(osmTiles, r => { if (++requests === 1) return r.abort(); pending.push(r) })
  await start(page)
  await expect.poll(() => pending.length).toBeGreaterThanOrEqual(2)
  await page.getByRole('button', { name: /Change basemap/ }).click()
  const status = page.getByRole('dialog', { name: 'Basemap options' }).getByRole('status')
  await expect(status).toHaveCount(0)
  await page.clock.install(); await page.clock.fastForward(13000)
  await expect(status).toHaveCount(0)
  await pending.shift()!.abort()
  await expect(status).toHaveText('Tiles unavailable')
  await pending.shift()!.fulfill({ contentType: 'image/png', body: readFileSync('public/images/Mentari Logo_Tagline Revamp_Color.png') })
  await expect(status).toHaveCount(0)
  await page.keyboard.press('Escape')
  await expect(page.getByRole('button', { name: /Change basemap/ })).toBeFocused()
})

test('planned overlays load separately, retry, and survive a basemap change with their source credits', async ({ page }) => {
  let fail = true, requests = 0
  const urls: string[] = [], errors: string[] = []
  page.on('request', r => urls.push(r.url()))
  page.on('pageerror', e => errors.push(e.message))
  await page.route('**/data/planning/generators.geojson', r => { requests++; return fail ? r.fulfill({ status: 503 }) : r.continue() })
  await page.route('https://mt1.google.com/**', r => r.abort())
  await start(page)
  await check(page, 'Generation projects', true)
  await expect(rail(page).getByRole('alert')).toContainText('generators.geojson')
  fail = false
  await rail(page).getByRole('button', { name: 'Retry projects' }).click()
  await expect(rail(page).locator('.layers-footer')).toContainText('1,059 mapped projects')
  expect(urls.some(u => u.endsWith('/planning/transmission.geojson') || u.endsWith('/planning/substations.geojson'))).toBe(false)
  const project = generators.features.find(f => f.properties.source.startsWith('RUKN'))!
  await searchMap(page, project.properties.id)
  await expect(rail(page).locator('.layers-footer')).toContainText('0 OSM · 1 mapped project')
  const zoom = await map(page).getAttribute('data-zoom')
  await page.getByRole('button', { name: /Change basemap/ }).click()
  await page.getByRole('dialog', { name: 'Basemap options' }).getByText('Google Satellite', { exact: true }).click()
  await expect(map(page)).toHaveAttribute('data-basemap', 'google_satellite')
  await expect(map(page)).toHaveAttribute('data-ready', 'true')
  await expect(map(page)).toHaveAttribute('data-zoom', zoom!)
  const credits = page.locator('.maplibregl-ctrl-attrib')
  await expect(credits).toContainText('Google Maps')
  await expect(credits).toContainText('OpenStreetMap contributors')
  await expect(credits).toContainText('Indonesia Power Map')
  const xy = project.geometry!.type === 'Point' ? project.geometry!.coordinates : []
  await expect(async () => {
    await page.locator('.maplibregl-canvas').click({ position: await mapPosition(page, xy) })
    await expect(details(page)).toContainText('RUKN', { timeout: 450 })
  }).toPass({ timeout: 7500 })
  await expect(details(page)).toContainText('2045')
  await expect(details(page)).toContainText('2000 MW')
  expect(requests).toBe(2)
  expect(errors).toEqual([])
})

test('planning register distinguishes all records, mapped routes, sources and co-located projects', async ({ page }) => {
  await start(page, '/#plans')
  const heading = page.getByRole('heading', { name: /Project register/ })
  await expect(heading).toHaveText('Project register 4,057')
  await page.getByLabel('Only records without map geometry').check()
  await expect(heading).toHaveText('Project register 10')
  await expect(page.getByRole('button', { name: 'Show results on map' })).toBeDisabled()
  await page.getByRole('region', { name: 'Planning register', exact: true }).locator('tbody button').first().click()
  await expect(details(page)).toContainText('No drawable route')
  await nav(page, 'RUPTL plans')
  await expect(page.getByLabel('Only records without map geometry')).toBeChecked()
  const register = page.getByRole('region', { name: 'Planning register', exact: true })
  await register.getByRole('button', { name: 'Reset filters' }).click()
  await register.getByRole('combobox', { name: 'Plan source', exact: true }).selectOption('RUKN 2025-2060')
  await expect(heading).toHaveText('Project register 8')
  await register.getByRole('combobox', { name: 'Target COD year', exact: true }).selectOption('2045')
  await expect(heading).toHaveText('Project register 3')
  await page.getByRole('button', { name: 'Show results on map' }).click()
  await expect(rail(page).locator('.layers-footer')).toContainText('3 mapped projects')
  await expect(rail(page).getByRole('checkbox', { name: 'Substation projects' })).toBeChecked()
  await nav(page, 'RUPTL plans')
  await register.getByRole('button', { name: 'Reset filters' }).click()
  await register.getByRole('combobox', { name: 'Project type', exact: true }).selectOption('substations')
  const site = plannedStations.features.find(f => f.properties.name === 'GI eksisting/baru Jawa Tengah')!
  await page.getByRole('searchbox', { name: 'Search projects' }).fill(site.properties.name)
  await register.locator('tbody button').first().click()
  const choices = details(page).getByRole('combobox', { name: /Projects at these coordinates/ })
  await expect(choices).toBeVisible()
  const sourceId = await choices.locator('option').nth(1).getAttribute('value')
  await choices.selectOption(sourceId!)
  await expect(details(page)).toContainText(sourceId!.split(':').pop()!)
})

test('report modal traps focus, dismisses with Escape and backdrop, and preserves the selected map feature', async ({ page }) => {
  await start(page)
  await searchMap(page, '-18678451')
  await rail(page).getByRole('button', { name: /GITET Pedan/ }).click()
  await expect(map(page)).toHaveAttribute('data-substation-mode', 'footprints')
  const zoom = await map(page).getAttribute('data-zoom')
  const trigger = page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button', { name: 'Summary', exact: true })
  await trigger.focus()
  await trigger.press('Enter')
  const dialog = page.getByRole('dialog', { name: 'Summary', exact: true })
  await expect(dialog).toBeVisible()
  expect(await dialog.evaluate(element => element.matches(':modal'))).toBe(true)
  await expect(map(page)).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'Summary', exact: true })).toBeFocused()
  const lastControl = dialog.getByRole('button', { name: /GITET Pedan/ })
  await lastControl.focus()
  await page.keyboard.press('Tab')
  await expect(dialog.getByRole('button', { name: 'Close report' })).toBeFocused()
  await page.keyboard.press('Shift+Tab')
  await expect(lastControl).toBeFocused()
  await page.keyboard.press('Escape')
  await expect(dialog).not.toBeVisible()
  await expect(trigger).toBeFocused()
  await expect(details(page)).toContainText('GITET Pedan')
  await expect(map(page)).toHaveAttribute('data-zoom', zoom!)
  await trigger.click()
  await dialog.locator('.page-content').click({ position: { x: 8, y: 8 } })
  await expect(dialog).toBeVisible()
  await page.mouse.click(5, 5)
  await expect(dialog).not.toBeVisible()
  await expect(trigger).toBeFocused()
  await page.goBack()
  await expect(dialog).toBeVisible()
  await page.goForward()
  await expect(dialog).not.toBeVisible()
})

test('mobile report stays within the screen and its shared search selects a footprint on the map', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await start(page, '/#summary')
  const dialog = page.getByRole('dialog', { name: 'Summary', exact: true })
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 })
    const bounds = (await dialog.boundingBox())!
    expect(bounds.x).toBe(0)
    expect(bounds.width).toBe(width)
    expect(bounds.height).toBe(844)
    await expect(dialog.getByRole('button', { name: 'Close report' })).toBeInViewport()
    await dialog.locator('.report-panel:visible').evaluate(element => { element.scrollTop = element.scrollHeight })
    await expect(dialog.getByRole('button', { name: 'Close report' })).toBeInViewport()
    expect(await dialog.evaluate(element => element.scrollWidth <= element.clientWidth)).toBe(true)
  }
  await dialog.getByRole('searchbox', { name: 'Search inventory records' }).fill('-18678451')
  await expect(page.getByTestId('primary-count')).toHaveText('1')
  await expect(map(page)).toHaveAttribute('data-rendered-symbols', '1')
  await dialog.getByRole('button', { name: /GITET Pedan/ }).click()
  await expect(dialog).not.toBeVisible()
  await expect(details(page)).toContainText('GITET Pedan')
  await expect(page.getByRole('button', { name: 'Close feature details' })).toBeFocused()
  await nav(page, 'Summary')
  await expect(dialog.getByRole('searchbox', { name: 'Search inventory records' })).toHaveValue('-18678451')
  await dialog.getByRole('button', { name: /GITET Pedan/ }).click()
  await expect(dialog).not.toBeVisible()
  await expect(page.getByRole('button', { name: 'Close feature details' })).toBeFocused()
  await nav(page, 'Summary')
  await dialog.getByRole('button', { name: 'Map filters' }).click()
  await expect(rail(page)).toBeVisible()
  await expect(rail(page).getByRole('searchbox')).toHaveValue('-18678451')
})
