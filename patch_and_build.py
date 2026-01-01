#!/usr/bin/env python3
"""
Patch PyInstaller to handle existing symlinks and complete the build
"""
import os
import shutil
import subprocess
import sys

def patch_pyinstaller():
    """Patch PyInstaller's assemble method to skip existing symlinks"""
    import PyInstaller.building.api
    
    original_assemble = PyInstaller.building.api.COLLECT.assemble
    
    def patched_assemble(self):
        """Patched version that skips existing symlinks"""
        import os
        for item in self.toc:
            if len(item) >= 3:
                src, dst = item[1], item[2]
                if os.path.islink(dst) and os.path.exists(dst):
                    # Skip if symlink already exists and is valid
                    continue
                try:
                    if os.path.islink(src):
                        # Create parent directory if needed
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if os.path.exists(dst):
                            os.remove(dst)
                        os.symlink(os.readlink(src), dst)
                    else:
                        shutil.copy2(src, dst)
                except (OSError, FileExistsError) as e:
                    # Skip if symlink already exists
                    if "File exists" in str(e) or "FileExistsError" in str(type(e).__name__):
                        continue
                    raise
    
    PyInstaller.building.api.COLLECT.assemble = patched_assemble
    print("✅ Patched PyInstaller to handle existing symlinks")

if __name__ == "__main__":
    patch_pyinstaller()
    # Now run pyinstaller
    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "CSV SQL Engine Pro.spec"])

