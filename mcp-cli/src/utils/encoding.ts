import fs from 'fs';

/**
 * Checks if a file has a UTF-8 BOM.
 */
export function hasBOM(filePath: string): boolean {
  const buffer = Buffer.alloc(3);
  const fd = fs.openSync(filePath, 'r');
  fs.readSync(fd, buffer, 0, 3, 0);
  fs.closeSync(fd);
  return buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF;
}

/**
 * Enforces UTF-8 without BOM by removing it if present.
 */
export function enforceUTF8NoBOM(filePath: string): void {
  if (!fs.existsSync(filePath)) return;

  const content = fs.readFileSync(filePath);
  if (content[0] === 0xEF && content[1] === 0xBB && content[2] === 0xBF) {
    // Remove BOM
    const noBOMContent = content.slice(3);
    fs.writeFileSync(filePath, noBOMContent, 'utf8');
    console.log(`[Encoding] BOM removed from ${filePath}`);
  } else {
    // Just ensure it's written as UTF-8
    const text = content.toString('utf8');
    fs.writeFileSync(filePath, text, 'utf8');
  }
}

/**
 * Validates encoding of a file.
 */
export function validateEncoding(filePath: string): { valid: boolean; message: string } {
  if (!fs.existsSync(filePath)) {
    return { valid: false, message: 'File does not exist' };
  }
  
  if (hasBOM(filePath)) {
    return { valid: false, message: 'UTF-8 with BOM detected' };
  }
  
  return { valid: true, message: 'UTF-8 without BOM' };
}
