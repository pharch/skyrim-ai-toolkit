#!/usr/bin/env node
const crypto = require('crypto');
const fs = require('fs');
const { assertAETarget, parseActivePlugins, resolvePluginsTxt } = require('./ae-target');

try {
    const target = assertAETarget();
    if (process.argv.includes('--game-root')) {
        process.stdout.write(`${target.gameRoot}\n`);
        process.exit(0);
    }
    const pluginsPath = resolvePluginsTxt({ gameRoot: target.gameRoot });
    const loadOrderBytes = fs.readFileSync(pluginsPath);
    const plugins = parseActivePlugins(loadOrderBytes.toString('utf8'));
    const executableSha256 = crypto.createHash('sha256')
        .update(fs.readFileSync(target.executable))
        .digest('hex');
    process.stdout.write(`${JSON.stringify({
        edition: target.edition,
        runtime: target.version,
        executableSha256,
        activePlugins: plugins.length,
        basePlugin: plugins[0],
        loadOrder: pluginsPath,
        loadOrderSha256: crypto.createHash('sha256').update(loadOrderBytes).digest('hex'),
        liveRuntimeTested: false,
    }, null, 2)}\n`);
} catch (error) {
    process.stderr.write(`AE preflight failed: ${error.message}\n`);
    process.exitCode = 1;
}
