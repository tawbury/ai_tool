import chalk from 'chalk';
import ora from 'ora';
import path from 'path';
import {
  ensureDirectoryExists,
  fileExists,
  directoryExists,
  getAiDirectory,
  getTimestamp,
  writeFile
} from '../utils/file';

export interface InitArgs {
  directory: string;
  force: boolean;
  verbose: boolean;
}

export async function initCommand(argv: InitArgs): Promise<void> {
  const projectRoot = path.resolve(argv.directory || '.');
  const verbose = argv.verbose || false;

  console.log(chalk.cyan('\n🚀 MCP OS Project Initialization\n'));

  // Check if project root exists
  if (!(await directoryExists(projectRoot))) {
    console.error(chalk.red(`✗ Directory does not exist: ${projectRoot}`));
    process.exit(1);
  }

  // Check if .ai directory already exists
  const aiDir = getAiDirectory(projectRoot);
  if ((await directoryExists(aiDir)) && !argv.force) {
    console.error(chalk.yellow(`⚠ Project already initialized at ${projectRoot}`));
    console.error(chalk.yellow(`  Use --force to reinitialize`));
    process.exit(1);
  }

  const spinner = ora();

  try {
    // Create directory structure
    const directories = [
      { path: path.join(aiDir, 'spec'), desc: '.ai/spec' },
      { path: path.join(aiDir, 'templates'), desc: '.ai/templates' },
      { path: path.join(aiDir, 'agents'), desc: '.ai/agents' },
      { path: path.join(aiDir, 'skills', '_shared'), desc: '.ai/skills/_shared' },
      { path: path.join(aiDir, 'validators', '_base'), desc: '.ai/validators/_base' },
      { path: path.join(aiDir, 'workflows', '_base'), desc: '.ai/workflows/_base' },
      { path: path.join(aiDir, 'install', 'adapters'), desc: '.ai/install/adapters' },
      { path: path.join(aiDir, 'install', 'templates'), desc: '.ai/install/templates' },
      { path: path.join(aiDir, 'export', 'chat', 'chatgpt'), desc: '.ai/export/chat/chatgpt' },
      { path: path.join(aiDir, 'export', 'chat', 'gemini'), desc: '.ai/export/chat/gemini' },
      { path: path.join(aiDir, 'export', 'chat', 'claude-web'), desc: '.ai/export/chat/claude-web' },
      { path: path.join(projectRoot, 'docs', 'decisions'), desc: 'docs/decisions' },
      { path: path.join(projectRoot, 'docs', 'tasks'), desc: 'docs/tasks' },
      { path: path.join(projectRoot, 'docs', 'reports'), desc: 'docs/reports' },
      { path: path.join(projectRoot, 'docs', 'dev', 'archi'), desc: 'docs/dev/archi' },
      { path: path.join(projectRoot, 'docs', 'dev', 'spec'), desc: 'docs/dev/spec' },
      { path: path.join(projectRoot, 'docs', 'dev', 'PRD'), desc: 'docs/dev/PRD' },
      { path: path.join(projectRoot, 'docs', 'index'), desc: 'docs/index' },
      { path: path.join(projectRoot, 'vault', 'drafts'), desc: 'vault/drafts' },
      { path: path.join(projectRoot, 'vault', 'experiments'), desc: 'vault/experiments' },
      { path: path.join(projectRoot, 'vault', 'legacy'), desc: 'vault/legacy' },
      { path: path.join(projectRoot, 'vault', 'pending'), desc: 'vault/pending' },
      { path: path.join(projectRoot, 'ops', 'run_records'), desc: 'ops/run_records' },
      { path: path.join(projectRoot, 'ops', 'approvals'), desc: 'ops/approvals' },
      { path: path.join(projectRoot, 'ops', 'audit'), desc: 'ops/audit' },
      { path: path.join(projectRoot, 'ops', 'notes'), desc: 'ops/notes' },
      { path: path.join(projectRoot, 'backup', 'docs'), desc: 'backup/docs' },
      { path: path.join(projectRoot, 'backup', 'vault'), desc: 'backup/vault' },
      { path: path.join(projectRoot, 'backup', '.ai'), desc: 'backup/.ai' }
    ];

    spinner.start(chalk.cyan('Creating directory structure...'));
    for (const dir of directories) {
      await ensureDirectoryExists(dir.path, verbose);
    }
    spinner.succeed(chalk.green(`Created ${directories.length} directories`));

    // Create README files
    spinner.start(chalk.cyan('Creating README files...'));
    await createReadmeFiles(projectRoot, verbose);
    spinner.succeed(chalk.green('README files created'));

    // Create .gitignore
    spinner.start(chalk.cyan('Creating .gitignore...'));
    await createGitignore(projectRoot, verbose);
    spinner.succeed(chalk.green('.gitignore created'));

    console.log(chalk.green('\n✓ Project initialized successfully!\n'));
    console.log(chalk.cyan('Next steps:'));
    console.log(chalk.white('  1. Review and customize .ai/ directory contents'));
    console.log(chalk.white('  2. Run: mcp install --all-tools'));
    console.log(chalk.white('  3. Configure your IDE tools\n'));

  } catch (error) {
    spinner.fail(chalk.red('Initialization failed'));
    if (error instanceof Error) {
      console.error(chalk.red(`✗ ${error.message}`));
    }
    process.exit(1);
  }
}

