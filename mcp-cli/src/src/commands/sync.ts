import chalk from 'chalk';
import ora from 'ora';
import path from 'path';
import {
  readFile,
  writeFile,
  fileExists,
  getMappingRulesPath,
  getProjectRoot,
  getTimestamp,
  renderTemplate
} from '../utils/file';
import { loadMappingRules, getEnabledTools, getToolConfig } from '../utils/yaml';
import fs from 'fs-extra';

export interface SyncArgs {
  force: boolean;
  check: boolean;
  verbose: boolean;
}

export async function syncCommand(argv: SyncArgs): Promise<void> {
  const projectRoot = getProjectRoot();
  const verbose = argv.verbose || false;
  const force = argv.force || false;
  const checkOnly = argv.check || false;

  console.log(chalk.cyan('\n🔄 MCP OS Synchronization\n'));

  const spinner = ora();

  try {
    // Load mapping rules
    spinner.start(chalk.cyan('Loading mapping rules...'));
    const mappingRulesPath = getMappingRulesPath(projectRoot);
    const mappingRules = await loadMappingRules(mappingRulesPath);
    spinner.succeed(chalk.green('Mapping rules loaded'));

    // Get enabled tools
    const toolsToSync = getEnabledTools(mappingRules);

    if (checkOnly) {
      await checkChanges(projectRoot, toolsToSync, mappingRules, verbose);
    } else {
      await syncTools(projectRoot, toolsToSync, mappingRules, force, verbose);
    }

  } catch (error) {
    spinner.fail(chalk.red('Synchronization failed'));
    if (error instanceof Error) {
      console.error(chalk.red(`✗ ${error.message}`));
    }
    process.exit(1);
  }
}

async function checkChanges(
  projectRoot: string,
  toolsToSync: string[],
  mappingRules: any,
  verbose: boolean
): Promise<void> {
  console.log(chalk.cyan('\n🔍 Checking for changes...\n'));

  let changesFound = false;

  for (const toolName of toolsToSync) {
    const toolConfig = getToolConfig(mappingRules, toolName);
    if (!toolConfig) continue;

    const templatePath = path.join(projectRoot, toolConfig.template);
    const outputPath = path.join(projectRoot, toolConfig.output_path);

    const templateExists = await fileExists(templatePath);
    const outputExists = await fileExists(outputPath);

    if (!templateExists) {
      console.log(chalk.yellow(`⚠ Template not found for ${toolName}: ${toolConfig.template}`));
      changesFound = true;
    } else if (!outputExists) {
      console.log(chalk.yellow(`⚠ Output file will be created: ${toolConfig.output_path}`));
      changesFound = true;
    } else {
      // Compare timestamps to detect changes
      const templateStats = await fs.stat(templatePath);
      const outputStats = await fs.stat(outputPath);

      if (templateStats.mtime > outputStats.mtime) {
        console.log(chalk.yellow(`⚠ Changes detected in: ${toolConfig.output_path}`));
        changesFound = true;
      }
    }
  }

  if (!changesFound) {
    console.log(chalk.green('✓ No changes detected. All files are up to date.\n'));
  } else {
    console.log(chalk.cyan('\nRun "mcp sync" to apply changes.\n'));
  }
}

