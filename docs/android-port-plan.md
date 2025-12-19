# BrowserOS Android Port - Technical Plan

## Executive Summary

This document outlines the technical plan for porting BrowserOS (Chromium-based browser with MCP server) to the Android platform. The port will enable Android users to run AI agents natively in their browser with privacy-first local processing.

## Current Architecture

### Components
1. **BrowserOS Client**: Chromium 142-based browser (macOS, Windows, Linux)
2. **MCP Server**: Native binary providing Model Context Protocol endpoints
3. **BrowserOS Agent**: Chrome extension (TypeScript/React) for AI agent functionality

### MCP Server Features
- CDP (Chrome DevTools Protocol) WebSocket server
- MCP HTTP endpoints on configurable ports
- Agent control endpoints
- Extension communication endpoints
- Health monitoring and auto-restart

## Android Port Strategy

### 1. Chromium Android Build

**Approach**: Use Chromium's existing Android build system

**Implementation**:
- Leverage Chromium's Android build configuration
- Apply BrowserOS patches to Android-specific code paths
- Build APK using Chromium's GN + Ninja build system

**Key Files to Create/Modify**:
- `packages/browseros/build/modules/package/android.py` - Android APK packaging
- `packages/browseros/chromium_patches/chrome/android/` - Android-specific patches
- Android GN build configurations

### 2. MCP Server Android Port

**Challenge**: Android apps run in sandboxed environments with limited background process support

**Solution Options**:

#### Option A: Embedded MCP Server (Recommended)
- Compile MCP server as Android native library (.so)
- Run as Android Service bound to main app
- Use Android IPC (AIDL/Binder) for communication
- Leverage WorkManager for background tasks

**Advantages**:
- Better integration with Android lifecycle
- No separate binary management
- Better battery optimization
- More secure (app sandbox)

#### Option B: Separate Binary
- Bundle MCP server as native executable
- Launch via ProcessBuilder in app's private directory
- Similar to desktop approach

**Disadvantages**:
- Complex lifecycle management
- Background execution restrictions
- Battery concerns

**Recommended**: Option A with the following architecture:
```
BrowserOSApp (APK)
├── WebView/ChromiumView (Browser UI)
├── MCPService (Android Service)
│   ├── libmcp_server.so (native library)
│   ├── CDP WebSocket server
│   └── MCP HTTP endpoints
└── AgentService (Chrome extension functionality)
```

### 3. BrowserOS Agent Android Adaptation

**Challenge**: Chrome extensions don't work on Android

**Solution**: Reimplement as native Android components

**Architecture**:
```
Android App
├── WebView with JavaScript bridge
├── AgentService (background service)
│   ├── AI provider integration (OpenAI, Anthropic, Ollama)
│   ├── Browser automation via CDP
│   └── MCP client implementation
└── UI Components
    ├── Settings Activity
    ├── Chat Interface (Fragment)
    └── Agent Status (Notification)
```

**Migration Strategy**:
- Port TypeScript business logic to Kotlin
- Use WebView JavaScript bridge for browser interaction
- Implement native UI using Android Jetpack Compose or Material Design
- Maintain API compatibility with desktop version

### 4. Android-Specific Considerations

#### Storage
- SharedPreferences for app settings
- Room database for agent history
- FileProvider for secure file sharing
- Scoped storage for user data

#### Networking
- Require INTERNET permission
- Use OkHttp for HTTP client (MCP requests)
- WebSocket support via OkHttp
- Network security config for local servers

#### Background Execution
- Foreground Service for MCP server (persistent notification)
- WorkManager for periodic health checks
- Doze mode exemption requests (if needed)
- Battery optimization whitelisting guidance

#### Security
- Android Keystore for API keys
- Certificate pinning for external APIs
- No cleartext traffic (except localhost)
- Runtime permissions for sensitive features

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Android Studio project structure
- [ ] Create basic Android app skeleton
- [ ] Configure Chromium Android build
- [ ] Apply BrowserOS patches to Android codebase

### Phase 2: MCP Server Port (Weeks 3-4)
- [ ] Design MCPService architecture
- [ ] Port server code to native Android library
- [ ] Implement Service lifecycle management
- [ ] Test CDP WebSocket on Android
- [ ] Test MCP HTTP endpoints

### Phase 3: Agent Implementation (Weeks 5-6)
- [ ] Port agent business logic to Kotlin
- [ ] Implement JavaScript bridge for WebView
- [ ] Create Settings UI
- [ ] Implement AI provider integrations
- [ ] Build chat interface

### Phase 4: Integration (Week 7)
- [ ] Connect MCP server with Agent
- [ ] Implement browser automation
- [ ] Test end-to-end agent workflows
- [ ] Performance optimization

