import os from 'os';
import path from 'path';

export interface AIOSPaths {
  home: string;
  ai: string;
  codex: string;
  claude: string;
  gemini: string;
}

export function detectPaths(): AIOSPaths {
  const homeDir = process.env.AIOS_HOME || os.homedir();
  
  return {
    home: homeDir,
    ai: path.join(homeDir, '.ai'),
    codex: path.join(homeDir, '.codex'),
    claude: path.join(homeDir, '.claude'),
    gemini: path.join(homeDir, '.gemini'),
  };
}

export function getProjectAIPath(projectRoot: string): string {
  return path.join(projectRoot, '.ai', 'project');
}
