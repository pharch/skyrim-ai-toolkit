const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { readActivePlugins } = require('./active-plugins');
const { parseActivePlugins, resolvePluginsTxt } = require('../ae-target');

function tmpPluginsTxt(contents) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'toolkit-ae-plugins-'));
    const file = path.join(dir, 'plugins.txt');
    fs.writeFileSync(file, contents, 'utf8');
    return file;
}

const AE_BASE = '*Skyrim.esm\n*Update.esm\n*Dawnguard.esm\n*HearthFires.esm\n*Dragonborn.esm\n';

test('only active plugins are returned, preserving their order', () => {
    const file = tmpPluginsTxt(
        AE_BASE + 'Unchecked.esp\n*Mod.esp\n'
    );
    assert.deepEqual(readActivePlugins(file), [
        'Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'HearthFires.esm', 'Dragonborn.esm', 'Mod.esp',
    ]);
});

test('CRLF and surrounding whitespace parse without altering plugin names', () => {
    assert.deepEqual(parseActivePlugins('\uFEFF' + AE_BASE.replaceAll('\n', '\r\n')), [
        'Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'HearthFires.esm', 'Dragonborn.esm',
    ]);
});

test('empty or non-AE base load orders fail rather than yielding plausible empty output', () => {
    assert.throws(() => parseActivePlugins(''), /no active plugins/);
    assert.throws(() => parseActivePlugins('*SkyrimVR.esm\n'), /begin with Skyrim\.esm/);
    assert.throws(() => parseActivePlugins('*Skyrim.esm\n'), /incomplete/);
});

test('duplicate and invalid plugin names are rejected', () => {
    assert.throws(() => parseActivePlugins('*Skyrim.esm\n*skyrim.esm\n'), /duplicate/);
    assert.throws(() => parseActivePlugins('*Skyrim.esm\n*../bad.esp\n'), /invalid/);
});

test('a missing plugin list reports an error', () => {
    assert.throws(() => readActivePlugins(path.join(os.tmpdir(), 'missing-ae-plugins.txt')));
});

test('explicit plugin-list path is resolved without scanning rival editions', () => {
    const file = tmpPluginsTxt(AE_BASE);
    assert.equal(resolvePluginsTxt({ env: { PLUGINS_TXT: file } }), file);
});

test('loadorder.txt cannot be mistaken for the active plugins.txt', () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'toolkit-ae-loadorder-'));
    const file = path.join(dir, 'loadorder.txt');
    fs.writeFileSync(file, AE_BASE);
    assert.throws(() => resolvePluginsTxt({ env: { PLUGINS_TXT: file } }), /plugins\.txt/);
});
