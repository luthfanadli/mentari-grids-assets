import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('../../', import.meta.url))

test('publication bytes and checksums survive Git staging and Windows/Linux checkout settings', () => {
  const temporary = mkdtempSync(join(tmpdir(), 'mentari-publication-git-'))
  const repository = join(temporary, 'repository')
  mkdirSync(join(repository, 'public/data'), { recursive: true })
  mkdirSync(join(repository, 'scripts'))
  const files = readdirSync(join(root, 'public/data')).map(name => `public/data/${name}`)
  const git = (...args: string[]) => execFileSync('git', args, {
    cwd: repository, stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 16 * 1024 * 1024,
  })
  try {
    for (const name of ['scripts/check_public_data.mjs', ...files]) {
      copyFileSync(join(root, name), join(repository, name))
    }
    git('init', '--quiet')
    git('-c', 'core.autocrlf=true', 'add', '--', 'scripts', 'public')
    const lineFile = 'public/data/transmission-lines.geojson'
    assert.equal(git('show', `:${lineFile}`).length, readFileSync(join(root, lineFile)).length - 1,
      'The fixture must reproduce the original one-byte loss before applying the fix')
    copyFileSync(join(root, '.gitattributes'), join(repository, '.gitattributes'))
    git('add', '--', '.gitattributes')
    git('-c', 'core.autocrlf=true', 'add', '--renormalize', '--', 'public/data')
    for (const name of files) {
      assert.deepEqual(git('show', `:${name}`), readFileSync(join(root, name)), `${name}: Git staging changed publication bytes`)
    }
    for (const autocrlf of ['false', 'true']) {
      const checkout = join(temporary, `checkout-${autocrlf}`)
      // An empty checkout with autocrlf=false reproduces the Linux CI settings;
      // autocrlf=true also verifies a fresh Windows checkout of the same index.
      git('-c', `core.autocrlf=${autocrlf}`, 'checkout-index', '--all', `--prefix=${checkout.replaceAll('\\', '/')}/`)
      for (const name of files) {
        assert.deepEqual(readFileSync(join(checkout, name)), readFileSync(join(root, name)), `${name}: checkout changed publication bytes (autocrlf=${autocrlf})`)
      }
      const output = execFileSync(process.execPath, [join(checkout, 'scripts/check_public_data.mjs')], { encoding: 'utf8' })
      assert.match(output, /Publication checks passed/)
    }
  } finally {
    rmSync(temporary, { recursive: true, force: true })
  }
})
