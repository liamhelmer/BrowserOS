# BrowserOS for Android - Installation Guide

## Overview

This guide covers building and installing BrowserOS on Android devices.

## Prerequisites

### Required Software

1. **Android Studio** (latest stable version)
   - Download from: https://developer.android.com/studio

2. **Android SDK**
   - Minimum API Level 26 (Android 8.0)
   - Target API Level 34 (Android 14)
   - Install via Android Studio SDK Manager

3. **Android NDK** r26 or later
   - Install via Android Studio SDK Manager
   - Or download from: https://developer.android.com/ndk/downloads

4. **Java Development Kit (JDK) 11+**
   - OpenJDK or Oracle JDK
   - Set `JAVA_HOME` environment variable

5. **Python 3.11+** (for build scripts)

6. **Chromium build tools** (depot_tools)
   - For building Chromium Android
   - Follow: https://chromium.googlesource.com/chromium/tools/depot_tools.git

### Environment Setup

```bash
# Set Android SDK location
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME

# Add Android tools to PATH
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin

# Set Java home
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Android NDK (auto-detected by build, but can be set explicitly)
export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/26.1.10909125
```

## Building from Source

### Option 1: Using Build System (Recommended)

```bash
# Clone repository
git clone https://github.com/browseros-ai/BrowserOS.git
cd BrowserOS

# Initialize submodules
git submodule update --init --recursive

# Navigate to browseros package
cd packages/browseros

# Set up environment
python3 -m pip install -r requirements.txt

# Build for Android
python3 build/cli/build.py --pipeline android
```

### Option 2: Manual Build

#### Step 1: Build Chromium for Android

```bash
cd packages/browseros

# Fetch Chromium source
./build/cli/build.py --pipeline git_setup

# Configure for Android
cd chromium/src
gn gen out/AndroidRelease --args='
  target_os="android"
  target_cpu="arm64"
  is_debug=false
  is_official_build=true
  android_channel="stable"
'

# Build Chromium
ninja -C out/AndroidRelease chrome_public_apk
```

#### Step 2: Build Android App

```bash
cd packages/browseros/android

# Build with Gradle
./gradlew assembleRelease

# Output APK
# Location: app/build/outputs/apk/release/BrowserOS-release.apk
```

### Build Variants

- **Debug**: `./gradlew assembleDebug` - Includes debugging symbols, larger APK
- **Release**: `./gradlew assembleRelease` - Optimized, smaller APK (requires signing)

## Installation

### Installing on Physical Device

#### Prerequisites
- Enable Developer Options on your Android device
- Enable USB Debugging
- Connect device via USB

#### Install APK

```bash
# Using adb
adb install -r app/build/outputs/apk/release/BrowserOS-release.apk

# Or using Gradle
./gradlew installRelease
```

### Installing on Emulator

```bash
# Start emulator
emulator -avd <avd_name>

# Install APK
adb install -r app/build/outputs/apk/release/BrowserOS-release.apk
```

### Download Pre-built APK

For convenience, download pre-built APKs from:
- **GitHub Releases**: https://github.com/browseros-ai/BrowserOS/releases
- **Official Website**: https://files.browseros.com/download/BrowserOS.apk

```bash
# Download and install
wget https://files.browseros.com/download/BrowserOS.apk
adb install -r BrowserOS.apk
```

## Configuration

### First Run Setup

1. **Launch BrowserOS** from app drawer
2. **Grant Permissions** when prompted:
   - Notifications (for MCP service)
   - Storage (optional, for downloads)
3. **Configure AI Provider**:
   - Tap menu → Settings
   - Select AI provider (OpenAI, Anthropic, Ollama)
   - Enter API key or configure local model

### MCP Server Setup

The MCP server starts automatically when you launch BrowserOS.

**Check MCP Status:**
1. Open BrowserOS Settings
2. Navigate to "MCP Server" section
3. Note the CDP and MCP port numbers

**Using from Claude Code:**

```bash
# Add BrowserOS MCP server
claude mcp add --transport http browseros http://<device-ip>:9225/mcp

# Example (if using emulator)
claude mcp add --transport http browseros http://10.0.2.2:9225/mcp
```

**Note**: For physical devices, ensure your development machine and Android device are on the same network.

### Network Access

To access MCP server from external devices:

1. **Find device IP**:
   ```bash
   adb shell ip addr show wlan0
   ```

