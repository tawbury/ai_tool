#!/usr/bin/env node

import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import chalk from 'chalk';
import { initCommand } from './commands/init';
import { installCommand } from './commands/install';
import { syncCommand } from './commands/sync';

const cli = yargs(hideBin(process.argv))
  .scriptName('mcp')
  .version('0.1.0')
  .strict()
  .help()
  .alias('h', 'help')
  .alias('v', 'version')

  // mcp init command
  .command(
    'init [directory]',
    'Initialize a new MCP OS project',
    (yargsBuilder: any) => {
      return yargsBuilder
        .positional('directory', {
          describe: 'Project directory to initialize',
          type: 'string',
          default: '.'
        })
        .option('force', {
          describe: 'Force initialization even if directory exists',
          type: 'boolean',
          default: false
        })
        .option('verbose', {
          describe: 'Verbose output',
          type: 'boolean',
          default: false
        });
    },
    initCommand as any
  )

  // mcp install command
  .command(
    'install',
    'Install IDE AI tool configurations',
    (yargsBuilder: any) => {
      return yargsBuilder
        .option('all-tools', {
          describe: 'Install all IDE tool configurations',
          type: 'boolean',
          default: false
        })
        .option('tools', {
          describe: 'Specific tools to install (copilot, claude, cursor, windsurf)',
          type: 'array',
          default: []
        })
        .option('verbose', {
          describe: 'Verbose output',
          type: 'boolean',
          default: false
        });
    },
    installCommand as any
  )

  // mcp sync command
  .command(
    'sync',
    'Synchronize .ai/ changes to generated files',
    (yargsBuilder: any) => {
      return yargsBuilder
        .option('force', {
          describe: 'Force regeneration of all files',
          type: 'boolean',
          default: false
        })
        .option('check', {
          describe: 'Only check for changes, do not regenerate',
          type: 'boolean',
          default: false
        })
        .option('verbose', {
          describe: 'Verbose output',
          type: 'boolean',
          default: false
        });
    },
    syncCommand as any
  )

  .showHelpOnFail(true)
  .epilogue('For more information, visit https://github.com/anthropics/mcp-os');

async function main() {
  try {
    await cli.parse();
  } catch (error) {
    if (error instanceof Error) {
      console.error(chalk.red(`✗ Error: ${error.message}`));
    } else {
      console.error(chalk.red('✗ An unknown error occurred'));
    }
    process.exit(1);
  }
}

main().catch(() => {
  process.exit(1);
});
