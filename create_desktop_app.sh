#!/bin/bash
# Create macOS Desktop Application for Nexus Platform

echo "🚀 Creating Nexus Platform Desktop Application..."

# Get the current directory
NEXUS_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Nexus Platform"
APP_BUNDLE="$HOME/Desktop/${APP_NAME}.app"

# Create app bundle structure
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

# Create Info.plist
cat > "${APP_BUNDLE}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>nexus_launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.nexusplatform.desktop</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

# Create the executable script
cat > "${APP_BUNDLE}/Contents/MacOS/nexus_launcher" << EOF
#!/bin/bash
# Nexus Platform Desktop Launcher

# Change to the Nexus directory
cd "${NEXUS_DIR}"

# Check if Python environment exists
if [ ! -d "nexus_python_env" ]; then
    osascript -e 'display alert "Nexus Platform" message "Python environment not found. Please run setup first." buttons {"OK"} default button "OK"'
    exit 1
fi

# Launch the desktop application
./nexus_python_env/bin/python nexus_desktop_launcher.py
EOF

# Make the executable script executable
chmod +x "${APP_BUNDLE}/Contents/MacOS/nexus_launcher"

# Create an icon (if possible)
if command -v sips &> /dev/null; then
    # Create a simple icon using text
    echo "Creating application icon..."
    # This would create a simple icon, but for now we'll skip it
fi

echo "✅ Desktop application created at: ${APP_BUNDLE}"
echo "🚀 You can now double-click 'Nexus Platform.app' on your desktop to launch the integrated system!"

# Make the startup script executable
chmod +x launch_nexus_desktop.sh

echo ""
echo "📋 Alternative launch methods:"
echo "1. Double-click 'Nexus Platform.app' on your desktop"
echo "2. Run: ./launch_nexus_desktop.sh"
echo "3. Run: ./nexus_python_env/bin/python nexus_desktop_launcher.py"
