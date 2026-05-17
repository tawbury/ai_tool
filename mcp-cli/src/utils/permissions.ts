import fs from 'fs';
import path from 'path';

export interface PermissionReport {
  readable: boolean;
  writable: boolean;
  error?: string;
}

export function validatePermissions(dirPath: string): PermissionReport {
  try {
    if (!fs.existsSync(dirPath)) {
      return { readable: false, writable: false, error: 'Directory does not exist' };
    }

    // Check readability
    fs.accessSync(dirPath, fs.constants.R_OK);
    
    // Check writability by attempting to create and delete a temp file
    const testFile = path.join(dirPath, `.aios_perm_test_${Date.now()}`);
    fs.writeFileSync(testFile, 'test');
    fs.unlinkSync(testFile);

    return { readable: true, writable: true };
  } catch (err: any) {
    return {
      readable: false,
      writable: false,
      error: err.message,
    };
  }
}
