import { defineConfig, devices } from '@playwright/test'
const externalPreview = process.env.PLAYWRIGHT_BASE_URL
export default defineConfig({
  testDir: './tests/e2e', fullyParallel: false, workers: 1, timeout: 45000,
  use: { baseURL: externalPreview || 'http://127.0.0.1:5174', trace: 'retain-on-failure',
    ...devices['Desktop Chrome'], channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
    launchOptions: { args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader'] } },
  webServer: externalPreview ? undefined : { command: 'pnpm dev --host 127.0.0.1', url: 'http://127.0.0.1:5174', reuseExistingServer: !process.env.CI },
})
