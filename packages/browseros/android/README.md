# BrowserOS for Android

Privacy-first AI browser for Android with native MCP server support.

## Features

- ✅ **Chromium-based Browser** - Full web browsing experience
- ✅ **Native MCP Server** - Run MCP server directly on your Android device
- ✅ **AI Agent Support** - Automate browsing tasks with AI
- ✅ **Privacy First** - Your data stays on your device
- ✅ **Local AI Models** - Support for Ollama and local models
- ✅ **WebView Integration** - Lightweight and efficient

## Quick Start

### Download

- **GitHub Releases**: [Download latest APK](https://github.com/browseros-ai/BrowserOS/releases)
- **Direct Download**: [BrowserOS.apk](https://files.browseros.com/download/BrowserOS.apk)

### Install

```bash
# Download APK
wget https://files.browseros.com/download/BrowserOS.apk

# Install on connected device
adb install BrowserOS.apk
```

Or transfer APK to your device and install via file manager.

### First Run

1. Launch BrowserOS
2. Grant required permissions (Notifications)
3. Configure AI provider (Settings → AI Provider)
4. Start browsing!

## Requirements

- **Android Version**: 8.0 (API 26) or higher
- **Architecture**: ARM64 or x86_64
- **Storage**: ~150 MB for app + cache
- **RAM**: 2 GB minimum, 4 GB recommended

## MCP Server

BrowserOS includes a built-in MCP (Model Context Protocol) server that runs on your Android device.

### Access MCP Server

The MCP server runs on port **9225** by default.

**From same device:**
```
http://localhost:9225/mcp
```

**From another device on same network:**
```
http://<device-ip>:9225/mcp
```

### Using with Claude Code

```bash
# Find your device IP
adb shell ip addr show wlan0

# Add to Claude Code
claude mcp add --transport http browseros http://<device-ip>:9225/mcp
```

### Port Forwarding (for emulator or development)

```bash
adb forward tcp:9225 tcp:9225
adb forward tcp:9222 tcp:9222
```

Then access via:
```
http://localhost:9225/mcp
```

## Building from Source

See [Android Installation Guide](../docs/android-installation.md) for detailed build instructions.

**Quick build:**

```bash
# Clone repository
git clone https://github.com/browseros-ai/BrowserOS.git
cd BrowserOS/packages/browseros/android

# Build release APK
./gradlew assembleRelease
```

## Project Structure

```
packages/browseros/android/
├── app/
│   ├── src/main/
│   │   ├── java/com/browseros/
│   │   │   ├── BrowserOSApplication.kt      # App initialization
│   │   │   ├── MainActivity.kt              # Main browser UI
│   │   │   ├── services/
│   │   │   │   ├── MCPService.kt           # MCP server service
│   │   │   │   └── AgentService.kt         # AI agent service
│   │   │   └── ui/
│   │   │       ├── BrowserScreen.kt        # Browser WebView
│   │   │       └── theme/                  # Material Design theme
│   │   ├── cpp/
│   │   │   └── mcp_server/                 # Native MCP server
│   │   ├── res/                            # Resources
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts                     # App build config
├── build.gradle.kts                         # Root build config
└── settings.gradle.kts                      # Gradle settings
```

## Development

### Prerequisites

- Android Studio (latest stable)
- Android SDK (API 26-34)
- Android NDK r26+
- JDK 11+

### Setup

```bash
# Clone and navigate
git clone https://github.com/browseros-ai/BrowserOS.git
cd BrowserOS/packages/browseros/android

# Open in Android Studio
# File → Open → Select android/ directory

# Sync Gradle
# Build → Make Project
```

### Debug Build

```bash
# Build and install debug version
./gradlew installDebug

# View logs
adb logcat | grep BrowserOS
```

### Testing

```bash
# Run unit tests
./gradlew test

# Run instrumented tests (requires device/emulator)
./gradlew connectedAndroidTest
```

## Configuration

### AI Providers

Configure AI providers in Settings:

**OpenAI:**
- Settings → AI Provider → OpenAI
- Enter API key
- Select model (GPT-4, GPT-3.5-turbo)

**Anthropic:**
- Settings → AI Provider → Anthropic
- Enter API key
- Select model (Claude 3 Opus, Sonnet)

**Ollama (Local):**
- Install Ollama on accessible device
- Settings → AI Provider → Ollama
- Enter Ollama server URL
- Select installed model

### MCP Server Settings

- **CDP Port**: Chrome DevTools Protocol port (default: 9222)
- **MCP Port**: Model Context Protocol port (default: 9225)
- **Auto-start**: Start MCP server on app launch
- **Persistent**: Keep server running in background

### Permissions

**Required:**
- **Internet** - For web browsing and AI providers
- **Network State** - Check connectivity
- **Foreground Service** - MCP server background operation
- **Notifications** - Service status and agent updates

**Optional:**
- **Storage** - Download files
- **Camera** - Upload photos
- **Microphone** - Voice input (future)

## Troubleshooting

### MCP Server Issues

**Server not starting:**
1. Check Settings → MCP Server → Status
2. View logs: `adb logcat | grep MCPService`
3. Restart app

**Cannot connect from external device:**
1. Ensure devices on same WiFi network
2. Check firewall settings
3. Verify port is open: `netstat -an | grep 9225`

### WebView Issues

**Pages not loading:**
1. Check internet connection
2. Clear app cache: Settings → Apps → BrowserOS → Clear Cache
3. Update Android System WebView

**Slow performance:**
1. Close unused tabs
2. Clear browsing data
3. Restart app

### Battery Drain

**High battery usage:**
1. MCP server runs as foreground service (expected behavior)
2. Normal usage: 3-5% per hour
3. Disable battery optimization: Settings → Apps → BrowserOS → Battery → Unrestricted

## Security & Privacy

- **Local Processing**: AI models can run locally via Ollama
- **API Keys**: Stored securely using Android Keystore
- **HTTPS Only**: All external connections use HTTPS (except localhost)
- **No Telemetry**: No tracking or analytics (privacy-first)
- **Open Source**: Full source code available for audit

## Roadmap

- [ ] **Chrome Extension Support** - Limited extension compatibility
- [ ] **Tab Management** - Multiple tabs and tab groups
- [ ] **Bookmarks & History** - Full browsing history and bookmarks
- [ ] **Sync** - Cross-device sync (optional, encrypted)
- [ ] **Voice Input** - Voice commands for AI agent
- [ ] **Tablet Optimization** - Better UI for tablets
- [ ] **Android TV** - Voice-controlled AI browser for TV
- [ ] **Wear OS** - Companion app for quick commands

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

**Areas needing help:**
- Native MCP server implementation
- Android UI improvements
- Battery optimization
- Testing on various devices
- Documentation

## Support

- **GitHub Issues**: [Report bugs](https://github.com/browseros-ai/BrowserOS/issues)
- **Discord**: [Join community](https://discord.gg/YKwjt5vuKr)
- **Slack**: [BrowserOS Slack](https://dub.sh/browserOS-slack)
- **Documentation**: [docs.browseros.com](https://docs.browseros.com)

## License

BrowserOS is licensed under **AGPL-3.0**. See [LICENSE](../../LICENSE) for details.

## Acknowledgments

- Built on [Chromium](https://www.chromium.org/)
- Inspired by [Claude Code](https://www.anthropic.com/)
- Android development with [Jetpack Compose](https://developer.android.com/jetpack/compose)

---

Made with ❤️ for the Android community