async function createReadmeFiles(projectRoot: string, verbose: boolean): Promise<void> {
  const readmeContent = `# AI Tool Project

This project uses the **mcp OS** - Multi-Agent AI Operating System.

## Project Structure

- **.ai/**: Single Source of Truth (SSoT) - all rules, templates, agents, skills, validators, workflows
- **docs/**: Official project documents
- **vault/**: AI drafts and experimental materials
- **ops/**: Operations logs and approval records
- **backup/**: Disaster recovery backups

## Getting Started

1. Review the MCP OS specification: \`.ai/spec/MCP_OS_Operational_Spec_v0_1.md\`
2. Explore agent definitions: \`.ai/agents/\`
3. Check available skills: \`.ai/skills/\`
4. Review workflow definitions: \`.ai/workflows/\`
5. Use document templates: \`.ai/templates/\`

## Running Commands

\`\`\`bash
mcp init              # Initialize a new project
mcp install --all-tools  # Generate IDE tool configurations
mcp sync              # Synchronize .ai/ changes
\`\`\`

## For More Information

See \`.ai/README.md\` and \`.ai/spec/MCP_OS_Operational_Spec_v0_1.md\`
`;

  const readmePath = path.join(projectRoot, 'README.md');
  if (!(await fileExists(readmePath))) {
    await writeFile(readmePath, readmeContent, verbose);
  }

  const aiReadmeContent = `# AI System Directory

Single Source of Truth (SSoT) for the mcp OS project.

## Structure

- **spec/**: Operational specifications
- **agents/**: Agent definitions
- **skills/**: Skill implementations
- **validators/**: Validation rules
- **workflows/**: Workflow definitions
- **templates/**: Document templates
- **install/**: Tool integration configuration
- **export/**: Exported configurations for external tools

## Do NOT Edit

- Generated files (except through mcp sync)
- .cursorrules (source for root .cursorrules)

## See Also

- Full Specification: \`spec/MCP_OS_Operational_Spec_v0_1.md\`
`;

  const aiReadmePath = path.join(projectRoot, '.ai', 'README.md');
  if (!(await fileExists(aiReadmePath))) {
    await writeFile(aiReadmePath, aiReadmeContent, verbose);
  }
}

async function createGitignore(projectRoot: string, verbose: boolean): Promise<void> {
  const gitignoreContent = `# Dependencies
node_modules/
*.lock

# Generated files (these are auto-generated, do not commit)
.github/copilot-instructions.md
.claude/project.md
.cursorrules
.windsurfrules

# OS
.DS_Store
Thumbs.db

# Backups (disaster recovery only)
backup/

# Logs
*.log
npm-debug.log*

# Temporary
.env.local
.env.*.local
`;

  const gitignorePath = path.join(projectRoot, '.gitignore');
  if (!(await fileExists(gitignorePath))) {
    await writeFile(gitignorePath, gitignoreContent, verbose);
  }
}
