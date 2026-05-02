"""Build script for rsjapp-mianyang EXE packaging.

Usage: uv run python build_exe.py
"""
import os
import sys
import subprocess


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(project_root, 'main.spec')

    print("Checking prerequisites...")

    try:
        import PyInstaller
        print(f"  PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("ERROR: PyInstaller not installed. Run: uv sync")
        sys.exit(1)

    try:
        import execjs
        runtime = execjs.get()
        print(f"  JS Runtime: {runtime}")
    except Exception as exc:
        print(f"  WARNING: JS runtime unavailable: {exc}")
        print("  Build will proceed but the EXE requires Node.js at runtime.")

    print(f"\nBuilding: {spec_file}")
    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', spec_file, '--clean', '--noconfirm'],
        cwd=project_root,
    )

    if result.returncode == 0:
        dist_dir = os.path.join(project_root, 'dist', 'rsjapp-mianyang')
        internal_dir = os.path.join(dist_dir, '_internal')
        print(f"\nBuild successful!")
        print(f"Output: {dist_dir}")

        for name in ['rsjapp-mianyang.exe']:
            path = os.path.join(dist_dir, name)
            status = "OK" if os.path.exists(path) else "MISSING!"
            print(f"  {name}: {status}")

        for name in ['course.js', 'app.js', 'node_modules', 'ffmpeg']:
            path = os.path.join(internal_dir, name)
            status = "OK" if os.path.exists(path) else "MISSING!"
            print(f"  _internal/{name}: {status}")
    else:
        print(f"\nBuild FAILED (exit code {result.returncode})")
        sys.exit(result.returncode)


if __name__ == '__main__':
    main()
