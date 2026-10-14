// Fail-closed target resolution for Skyrim Anniversary Edition (runtime 1.6.318+).
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const MIN_AE_VERSION = [1, 6, 318];
const REQUIRED_AE_MASTERS = [
    'Skyrim.esm',
    'Update.esm',
    'Dawnguard.esm',
    'HearthFires.esm',
    'Dragonborn.esm',
];

function localConfig() {
    const file = path.resolve(__dirname, '..', 'config', 'local.env');
    const values = {};
    if (!fs.existsSync(file)) return values;
    for (const raw of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
        const line = raw.trim();
        if (!line || line.startsWith('#') || !line.includes('=')) continue;
        const index = line.indexOf('=');
        const key = line.slice(0, index).trim();
        const value = line.slice(index + 1).trim().replace(/^(['"])(.*)\1$/, '$2');
        values[key] = value;
    }
    return values;
}

function settings(env = process.env) {
    return { ...localConfig(), ...env };
}

function parseVersion(value) {
    const match = String(value || '').match(/(?:^|[^\d])(\d+)\.(\d+)\.(\d+)(?:\.\d+)?(?:$|[^\d])/);
    if (!match) throw new Error(`cannot parse Skyrim executable version: ${JSON.stringify(value)}`);
    return match.slice(1).map(Number);
}

function compareVersion(left, right) {
    for (let i = 0; i < 3; i++) {
        if (left[i] !== right[i]) return left[i] - right[i];
    }
    return 0;
}

function readExecutableVersion(executable, platform = process.platform) {
    if (platform !== 'win32') {
        throw new Error('Skyrim AE executable version inspection requires Windows; no version was verified');
    }
    const result = spawnSync('powershell.exe', [
        '-NoProfile', '-NonInteractive', '-Command',
        "$ErrorActionPreference='Stop'; [Diagnostics.FileVersionInfo]::GetVersionInfo($env:SKYRIM_EXE_PATH).ProductVersion",
    ], {
        encoding: 'utf8',
        env: { ...process.env, SKYRIM_EXE_PATH: executable },
        windowsHide: true,
    });
    if (result.error || result.status !== 0) {
        throw new Error(`could not read Skyrim executable version: ${result.error?.message || result.stderr.trim()}`);
    }
    return result.stdout.trim();
}

function assertAETarget({ env = process.env, versionReader = readExecutableVersion } = {}) {
    const config = settings(env);
    if (config.SKYRIM_EDITION !== 'AE') {
        throw new Error('SKYRIM_EDITION must be explicitly set to AE');
    }
    if (!config.GAME_ROOT) throw new Error('GAME_ROOT must point to the Skyrim AE installation');

    const gameRoot = path.resolve(config.GAME_ROOT);
    const executable = path.resolve(config.SKYRIM_EXE_PATH || path.join(gameRoot, 'SkyrimSE.exe'));
    if (path.basename(executable).toLowerCase() !== 'skyrimse.exe') {
        throw new Error('AE target executable must be SkyrimSE.exe');
    }
    const relative = path.relative(gameRoot, executable);
    if (!relative || relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
        throw new Error('SkyrimSE.exe must be inside GAME_ROOT');
    }
    if (!fs.statSync(gameRoot).isDirectory()) throw new Error(`GAME_ROOT is not a directory: ${gameRoot}`);
    if (!fs.statSync(executable).isFile()) throw new Error(`Skyrim executable is not a file: ${executable}`);

    const versionText = versionReader(executable);
    const version = parseVersion(versionText);
    if (version[0] !== 1 || version[1] !== 6 || compareVersion(version, MIN_AE_VERSION) < 0) {
        throw new Error(`unsupported Skyrim runtime ${versionText}; AE runtime 1.6.318 or newer is required`);
    }

    return { edition: 'AE', gameRoot, executable, version: version.join('.') };
}

function resolvePluginsTxt({ env = process.env, gameRoot } = {}) {
    const config = settings(env);
    const configured = config.PLUGINS_TXT
        || (config.SKYRIM_LOADORDER_DIR && path.join(config.SKYRIM_LOADORDER_DIR, 'plugins.txt'));
    const localAppData = config.LOCALAPPDATA
        || (config.USERPROFILE && path.join(config.USERPROFILE, 'AppData', 'Local'));
    const candidate = configured || (localAppData && path.join(localAppData, 'Skyrim Special Edition', 'plugins.txt'));
    if (!candidate) throw new Error('set PLUGINS_TXT to the Skyrim AE or MO2 profile plugins.txt');
    if (!path.isAbsolute(candidate)) throw new Error('PLUGINS_TXT must be an absolute path');
    const file = path.resolve(candidate);
    if (path.basename(file).toLowerCase() !== 'plugins.txt') {
        throw new Error('PLUGINS_TXT must name the active plugins.txt, not loadorder.txt or another file');
    }
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
        throw new Error(`active plugin list not found: ${file}; set PLUGINS_TXT to the AE/MO2 profile list`);
    }
    if (gameRoot) {
        const normalized = path.resolve(gameRoot);
        if (file === normalized || file.startsWith(normalized + path.sep)) {
            throw new Error('PLUGINS_TXT must be the active profile list, not a file inside GAME_ROOT');
        }
    }
    return file;
}

function parseActivePlugins(text) {
    const active = String(text).replace(/^\uFEFF/, '').split(/\r?\n/)
        .map(line => line.trim())
        .filter(line => line.startsWith('*'))
        .map(line => line.slice(1).trim())
        .filter(Boolean);
    if (active.length === 0) throw new Error('active plugin list contains no active plugins');
    if (active[0].toLowerCase() !== 'skyrim.esm') {
        throw new Error('active plugin list must begin with Skyrim.esm');
    }
    const seen = new Set();
    for (const name of active) {
        if (!/^[^\\/:*?"<>|]+\.(?:esm|esp|esl)$/i.test(name)) {
            throw new Error(`invalid active plugin name: ${name}`);
        }
        const key = name.toLowerCase();
        if (seen.has(key)) throw new Error(`duplicate active plugin: ${name}`);
        seen.add(key);
    }

    const folded = new Set(active.map(name => name.toLowerCase()));
    const missingMasters = REQUIRED_AE_MASTERS.filter(name => !folded.has(name.toLowerCase()));
    if (missingMasters.length) {
        throw new Error(`active plugin list is incomplete; missing required AE masters: ${missingMasters.join(', ')}`);
    }
    return active;
}

module.exports = {
    assertAETarget,
    compareVersion,
    parseActivePlugins,
    parseVersion,
    readExecutableVersion,
    REQUIRED_AE_MASTERS,
    resolvePluginsTxt,
};
