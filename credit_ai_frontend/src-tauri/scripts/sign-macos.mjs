import { spawnSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, rmSync, symlinkSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const srcTauri = join(here, '..')
const entitlements = join(srcTauri, 'entitlements.plist')

function run(command, args) {
  const result = spawnSync(command, args, { stdio: 'inherit' })
  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }
}

function sign(target, identifier) {
  const args = [
    '--force',
    '--sign',
    '-',
    '--timestamp=none',
    '--entitlements',
    entitlements,
  ]
  if (identifier) {
    args.push('--identifier', identifier)
  }
  args.push(target)
  run('codesign', args)
}

function findApp() {
  const candidates = []
  if (process.env.CARGO_TARGET_DIR) {
    candidates.push(join(process.env.CARGO_TARGET_DIR, 'release/bundle/macos/Kuber.app'))
  }
  candidates.push(join(srcTauri, 'target/release/bundle/macos/Kuber.app'))
  return candidates.find((path) => existsSync(path))
}

function createDmg(appPath) {
  const outDir = join(dirname(appPath), '../dmg')
  mkdirSync(outDir, { recursive: true })
  const dmgPath = join(outDir, 'Kuber-0.1.0-macos-arm64.dmg')
  const stage = join(tmpdir(), `kuber-dmg-${Date.now()}`)
  mkdirSync(stage, { recursive: true })
  try {
    cpSync(appPath, join(stage, 'Kuber.app'), { recursive: true })
    symlinkSync('/Applications', join(stage, 'Applications'))
    rmSync(dmgPath, { force: true })
    run('hdiutil', [
      'create',
      '-volname',
      'Kuber',
      '-srcfolder',
      stage,
      '-ov',
      '-format',
      'UDZO',
      dmgPath,
    ])
  } finally {
    rmSync(stage, { recursive: true, force: true })
  }
  run('codesign', ['--force', '--sign', '-', '--timestamp=none', dmgPath])
  console.log(`installer ${dmgPath}`)
}

const target = process.argv[2] || findApp()
if (!target) {
  console.error('usage: node sign-macos.mjs <binary-or-app>')
  process.exit(1)
}

const path = resolve(target)
if (!existsSync(path)) {
  console.error(`missing: ${path}`)
  process.exit(1)
}

if (path.endsWith('.app')) {
  const sidecar = join(path, 'Contents/Resources/binaries/reasoning-layer')
  if (existsSync(sidecar)) {
    sign(sidecar, 'com.kuber.reasoning-layer')
  }
  sign(path, 'com.kuber.credit-ai')
  createDmg(path)
  rmSync(path, { recursive: true, force: true })
  console.log(`removed ${path}`)
} else if (path.endsWith('.dmg')) {
  run('codesign', ['--force', '--sign', '-', '--timestamp=none', path])
} else {
  sign(path, 'com.kuber.reasoning-layer')
}

console.log(`signed ${path}`)