2. **Enable port forwarding** (for emulator):
   ```bash
   adb forward tcp:9225 tcp:9225
   adb forward tcp:9222 tcp:9222
   ```

3. **Access MCP server**:
   - From emulator: `http://10.0.2.2:9225/mcp`
   - From device: `http://<device-ip>:9225/mcp`

## Troubleshooting

### Build Issues

**Problem**: `ANDROID_HOME not set`
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
```

**Problem**: `Android NDK not found`
```bash
# Install via Android Studio SDK Manager
# Or set manually:
export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/<version>
```

**Problem**: `Java not found`
```bash
# Install JDK 11+
sudo apt install openjdk-11-jdk  # Ubuntu/Debian
brew install openjdk@11          # macOS

# Set JAVA_HOME
export JAVA_HOME=/path/to/jdk
```

### Runtime Issues

**Problem**: MCP server not starting

1. Check app logs:
   ```bash
   adb logcat | grep MCP
   ```

2. Ensure battery optimization is disabled:
   - Settings → Apps → BrowserOS → Battery → Unrestricted

**Problem**: Cannot connect to MCP from external device

1. Check firewall settings
2. Verify device is on same network
3. Test with curl:
   ```bash
   curl http://<device-ip>:9225/health
   ```

**Problem**: WebView not loading pages

1. Clear app data:
   ```bash
   adb shell pm clear com.browseros.app
   ```

2. Check network permissions in Settings

### Performance Issues

**High battery usage**:
- MCP server runs as foreground service
- Normal usage: 3-5% per hour
- If higher, check for continuous background tasks

**App size too large**:
- APK includes Chromium and native libraries
- Expected size: 80-150 MB
- Use Android App Bundle for Google Play (smaller download)

## Debugging

### Enable Debug Logging

```bash
# View all app logs
adb logcat | grep BrowserOS

# View MCP service logs
adb logcat | grep MCPService

# View native logs
adb logcat | grep MCP_Server_Native

# Save logs to file
adb logcat -d > browseros-log.txt
```

### Debug Build

```bash
# Build debug variant
./gradlew assembleDebug

# Install and launch with debugger
./gradlew installDebug
adb shell am start -D com.browseros.app/.MainActivity

# Attach Android Studio debugger
```

### WebView Debugging

1. Enable WebView debugging in app (debug builds only)
2. Open Chrome on desktop: `chrome://inspect`
3. Select device and inspect WebView

## Updating

### Manual Update

1. Download latest APK
2. Install over existing version:
   ```bash
   adb install -r BrowserOS-latest.apk
   ```

### Automatic Updates (Future)

- In-app update notifications
- Download and install updates within app
- Or via Google Play Store (when available)

## Uninstallation

```bash
# Using adb
adb uninstall com.browseros.app

# Or via device Settings
Settings → Apps → BrowserOS → Uninstall
```

## Support

- **GitHub Issues**: https://github.com/browseros-ai/BrowserOS/issues
- **Discord**: https://discord.gg/YKwjt5vuKr
- **Documentation**: https://docs.browseros.com

## Platform-Specific Notes

### Samsung Devices

- May require disabling Samsung Internet as default browser
- Some Knox security features may interfere with WebView

### Xiaomi/MIUI

- Disable battery saver for BrowserOS
- Grant "Display over other apps" permission

### OnePlus/OxygenOS

- Disable battery optimization
- Allow background activity

## Advanced

### Custom Builds

Edit `app/build.gradle.kts` to customize:
- App ID: `applicationId`
- Version: `versionCode`, `versionName`
- Features: Add/remove dependencies

### Signing for Release

1. Generate keystore:
   ```bash
   keytool -genkey -v -keystore browseros-release.keystore \
     -alias browseros -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Add to `gradle.properties`:
   ```properties
   KEYSTORE_FILE=/path/to/browseros-release.keystore
   KEYSTORE_PASSWORD=your_password
   KEY_ALIAS=browseros
   KEY_PASSWORD=your_key_password
   ```

3. Build signed APK:
   ```bash
   ./gradlew assembleRelease
   ```

### Building for Multiple Architectures

By default, builds for `arm64-v8a` and `x86_64`.

To build for specific architecture:
```gradle
android {
    defaultConfig {
        ndk {
            abiFilters.clear()
            abiFilters += "arm64-v8a"  // or "x86_64", "armeabi-v7a"
        }
    }
}
```

## License

BrowserOS is licensed under AGPL-3.0. See LICENSE file for details.
