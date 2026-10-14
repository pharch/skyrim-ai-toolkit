// Resolve the explicit Skyrim AE (or MO2 profile) load order before xEdit sees it.
const fs = require('fs');
const path = require('path');
const { assertAETarget, parseActivePlugins, resolvePluginsTxt } = require('../ae-target');

function defaultPluginsTxt() {
    const target = assertAETarget();
    return resolvePluginsTxt({ gameRoot: target.gameRoot });
}

function readActivePlugins(pluginsTxt = defaultPluginsTxt()) {
    return parseActivePlugins(fs.readFileSync(pluginsTxt, 'utf8'));
}

function loadActive(xelib, { smartLoad = true, buildRefs = false, pluginsTxt } = {}) {
    const target = assertAETarget();
    const orderFile = pluginsTxt
        ? resolvePluginsTxt({
            env: { ...process.env, PLUGINS_TXT: path.resolve(pluginsTxt) },
            gameRoot: target.gameRoot,
        })
        : resolvePluginsTxt({ gameRoot: target.gameRoot });
    const active = readActivePlugins(orderFile);
    xelib.loadPlugins(active.join('\n'), smartLoad, buildRefs);
    return active;
}

module.exports = { readActivePlugins, loadActive, defaultPluginsTxt };
