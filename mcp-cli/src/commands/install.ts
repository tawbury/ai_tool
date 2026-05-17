import chalk from 'chalk';
import ora from 'ora';
import path from 'path';
import {
  readFile,
  writeFile,
  directoryExists,
  getMappingRulesPath,
  getProjectRoot,
  getTimestamp,
  renderTemplate,
  getTemplatesDirectory
} from '../utils/file';
import { loadMappingRules, getEnabledTools, getToolConfig, loadAdapterConfig } from '../utils/yaml';

export interface InstallArgs {
  'all-tools': boolean;
  tools: string[];
  verbose: boolean;
}

export async function installCommand(argv: InstallArgs): Promise<void> {
  const projectRoot = getProjectRoot();
  const verbose = argv.verbose || false;
  const allTools = argv['all-tools'] || false;
  const specificTools = (argv.tools || []) as string[];

  console.log(chalk.cyan('\n📦 MCP OS Tool Installation\n'));

  const spinner = ora();

  try {
    // Load mapping rules
    spinner.start(chalk.cyan('Loading mapping rules...'));
    const mappingRulesPath = getMappingRulesPath(projectRoot);
    const mappingRules = await loadMappingRules(mappingRulesPath);
    spinner.succeed(chalk.green('Mapping rules loaded'));

    // Determine which tools to install
    let toolsToInstall: string[];
    if (allTools) {
      toolsToInstall = getEnabledTools(mappingRules);
    } else if (specificTools.length > 0) {
      toolsToInstall = specificTools;
    } else {
      console.error(chalk.red('✗ Please specify --all-tools or specific tools'));
      process.exit(1);
    }

    // Install each tool
    const results: { tool: string; status: 'success' | 'failed'; message: string }[] = [];

    for (const toolName of toolsToInstall) {
      const toolConfig = getToolConfig(mappingRules, toolName);
      if (!toolConfig) {
        results.push({ tool: toolName, status: 'failed', message: 'Tool not found in mapping rules' });
        continue;
      }

      try {
        spinner.start(chalk.cyan(`Installing ${toolName}...`));
        await installTool(projectRoot, toolName, toolConfig, mappingRules, verbose);
        results.push({ tool: toolName, status: 'success', message: 'Installed successfully' });
        spinner.succeed(chalk.green(`✓ ${toolName} installed`));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        results.push({ tool: toolName, status: 'failed', message: errorMessage });
        spinner.fail(chalk.red(`✗ ${toolName} installation failed`));
      }
    }

    // Summary
    console.log(chalk.cyan('\n📋 Installation Summary\n'));
    const successful = results.filter(r => r.status === 'success');
    const failed = results.filter(r => r.status === 'failed');

    if (successful.length > 0) {
      console.log(chalk.green('✓ Successfully installed:'));
      successful.forEach(r => {
        console.log(chalk.white(`  - ${r.tool}`));
      });
    }

    if (failed.length > 0) {
      console.log(chalk.red('\n✗ Failed to install:'));
      failed.forEach(r => {
        console.log(chalk.white(`  - ${r.tool}: ${r.message}`));
      });
    }

    console.log();

    if (failed.length === 0) {
      // Update Claude settings to auto-recognize project.md
      await updateClaudeSettings(projectRoot, verbose);
      console.log(chalk.green('✓ All tools installed successfully!\n'));
    } else {
      process.exit(1);
    }

  } catch (error) {
    spinner.fail(chalk.red('Installation failed'));
    if (error instanceof Error) {
      console.error(chalk.red(`✗ ${error.message}`));
    }
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
    // Don't fail installation if settings update fails
    console.warn(chalk.yellow(`⚠ Warning: Could not update Claude settings: ${error instanceof Error ? error.message : 'Unknown error'}`));
  }
}

async function installTool(
  projectRoot: string,
  toolName: string,
  toolConfig: any,
  mappingRules: any,
  verbose: boolean
): Promise<void> {
  const templatePath = path.join(projectRoot, toolConfig.template);
  const outputPath = path.join(projectRoot, toolConfig.output_path);

  // Read template
  const template = await readFile(templatePath);

  // Prepare variables for template rendering
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
}
