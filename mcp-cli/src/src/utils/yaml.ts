import yaml from 'js-yaml';
import { readFile } from './file';

export interface MappingRules {
  version: string;
  description: string;
  source_sections: Record<string, string>;
  tools: Record<string, ToolConfig>;
  generated_file_header: GeneratedFileHeader;
}

export interface ToolConfig {
  enabled: boolean;
  output_path: string;
  template: string;
  source_sections: string[];
  description: string;
}

export interface GeneratedFileHeader {
  enabled: boolean;
  format: string;
  content: string;
}

export async function loadMappingRules(filePath: string): Promise<MappingRules> {
  try {
    const content = await readFile(filePath);
    const data = yaml.load(content);

    if (!isValidMappingRules(data)) {
      throw new Error('Invalid mapping rules format');
    }

    return data as MappingRules;
  } catch (error) {
    throw new Error(`Failed to load mapping rules from ${filePath}: ${error}`);
  }
}

export async function loadAdapterConfig(filePath: string): Promise<Record<string, any>> {
  try {
    const content = await readFile(filePath);
    const data = yaml.load(content);
    return data as Record<string, any>;
  } catch (error) {
    throw new Error(`Failed to load adapter config from ${filePath}: ${error}`);
  }
}

function isValidMappingRules(data: any): data is MappingRules {
  return (
    data &&
    typeof data === 'object' &&
    'version' in data &&
    'tools' in data &&
    'generated_file_header' in data
  );
}

export function getEnabledTools(rules: MappingRules): string[] {
  return Object.entries(rules.tools)
    .filter(([_, config]) => config.enabled)
    .map(([name, _]) => name);
}

export function getToolConfig(rules: MappingRules, toolName: string): ToolConfig | null {
  return rules.tools[toolName] || null;
}