async function syncTools(
  projectRoot: string,
  toolsToSync: string[],
  mappingRules: any,
  force: boolean,
  verbose: boolean
): Promise<void> {
  console.log(chalk.cyan('\n🔄 Synchronizing tools...\n'));

  const spinner = ora();
  const results: { tool: string; status: 'success' | 'skipped' | 'failed'; message: string }[] = [];

  for (const toolName of toolsToSync) {
    const toolConfig = getToolConfig(mappingRules, toolName);
    if (!toolConfig) {
      results.push({ tool: toolName, status: 'failed', message: 'Tool config not found' });
      continue;
    }

    try {
      const templatePath = path.join(projectRoot, toolConfig.template);
      const outputPath = path.join(projectRoot, toolConfig.output_path);

      // Check if regeneration is needed
      let needsRegen = force;

      if (!needsRegen && await fileExists(templatePath) && await fileExists(outputPath)) {
        const templateStats = await fs.stat(templatePath);
        const outputStats = await fs.stat(outputPath);
        needsRegen = templateStats.mtime > outputStats.mtime;
      } else if (!needsRegen) {
        needsRegen = !(await fileExists(outputPath));
      }

      if (!needsRegen && !force) {
        results.push({ tool: toolName, status: 'skipped', message: 'No changes' });
        continue;
      }

      spinner.start(chalk.cyan(`Syncing ${toolName}...`));

      // Read template
      const template = await readFile(templatePath);

      // Prepare variables
      const variables: Record<string, string> = {
        timestamp: getTimestamp(),
        version: mappingRules.version
      };

      // If template includes {{source_content}}, read source file content
      if (template.includes('{{source_content}}') && toolConfig.source_sections && toolConfig.source_sections.length > 0) {
        try {
          const sourceFile = toolConfig.source_sections[0];
          const sourceFilePath = path.join(projectRoot, sourceFile);
          const sourceContent = await readFile(sourceFilePath);
          variables.source_content = sourceContent;
        } catch (error) {
          console.warn(`Warning: Could not read source file for ${toolName}`);
          variables.source_content = '[Source content could not be read]';
        }
      }

      // Render template
      const content = renderTemplate(template, variables);

      // Write output file
      await writeFile(outputPath, content, verbose);

      results.push({ tool: toolName, status: 'success', message: 'Synced' });
      spinner.succeed(chalk.green(`✓ ${toolName} synced`));

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      results.push({ tool: toolName, status: 'failed', message: errorMessage });
      spinner.fail(chalk.red(`✗ ${toolName} sync failed`));
    }
  }

  // Summary
  console.log(chalk.cyan('\n📋 Synchronization Summary\n'));
  const successful = results.filter(r => r.status === 'success');
  const skipped = results.filter(r => r.status === 'skipped');
  const failed = results.filter(r => r.status === 'failed');

  if (successful.length > 0) {
    console.log(chalk.green('✓ Synced:'));
    successful.forEach(r => {
      console.log(chalk.white(`  - ${r.tool}`));
    });
  }

  if (skipped.length > 0) {
    console.log(chalk.blue('\n⊘ Skipped (no changes):'));
    skipped.forEach(r => {
      console.log(chalk.white(`  - ${r.tool}`));
    });
  }

  if (failed.length > 0) {
    console.log(chalk.red('\n✗ Failed:'));
    failed.forEach(r => {
      console.log(chalk.white(`  - ${r.tool}: ${r.message}`));
    });
  }

  console.log();

  if (failed.length === 0) {
    // Update Claude settings to auto-recognize project.md
    await updateClaudeSettings(projectRoot, verbose);
    console.log(chalk.green('✓ Synchronization completed successfully!\n'));
  } else {
    process.exit(1);
  }
}

async function updateClaudeSettings(projectRoot: string, verbose: boolean): Promise<void> {
  const claudeSettingsPath = path.join(projectRoot, '.claude', 'settings.json');

  try {
    // Try to read existing settings
    let settings: any = {
      permissions: { allow: [], additionalDirectories: [] },
      workspace: { root: projectRoot, ai_system: '.ai/', rules_file: '.ai/.cursorrules' },
      context: { ai_system_enabled: true, agent_awareness: true, skill_mapping: true, workflow_integration: true }
    };

    try {
      const existingSettings = await readFile(claudeSettingsPath);
      settings = JSON.parse(existingSettings);
    } catch {
      // Settings file doesn't exist, will create new one
    }

    // Ensure context section has project_context_file
    if (!settings.context) {
      settings.context = {};
    }
    settings.context.project_context_file = '.claude/project.md';

    // Write updated settings
    await writeFile(claudeSettingsPath, JSON.stringify(settings, null, 2), verbose);

    if (verbose) {
      console.log(chalk.green('✓ Claude settings updated with project context'));
    }
  } catch (error) {
    // Don't fail sync if settings update fails
    console.warn(chalk.yellow(`⚠ Warning: Could not update Claude settings: ${error instanceof Error ? error.message : 'Unknown error'}`));
  }
}
