import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';

export async function ensureDirectoryExists(dir: string, verbose: boolean = false): Promise<void> {
  try {
    await fs.ensureDir(dir);
    if (verbose) {
      console.log(chalk.green(`✓ Directory ensured: ${dir}`));
    }
  } catch (error) {
    throw new Error(`Failed to create directory ${dir}: ${error}`);
  }
}

export async function readFile(filePath: string): Promise<string> {
  try {
    return await fs.readFile(filePath, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to read file ${filePath}: ${error}`);
  }
}

export async function writeFile(filePath: string, content: string, verbose: boolean = false): Promise<void> {
  try {
    const dir = path.dirname(filePath);
    await fs.ensureDir(dir);
    await fs.writeFile(filePath, content, 'utf-8');
    if (verbose) {
      console.log(chalk.green(`✓ File written: ${filePath}`));
    }
  } catch (error) {
    throw new Error(`Failed to write file ${filePath}: ${error}`);
  }
}

export async function fileExists(filePath: string): Promise<boolean> {
  return fs.pathExists(filePath);
}

export async function directoryExists(dirPath: string): Promise<boolean> {
  const exists = await fs.pathExists(dirPath);
  if (!exists) return false;
  const stats = await fs.stat(dirPath);
  return stats.isDirectory();
}

export async function copyFile(source: string, destination: string, verbose: boolean = false): Promise<void> {
  try {
    await fs.ensureDir(path.dirname(destination));
    await fs.copy(source, destination);
    if (verbose) {
      console.log(chalk.green(`✓ Copied: ${source} → ${destination}`));
    }
  } catch (error) {
    throw new Error(`Failed to copy file from ${source} to ${destination}: ${error}`);
  }
}

export async function readDirectory(dirPath: string): Promise<string[]> {
  try {
    return await fs.readdir(dirPath);
  } catch (error) {
    throw new Error(`Failed to read directory ${dirPath}: ${error}`);
  }
}

export async function removeFile(filePath: string, verbose: boolean = false): Promise<void> {
  try {
    if (await fs.pathExists(filePath)) {
      await fs.remove(filePath);
      if (verbose) {
        console.log(chalk.green(`✓ Removed: ${filePath}`));
      }
    }
  } catch (error) {
    throw new Error(`Failed to remove file ${filePath}: ${error}`);
  }
}

export function getProjectRoot(): string {
  return process.cwd();
}

export function getAiDirectory(projectRoot: string = getProjectRoot()): string {
  return path.join(projectRoot, '.ai');
}

export function getInstallDirectory(projectRoot: string = getProjectRoot()): string {
  return path.join(getAiDirectory(projectRoot), 'install');
}

export function getMappingRulesPath(projectRoot: string = getProjectRoot()): string {
  return path.join(getInstallDirectory(projectRoot), 'mapping_rules.yaml');
}

export function getAdaptersDirectory(projectRoot: string = getProjectRoot()): string {
  return path.join(getInstallDirectory(projectRoot), 'adapters');
}

export function getTemplatesDirectory(projectRoot: string = getProjectRoot()): string {
  return path.join(getInstallDirectory(projectRoot), 'templates');
}

export function getTimestamp(): string {
  return new Date().toISOString().replace(/T/, ' ').replace(/\.\d{3}Z/, '');
}

export function renderTemplate(template: string, variables: Record<string, string>): string {
  let result = template;
  Object.entries(variables).forEach(([key, value]) => {
    result = result.replace(new RegExp(`{{${key}}}`, 'g'), value);
  });
  return result;
}
