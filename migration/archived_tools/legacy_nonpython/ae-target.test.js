const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
    assertAETarget, parseVersion, readExecutableVersion, REQUIRED_AE_MASTERS,
} = require('./ae-target');

function fixture() {
    const gameRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'skyrim-ae-target-'));
    const executable = path.join(gameRoot, 'SkyrimSE.exe');
    fs.writeFileSync(executable, 'fixture');
    return { gameRoot, executable };
}

test('strictly accepts an AE executable version read from its injected reader', () => {
    const { gameRoot, executable } = fixture();
    const target = assertAETarget({
        env: { SKYRIM_EDITION: 'AE', GAME_ROOT: gameRoot },
        versionReader: file => {
            assert.equal(file, executable);
            return '1.6.1170.0';
        },
    });
    assert.equal(target.edition, 'AE');
    assert.equal(target.version, '1.6.1170');
});

test('rejects missing/non-AE edition declarations and pre-AE runtimes', () => {
    const { gameRoot } = fixture();
    assert.throws(() => assertAETarget({
        env: { GAME_ROOT: gameRoot },
        versionReader: () => '1.6.1170.0',
    }), /SKYRIM_EDITION/);
    assert.throws(() => assertAETarget({
        env: { SKYRIM_EDITION: 'VR', GAME_ROOT: gameRoot },
        versionReader: () => '1.6.1170.0',
    }), /SKYRIM_EDITION/);
    assert.throws(() => assertAETarget({
        env: { SKYRIM_EDITION: 'AE', GAME_ROOT: gameRoot },
        versionReader: () => '1.5.97.0',
    }), /1\.6\.318/);
});

test('rejects wrong executable names, missing executables, and invalid versions', () => {
    const { gameRoot, executable } = fixture();
    assert.throws(() => assertAETarget({
        env: { SKYRIM_EDITION: 'AE', GAME_ROOT: gameRoot, SKYRIM_EXE_PATH: path.join(gameRoot, 'SkyrimVR.exe') },
        versionReader: () => '1.6.1170.0',
    }), /SkyrimSE\.exe/);
    assert.throws(() => assertAETarget({
        env: { SKYRIM_EDITION: 'AE', GAME_ROOT: gameRoot, SKYRIM_EXE_PATH: path.join(os.tmpdir(), 'SkyrimSE.exe') },
        versionReader: () => '1.6.1170.0',
    }), /inside GAME_ROOT/);
    assert.throws(() => assertAETarget({
        env: { SKYRIM_EDITION: 'AE', GAME_ROOT: gameRoot },
        versionReader: () => 'unknown',
    }), /cannot parse/);
    assert.equal(fs.existsSync(executable), true);
});

test('version parser fails closed outside numeric runtime metadata', () => {
    assert.deepEqual(parseVersion('1.6.640.0'), [1, 6, 640]);
    assert.throws(() => parseVersion('Skyrim AE'), /cannot parse/);
});

test('native executable inspection refuses non-Windows instead of trusting a version string', () => {
    assert.throws(() => readExecutableVersion('/fake/SkyrimSE.exe', 'linux'), /requires Windows/);
});

test('AE load-order baseline is explicit and requires the full official master set', () => {
    assert.deepEqual(REQUIRED_AE_MASTERS, [
        'Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'HearthFires.esm', 'Dragonborn.esm',
    ]);
});
