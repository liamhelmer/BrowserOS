# BrowserOS Android - Developer Quick Start

## 🚀 Get Started in 5 Minutes

This guide gets you up and running with BrowserOS Android development quickly.

## Prerequisites Check

```bash
# Check Android SDK
echo $ANDROID_HOME
# Should print: /Users/<username>/Library/Android/sdk (macOS)
#            or /home/<username>/Android/Sdk (Linux)

# Check Java
java -version
# Should show Java 11 or higher

# Check Gradle (optional, wrapper is included)
./gradlew --version
```

If any are missing, see [Android Installation Guide](../docs/android-installation.md).

## Quick Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/browseros-ai/BrowserOS.git
cd BrowserOS

# Initialize submodules
git submodule update --init --recursive

# Navigate to Android project
cd packages/browseros/android
```

### 2. Open in Android Studio

```bash
# Option A: Command line (macOS)
open -a "Android Studio" .

# Option B: Command line (Linux)
studio .

# Option C: Manual
# Launch Android Studio → File → Open → Select android/ directory
```

### 3. Sync and Build

In Android Studio:
1. Wait for Gradle sync to complete
2. Click "Build" → "Make Project"
3. Or run in terminal:

```bash
./gradlew build
```

### 4. Run on Device/Emulator

**Using Android Studio:**
1. Connect device or start emulator
2. Click "Run" button (green triangle)

**Using Command Line:**
```bash
# Debug build
./gradlew installDebug

# Launch app
adb shell am start -n com.browseros.app/.MainActivity
```

## Project Structure Quick Reference

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/browseros/
│   │   │   ├── BrowserOSApplication.kt     # App entry point
│   │   │   ├── MainActivity.kt             # Main UI
│   │   │   ├── services/
│   │   │   │   ├── MCPService.kt          # MCP server (background)
│   │   │   │   └── AgentService.kt        # AI agent logic
│   │   │   └── ui/
│   │   │       ├── BrowserScreen.kt       # Browser WebView UI
│   │   │       └── theme/Theme.kt         # Material theme
│   │   ├── cpp/                           # Native code
│   │   │   └── mcp_server/                # MCP server JNI
│   │   ├── res/                           # Resources (layouts, strings)
│   │   └── AndroidManifest.xml            # App config & permissions
│   └── build.gradle.kts                    # App build config
├── build.gradle.kts                        # Root build config
└── settings.gradle.kts                     # Gradle settings
```

## Common Development Tasks

### Build Debug APK

```bash
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

### Build Release APK

```bash
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/app-release-unsigned.apk
```

### Run Tests

```bash
# Unit tests
./gradlew test

# Instrumented tests (requires device/emulator)
./gradlew connectedAndroidTest
```

### Clean Build

```bash
./gradlew clean
```

### View Logs

```bash
# All app logs
adb logcat | grep BrowserOS

# MCP Service logs only
adb logcat | grep MCPService

# Save logs to file
adb logcat -d > browseros.log
```

### Install on Multiple Devices

```bash
# List connected devices
adb devices

# Install on specific device
adb -s <device-id> install app/build/outputs/apk/debug/app-debug.apk
```

## Key Files to Modify

| What you want to do | File to modify |
|---------------------|----------------|
| Change app name | `app/src/main/res/values/strings.xml` |
| Add permissions | `app/src/main/AndroidManifest.xml` |
| Modify UI | `app/src/main/java/com/browseros/ui/BrowserScreen.kt` |
| Add dependencies | `app/build.gradle.kts` |
| Configure MCP server | `app/src/main/java/com/browseros/services/MCPService.kt` |
| Add AI providers | `app/src/main/java/com/browseros/services/AgentService.kt` |
| Customize theme | `app/src/main/java/com/browseros/ui/theme/Theme.kt` |

## Troubleshooting

### Gradle Sync Failed

```bash
# Clear Gradle cache
rm -rf ~/.gradle/caches/
./gradlew clean build --refresh-dependencies
```

### SDK Not Found

```bash
# Set Android SDK path
export ANDROID_HOME=/path/to/Android/Sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
```

### NDK Not Found

Install via Android Studio:
1. Tools → SDK Manager
2. SDK Tools tab
3. Check "NDK (Side by side)"
4. Click Apply

### Build Too Slow

```bash
# Enable Gradle daemon and parallel builds
echo "org.gradle.daemon=true" >> gradle.properties
echo "org.gradle.parallel=true" >> gradle.properties
```

### App Crashes on Launch

```bash
# Check crash logs
adb logcat | grep AndroidRuntime

# Clear app data and reinstall
adb shell pm clear com.browseros.app
./gradlew installDebug
```

## Next Steps

### Implement Features

1. **MCP Server**: Edit `services/MCPService.kt` to add actual server logic
2. **AI Integration**: Modify `services/AgentService.kt` for AI provider APIs
3. **UI Improvements**: Enhance `ui/BrowserScreen.kt` with tabs, bookmarks
4. **Settings**: Create Settings Activity for user preferences

### Testing

1. Write unit tests in `app/src/test/`
2. Write UI tests in `app/src/androidTest/`
3. Add integration tests for MCP server

### Resources

- [Android Developer Guide](https://developer.android.com/guide)
- [Jetpack Compose Tutorial](https://developer.android.com/jetpack/compose/tutorial)
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [Android Services](https://developer.android.com/guide/components/services)

## Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/browseros-ai/BrowserOS/issues)
- **Discord**: [Join community](https://discord.gg/YKwjt5vuKr)
- **Documentation**: [Full docs](https://docs.browseros.com)

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

Quick checklist:
- [ ] Fork the repository
- [ ] Create feature branch
- [ ] Make changes
- [ ] Test on device/emulator
- [ ] Submit pull request

---

Happy coding! 🎉
