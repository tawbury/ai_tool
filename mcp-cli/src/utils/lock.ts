import fs from 'fs';
import path from 'path';

export class AIOSLock {
  private lockFilePath: string;

  constructor(dirPath: string) {
    this.lockFilePath = path.join(dirPath, '.lock');
  }

  /**
   * Tries to acquire a lock. Fails fast if already locked.
   */
  acquire(): boolean {
    if (fs.existsSync(this.lockFilePath)) {
      const pid = fs.readFileSync(this.lockFilePath, 'utf8');
      console.error(`[Lock] Already locked by PID: ${pid}`);
      return false;
    }

    try {
      fs.writeFileSync(this.lockFilePath, process.pid.toString(), { flag: 'wx' });
      return true;
    } catch (err) {
      return false;
    }
  }

  /**
   * Releases the lock.
   */
  release(): void {
    if (fs.existsSync(this.lockFilePath)) {
      fs.unlinkSync(this.lockFilePath);
    }
  }

  /**
   * Checks if the lock is held.
   */
  isLocked(): boolean {
    return fs.existsSync(this.lockFilePath);
  }
}

export function getGlobalLock(homeDir: string): AIOSLock {
  const aiDir = path.join(homeDir, '.ai');
  if (!fs.existsSync(aiDir)) {
    fs.mkdirSync(aiDir, { recursive: true });
  }
  return new AIOSLock(aiDir);
}

export function getProjectLock(projectRoot: string): AIOSLock {
  const aiProjectDir = path.join(projectRoot, '.ai');
  if (!fs.existsSync(aiProjectDir)) {
    fs.mkdirSync(aiProjectDir, { recursive: true });
  }
  return new AIOSLock(aiProjectDir);
}
