/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

const { writeFileSync } = require('fs');
const util = require('node:util');
const exec = util.promisify(require('node:child_process').exec);

if (process.env.http_proxy) {
  const { setGlobalDispatcher, ProxyAgent } = require('undici');

  setGlobalDispatcher(new ProxyAgent(process.env.http_proxy));
}

async function main() {
  const git = exec('git describe --tags', {
    cwd: __dirname,
  });
  const gitTag = exec('git describe --tags --abbrev=0', {
    cwd: __dirname,
  });

  const gitResponse = await git;
  console.error(gitResponse.stderr);
  const gitTagResponse = await gitTag;
  console.error(gitTagResponse.stderr);

  if (gitTagResponse.error || gitResponse.error) {
    process.exit(1);
  }

  const json = {
    git: {
      version: gitResponse.stdout.replace(/\n/g, ''),
      tag: gitTagResponse.stdout.replace(/\n/g, ''),
    },
  };

  writeFileSync(__dirname + '/src/assets/version.json', JSON.stringify(json));
}

main();
