#!/bin/bash
set -e

# Configuration
SDK_ROOT="/mnt/c/Users/29903/AppData/Local/Android/Sdk"
BUILD_TOOLS="$SDK_ROOT/build-tools/34.0.0"
PLATFORM="$SDK_ROOT/platforms/android-34"
PROJECT_DIR="/mnt/d/聊天项目/android-app"
APP_DIR="$PROJECT_DIR/app/src/main"
BUILD_DIR="$PROJECT_DIR/build"
OUTPUT_DIR="$PROJECT_DIR/output"
JAVAC="/mnt/d/Java/jdk-24/bin/javac.exe"

# Helper: convert WSL path to Windows path
wsl_to_win() {
    wslpath -w "$1"
}

# Clean
rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
mkdir -p "$BUILD_DIR/gen" "$BUILD_DIR/obj" "$BUILD_DIR/apk" "$OUTPUT_DIR"

echo "=== Step 1: Compile resources with aapt2 ==="
"$BUILD_TOOLS/aapt2" compile --dir "$APP_DIR/res" -o "$BUILD_DIR/resources.zip"

echo "=== Step 2: Link resources ==="
"$BUILD_TOOLS/aapt2" link \
    -o "$BUILD_DIR/apk/base.apk" \
    -I "$PLATFORM/android.jar" \
    --manifest "$APP_DIR/AndroidManifest.xml" \
    --java "$BUILD_DIR/gen" \
    "$BUILD_DIR/resources.zip"

echo "=== Step 3: Compile Java ==="
WIN_PLATFORM=$(wsl_to_win "$PLATFORM/android.jar")
WIN_MAIN=$(wsl_to_win "$APP_DIR/java/com/chat/platform/MainActivity.java")
WIN_R=$(wsl_to_win "$BUILD_DIR/gen/com/chat/platform/R.java")
WIN_OUT=$(wsl_to_win "$BUILD_DIR/obj")

"$JAVAC" --release 8 \
    -classpath "$WIN_PLATFORM" \
    -d "$WIN_OUT" \
    "$WIN_MAIN" "$WIN_R"

echo "=== Step 4: Convert to DEX ==="
export ANDROID_HOME="$SDK_ROOT"
bash "$BUILD_TOOLS/d8" --output "$BUILD_DIR/apk" \
    --lib "$PLATFORM/android.jar" \
    "$BUILD_DIR/obj/com/chat/platform/"*.class

echo "=== Step 5: Package APK ==="
cd "$BUILD_DIR/apk"
mkdir -p unzipped
cd unzipped
unzip -o ../base.apk
cp ../classes.dex .
zip -r -q ../unsigned.apk .
cd ..

echo "=== Step 6: Align APK ==="
"$BUILD_TOOLS/zipalign" -f 4 unsigned.apk aligned.apk

echo "=== Step 7: Sign APK ==="
KEYSTORE="$PROJECT_DIR/debug.keystore"
if [ ! -f "$KEYSTORE" ]; then
    keytool -genkey -v -keystore "$KEYSTORE" \
        -alias debug -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass android -keypass android \
        -dname "CN=Debug, OU=Debug, O=Debug, L=Debug, S=Debug, C=US"
fi

bash "$BUILD_TOOLS/apksigner" sign \
    --ks "$KEYSTORE" \
    --ks-key-alias debug \
    --ks-pass pass:android \
    --key-pass pass:android \
    --out "$OUTPUT_DIR/聊天平台.apk" \
    aligned.apk

echo ""
echo "=== BUILD SUCCESS ==="
echo "APK: $OUTPUT_DIR/聊天平台.apk"
ls -lh "$OUTPUT_DIR/聊天平台.apk"