### Phase 5: Polish & Release (Week 8)
- [ ] UI/UX refinement
- [ ] Battery optimization
- [ ] Documentation
- [ ] Play Store preparation
- [ ] APK signing and distribution

## Technical Requirements

### Build Environment
- Android Studio (latest stable)
- Android NDK r26+
- Chromium build tools (depot_tools)
- Python 3.11+
- Minimum API Level: 26 (Android 8.0)
- Target API Level: 34 (Android 14)

### Dependencies
- AndroidX libraries
- Jetpack Compose (UI)
- Room (database)
- OkHttp (networking)
- Kotlinx Coroutines
- Chromium WebView or Custom Tabs

### Permissions Required
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

## Build System Integration

### New Build Modules

#### `packages/browseros/build/modules/package/android.py`
```python
class AndroidPackageModule(PackageModule):
    """Builds Android APK from Chromium build + BrowserOS components"""
    
    def validate(self):
        # Check Android SDK, NDK, build tools
        
    def execute(self):
        # 1. Build Chromium for Android
        # 2. Build MCP server native library
        # 3. Package agent resources
        # 4. Create APK
        # 5. Sign APK
```

### Build Configuration
Add to `packages/browseros/build/common/utils.py`:
```python
def IS_ANDROID():
    return platform.system() == "Linux" and os.environ.get("ANDROID_BUILD") == "1"
```

## File Structure

```
packages/browseros/
├── android/                          # New Android project
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/browseros/
│   │   │   │   ├── BrowserOSActivity.kt
│   │   │   │   ├── services/
│   │   │   │   │   ├── MCPService.kt
│   │   │   │   │   └── AgentService.kt
│   │   │   │   ├── ui/
│   │   │   │   └── utils/
│   │   │   ├── cpp/                  # Native MCP server
│   │   │   │   └── mcp_server/
│   │   │   ├── res/
│   │   │   └── AndroidManifest.xml
│   │   ├── build.gradle.kts
│   │   └── proguard-rules.pro
│   ├── gradle/
│   ├── build.gradle.kts
│   └── settings.gradle.kts
├── chromium_patches/
│   └── chrome/android/              # New Android patches
└── resources/binaries/browseros_server/
    ├── browseros-server-android-arm64.so
    └── browseros-server-android-x86_64.so
```

## Distribution Strategy

### APK Distribution
1. **GitHub Releases**: Direct APK download
2. **Website**: https://files.browseros.com/download/BrowserOS.apk
3. **Google Play Store**: (Future, requires compliance review)

### Update Mechanism
- Check for updates via GitHub API
- Download APK updates
- Use Android's PackageInstaller API
- (Alternative) Use in-app update API if on Play Store

## Testing Strategy

### Unit Tests
- Kotlin/Java code (JUnit, Mockito)
- Native code (Google Test)

### Integration Tests
- Espresso for UI testing
- CDP/MCP endpoint testing
- Agent workflow testing

### Manual Testing
- Device matrix (Samsung, Pixel, OnePlus, etc.)
- Android versions (8.0 - 14)
- Different screen sizes and densities
- Battery impact testing
- Network condition testing

## Challenges and Mitigations

### Challenge 1: Chromium Build Complexity
**Mitigation**: Use Chromium's existing Android build system, apply minimal patches

### Challenge 2: Background Service Limitations
**Mitigation**: Use Foreground Service with notification, educate users about battery optimization

### Challenge 3: Chrome Extension Incompatibility
**Mitigation**: Rewrite as native Android app with equivalent functionality

### Challenge 4: Storage and Permissions
**Mitigation**: Follow Android best practices, request permissions at runtime

### Challenge 5: APK Size
**Mitigation**: 
- Use app bundles for Play Store
- Separate native libraries by architecture
- Remove unused Chromium components

## Success Criteria

- [ ] Android APK builds successfully
- [ ] MCP server runs as Android service
- [ ] Agent can control browser via CDP
- [ ] AI providers integrate correctly
- [ ] App passes Android security review
- [ ] Battery usage is acceptable (< 5% per hour active use)
- [ ] APK size < 150MB
- [ ] Performance comparable to desktop version

## Future Enhancements

1. **Tablet Support**: Optimize UI for larger screens
2. **Chrome OS Support**: Leverage Android compatibility
3. **Android TV**: Voice-controlled AI agent
4. **Wear OS**: Companion app for quick commands
5. **Widgets**: Home screen widgets for quick access

## References

- [Chromium Android Build Instructions](https://chromium.googlesource.com/chromium/src/+/main/docs/android_build_instructions.md)
- [Android Services](https://developer.android.com/guide/components/services)
- [WebView Best Practices](https://developer.android.com/guide/webapps/webview)
- [Android App Architecture](https://developer.android.com/topic/architecture)
