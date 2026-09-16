#!/usr/bin/env node

/**
 * Run the installed Mint preview with an explicit loopback-only HTTP bind.
 *
 * Mint 4.2.x exposes no bind-host option and calls `server.listen(port)`.
 * This narrow launcher supplies 127.0.0.1 only when a server in this process
 * omits its host. Explicit host/socket/options forms are left unchanged.
 */

import http from 'node:http';

const LOOPBACK = '127.0.0.1';
const originalListen = http.Server.prototype.listen;

http.Server.prototype.listen = function listenLoopback(...args) {
  if (typeof args[0] === 'number' && (args.length === 1 || typeof args[1] === 'function')) {
    args.splice(1, 0, LOOPBACK);
  } else if (
    args[0]
    && typeof args[0] === 'object'
    && !Array.isArray(args[0])
    && !Object.hasOwn(args[0], 'host')
    && !Object.hasOwn(args[0], 'path')
  ) {
    args[0] = { ...args[0], host: LOOPBACK };
  }
  return originalListen.apply(this, args);
};

process.env.HOSTNAME = LOOPBACK;

const cliStart = new URL('../node_modules/@mintlify/cli/bin/start.js', import.meta.url);
const callerArgs = process.argv.slice(2);
process.argv = [process.execPath, cliStart.pathname, 'dev', '--no-open', ...callerArgs];

console.log('Mint preview bind restricted to http://127.0.0.1 (ignore Mint\'s generic network URL label).');
await import(cliStart.href);
