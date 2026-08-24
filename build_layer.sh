#!/bin/bash

# Script to create an optimized AWS Lambda Layer package
# Standard installation with heavy cleanup

LAYER_DIR="lambda_layer"
PYTHON_DIR="$LAYER_DIR/python"
ZIP_FILE="packages.zip"

echo "--- Starting Lambda Layer Package Creation ---"

# 1. Clean up old build files
echo "[1/4] Cleaning previous builds..."
rm -rf "$LAYER_DIR"
rm -f "$ZIP_FILE"

# 2. Recreate directory structure
mkdir -p "$PYTHON_DIR"

# 3. Install requirements
echo "[2/4] Installing requirements from requirements.txt..."
if [ -f "requirements.txt" ]; then
    # Install without --platform/--only-binary since this machine is already
    # Linux x86_64 (same as Lambda). Those flags block pure-Python packages
    # like sgmllib3k (feedparser dep) that have no pre-built wheels.
    pip3 install \
        --target "$PYTHON_DIR" \
        --upgrade \
        --no-cache-dir \
        -r requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# 4. Cleanup and Optimization (CRITICAL)
echo "[3/4] Optimizing packages to reduce size..."

# Remove unnecessary documentation and metadata
find "$PYTHON_DIR" -name "__pycache__" -type d -exec rm -rf {} +
find "$PYTHON_DIR" -name "*.dist-info" -type d -exec rm -rf {} +
find "$PYTHON_DIR" -name "*.egg-info" -type d -exec rm -rf {} +
find "$PYTHON_DIR" -name "*.pyc" -delete
find "$PYTHON_DIR" -name "tests" -type d -exec rm -rf {} +
find "$PYTHON_DIR" -name "test" -type d -exec rm -rf {} +

# Strip binary files if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "      Stripping debug symbols from .so files..."
    find "$PYTHON_DIR" -name "*.so" \
        -exec strip --strip-unneeded {} + 2>/dev/null
fi

# 5. Zip the layer
echo "[4/4] Creating $ZIP_FILE..."
cd "$LAYER_DIR" || exit
zip -r -9 "../$ZIP_FILE" python > /dev/null
cd ..

# Final check
SIZE=$(du -sh "$ZIP_FILE" | cut -f1)
echo "--- Finished! ---"
echo "Package created: $ZIP_FILE"
echo "Current Size: $SIZE"
echo "-----------------------------------------------"
echo "Kiểm tra 'Runtime settings' trên AWS console xem 'Handler'"
echo "đã khớp với 'tên_file_của_bạn.lambda_handler' chưa."
echo "-----------------------------------------------"
