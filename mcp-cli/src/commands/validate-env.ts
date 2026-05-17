import chalk from 'chalk';
import fs from 'fs';
import { detectPaths } from '../utils/paths';
import { validatePermissions } from '../utils/permissions';
import { validateEncoding } from '../utils/encoding';
import { AIOSLock } from '../utils/lock';

export async function validateEnvCommand(argv: any) {
  console.log(chalk.cyan('🔍 AI OS Environment Validation...'));
  console.log('---');

  const paths = detectPaths();
  const results = {
    paths: [] as any[],
    permissions: [] as any[],
    locks: [] as any[],
  };

  // 1. Path & Permission Check
  const targets = [
    { name: 'AIOS Home', path: paths.home },
    { name: 'AI OS Core (.ai)', path: paths.ai },
    { name: 'Codex Config', path: paths.codex },
    { name: 'Claude Config', path: paths.claude },
    { name: 'Gemini Config', path: paths.gemini },
  ];

  for (const target of targets) {
    const exists = fs.existsSync(target.path);
    const perm = exists ? validatePermissions(target.path) : { readable: false, writable: false, error: 'Directory missing' };
    
    console.log(`${chalk.bold(target.name)}: ${target.path}`);
    if (exists) {
      const status = perm.writable ? chalk.green('✓ OK') : chalk.red(`✗ ${perm.error}`);
      console.log(`  Status: ${status}`);
    } else {
      console.log(`  Status: ${chalk.yellow('⚠ Missing')}`);
    }
  }

  // 2. Lock System Check
  console.log('\n' + chalk.cyan('🔒 Lock System Status:'));
  const globalLock = new AIOSLock(paths.ai);
  const isLocked = globalLock.isLocked();
  console.log(`  Global Lock: ${isLocked ? chalk.yellow('Locked') : chalk.green('Available')}`);

  // 3. Encoding Check (sample check on README if exists)
  console.log('\n' + chalk.cyan('📄 Encoding Enforcement Check:'));
  const sampleFile = 'README.md';
  if (fs.existsSync(sampleFile)) {
    const enc = validateEncoding(sampleFile);
    console.log(`  Sample (${sampleFile}): ${enc.valid ? chalk.green('✓ ' + enc.message) : chalk.red('✗ ' + enc.message)}`);
  } else {
    console.log(`  Sample: ${chalk.yellow('No sample file found to check')}`);
  }

  console.log('\n---');
  console.log(chalk.cyan('✅ Validation Complete.'));
}
