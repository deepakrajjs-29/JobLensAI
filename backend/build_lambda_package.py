"""Build script to create a production-ready AWS Lambda deployment ZIP targeting Linux x86_64 / Python 3.12."""
import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = BASE_DIR / "lambda_package"
ZIP_FILE = BASE_DIR / "joblens-ai-backend.zip"
TEST_TARGET = BASE_DIR / "test_lambda_target"


def clean_dir(directory: Path):
    """Safely remove and recreate directory with retry for Windows locks."""
    import time
    if directory.exists():
        for i in range(5):
            try:
                shutil.rmtree(directory)
                break
            except Exception as e:
                time.sleep(0.5)
                if i == 4:
                    print(f"  Warning: Could not completely remove {directory}: {e}")
    directory.mkdir(parents=True, exist_ok=True)


def build_package():
    print("=" * 60)
    print("BUILDING JOBLENS AI AWS LAMBDA DEPLOYMENT PACKAGE")
    print("Target Runtime: Python 3.12 | Linux | x86_64")
    print("=" * 60 + "\n")

    # 1. Clean test target from earlier test
    if TEST_TARGET.exists():
        shutil.rmtree(TEST_TARGET)

    # 2. Prepare clean lambda_package directory
    print("[1/5] Preparing clean package directory:", PACKAGE_DIR)
    clean_dir(PACKAGE_DIR)

    # 3. Download and install Linux x86_64 compatible wheels
    print("\n[2/5] Installing Linux x86_64 dependencies for Python 3.12...")
    packages = [
        "fastapi>=0.115.0",
        "mangum>=0.19.0",
        "pydantic>=2.8.0",
        "python-multipart>=0.0.9",
        "pypdf>=5.0.0",
        "python-dotenv>=1.0.0",
        "boto3>=1.35.0",
        "botocore>=1.35.0",
    ]

    pip_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--target",
        str(PACKAGE_DIR),
        "--platform",
        "manylinux2014_x86_64",
        "--implementation",
        "cp",
        "--python-version",
        "3.12",
        "--only-binary=:all:",
        *packages,
    ]

    result = subprocess.run(pip_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] pip install failed:\n", result.stderr, file=sys.stderr)
        sys.exit(1)
    print("  Dependencies installed successfully.")

    # 4. Copy backend application code
    print("\n[3/5] Copying application code (app/ and lambda_handler.py)...")
    app_src = BASE_DIR / "app"
    app_dst = PACKAGE_DIR / "app"
    shutil.copytree(
        app_src,
        app_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".env*")
    )
    print("  app/ directory copied.")

    handler_src = BASE_DIR / "lambda_handler.py"
    handler_dst = PACKAGE_DIR / "lambda_handler.py"
    shutil.copy2(handler_src, handler_dst)
    print("  lambda_handler.py copied.")

    # Verify .env is NOT in the package
    for root, dirs, files in os.walk(PACKAGE_DIR):
        for file in files:
            lower_file = file.lower()
            if lower_file.startswith(".env") or lower_file.endswith(".key") or lower_file == "id_rsa":
                print(f"[SECURITY ALERT] Removing sensitive file: {os.path.join(root, file)}")
                os.remove(os.path.join(root, file))

    # 5. Clean unnecessary metadata and caches to optimize ZIP size
    print("\n[4/5] Pruning unnecessary caches, tests, and documentation...")
    uncompressed_bytes = 0
    file_count = 0

    for root, dirs, files in os.walk(PACKAGE_DIR, topdown=False):
        # Remove __pycache__
        for d in list(dirs):
            if d == "__pycache__" or d == "tests" or d.endswith(".dist-info"):
                dir_path = Path(root) / d
                # Keep dist-info if needed, but remove tests/caches
                if d in ["__pycache__", "tests"]:
                    shutil.rmtree(dir_path, ignore_errors=True)

    for root, dirs, files in os.walk(PACKAGE_DIR):
        for file in files:
            file_path = Path(root) / file
            uncompressed_bytes += file_path.stat().st_size
            file_count += 1

    uncompressed_mb = uncompressed_bytes / (1024 * 1024)
    print(f"  Total uncompressed files: {file_count} ({uncompressed_mb:.2f} MB)")

    # 6. Create ZIP archive
    print(f"\n[5/5] Creating deployment ZIP archive: {ZIP_FILE}...")
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()

    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PACKAGE_DIR):
            for file in files:
                file_path = Path(root) / file
                archive_name = file_path.relative_to(PACKAGE_DIR)
                zipf.write(file_path, arcname=archive_name)

    zip_bytes = ZIP_FILE.stat().st_size
    zip_mb = zip_bytes / (1024 * 1024)
    print(f"  ZIP created successfully! Size: {zip_mb:.2f} MB ({zip_bytes:,} bytes)")

    # 7. Verify ZIP internal structure
    print("\n" + "=" * 60)
    print("ZIP STRUCTURE VERIFICATION")
    print("=" * 60)
    with zipfile.ZipFile(ZIP_FILE, "r") as zipf:
        namelist = zipf.namelist()
        has_handler = "lambda_handler.py" in namelist
        has_app_main = any(n.startswith("app/main.py") or n.startswith("app\\main.py") for n in namelist)
        has_fastapi = any(n.startswith("fastapi/") for n in namelist)
        has_pydantic_core = any(n.startswith("pydantic_core/") for n in namelist)
        has_env = any(".env" in n for n in namelist)

        print(f"  - Root lambda_handler.py: {'[OK]' if has_handler else '[FAIL]'}")
        print(f"  - app/main.py present:     {'[OK]' if has_app_main else '[FAIL]'}")
        print(f"  - fastapi package present: {'[OK]' if has_fastapi else '[FAIL]'}")
        print(f"  - Linux pydantic_core:     {'[OK]' if has_pydantic_core else '[FAIL]'}")
        print(f"  - .env / secrets excluded: {'[OK]' if not has_env else '[FAIL - SECRETS FOUND]'}")

    print("\n" + "=" * 60)
    print("PACKAGE SUMMARY")
    print("=" * 60)
    print(f"ZIP Path:          {ZIP_FILE}")
    print(f"ZIP Size:          {zip_mb:.2f} MB")
    print(f"Uncompressed Size: {uncompressed_mb:.2f} MB")
    print(f"Target Runtime:    Python 3.12 (Linux x86_64)")
    print(f"Handler:           lambda_handler.handler")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    build_package()
