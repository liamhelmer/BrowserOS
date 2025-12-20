# BrowserOS Android Architecture Diagrams

This document provides visual representations of the Android port architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BrowserOS Android App                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │     UI       │  │   Services   │  │   Native     │
    │   Layer      │  │    Layer     │  │   Layer      │
    └──────────────┘  └──────────────┘  └──────────────┘
         │                   │                   │
         │                   │                   │
    ┌────▼─────┐      ┌──────▼──────┐     ┌─────▼──────┐
    │MainActivity│    │ MCPService  │     │libmcp_     │
    │            │    │ (Foreground)│     │server.so   │
    │ Compose UI │    │             │     │            │
    │            │    │ AgentService│     │ CDP Server │
    │ WebView    │    │             │     │ MCP Server │
    └────┬─────┘      └──────┬──────┘     └─────┬──────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Android System  │
                    │  - WebView       │
                    │  - Storage       │
                    │  - Network       │
                    └──────────────────┘
```

## MCP Server Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Android Application                     │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐              ┌──────────────┐          │
│  │  WebView     │──────────────│ MainActivity │          │
│  │  (Browser)   │   Renders    │   (Compose)  │          │
│  └──────┬───────┘              └──────────────┘          │
│         │                                                  │
│         │ JavaScript Bridge                               │
│         │                                                  │
│  ┌──────▼────────────────────────────────────────────┐   │
│  │            MCPService (Foreground Service)        │   │
│  ├───────────────────────────────────────────────────┤   │
│  │                                                    │   │
│  │  Port Discovery                                    │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│  │  │CDP:9222 │  │MCP:9225 │  │Agent:.. │           │   │
│  │  └─────────┘  └─────────┘  └─────────┘           │   │
│  │                                                    │   │
│  │  Health Monitor                                    │   │
│  │  └─ Check every 30s                               │   │
│  │  └─ Auto-restart on failure                       │   │
│  │                                                    │   │
│  │  JNI Interface                                     │   │
│  │  ┌───────────────────────────────────────────┐   │   │
│  │  │ startNativeMCPServer()                    │   │   │
│  │  │ stopNativeMCPServer()                     │   │   │
│  │  │ isNativeMCPServerRunning()                │   │   │
│  │  └───────────────┬───────────────────────────┘   │   │
│  └──────────────────┼───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │        libmcp_server.so (Native Library)        │   │
│  ├─────────────────────────────────────────────────┤   │
│  │                                                  │   │
│  │  ┌──────────────────┐  ┌─────────────────────┐ │   │
│  │  │ CDP WebSocket    │  │ MCP HTTP Server     │ │   │
│  │  │ Server           │  │                     │ │   │
│  │  │                  │  │ /mcp      (API)     │ │   │
│  │  │ ws://localhost   │  │ /health   (Monitor) │ │   │
│  │  │    :9222         │  │ /init     (Setup)   │ │   │
│  │  └──────────────────┘  └─────────────────────┘ │   │
│  │                                                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
         │                              │
         │ WebSocket                    │ HTTP
         │                              │
    ┌────▼───────┐              ┌───────▼────────┐
    │   Chrome   │              │  External      │
    │  DevTools  │              │  MCP Clients   │
    │            │              │  (claude-code) │
    └────────────┘              └────────────────┘
```

## Agent Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AgentService (Background Service)          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Task Execution Engine                                  │
│  ┌───────────────────────────────────────────────┐     │
│  │                                                │     │
│  │  1. Receive Task                              │     │
│  │     └─ User prompt                            │     │
│  │                                                │     │
│  │  2. Plan Generation                           │     │
│  │     └─ AI Provider → Generate plan            │     │
│  │                                                │     │
│  │  3. Step Execution                            │     │
│  │     └─ Browser automation via CDP             │     │
│  │                                                │     │
│  │  4. Result Collection                         │     │
│  │     └─ Callback to UI                         │     │
│  │                                                │     │
│  └───────────────────────────────────────────────┘     │
│                                                          │
│  AI Provider Integration                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   OpenAI     │  │  Anthropic   │  │   Ollama    │  │
│  │   Client     │  │   Client     │  │   Client    │  │
│  │              │  │              │  │  (Local)    │  │
│  │ - API Key    │  │ - API Key    │  │ - Server URL│  │
│  │ - GPT-4      │  │ - Claude 3   │  │ - Local AI │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                             │
│                  ┌─────────▼──────────┐                 │
│                  │   HTTP Client      │                 │
│                  │   (OkHttp)         │                 │
│                  └────────────────────┘                 │
│                                                          │
│  CDP Client (Browser Control)                           │
│  ┌─────────────────────────────────────────────┐       │
│  │                                              │       │
│  │  WebSocket Connection to MCPService         │       │
│  │  └─ ws://localhost:9222                     │       │
│  │                                              │       │
│  │  Commands:                                  │       │
│  │  - Navigate(url)                            │       │
│  │  - Click(selector)                          │       │
│  │  - Type(selector, text)                     │       │
│  │  - ExtractText(selector)                    │       │
│  │  - Screenshot()                             │       │
│  │                                              │       │
│  └─────────────────────────────────────────────┘       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

### Browser Automation Flow

```
User Request
     │
     ▼
┌─────────────────┐
│  MainActivity   │
│  (User Input)   │
└────────┬────────┘
         │
         │ Intent/Binding
         ▼
┌─────────────────┐
│  AgentService   │
│  - Parse prompt │
│  - Create plan  │
└────────┬────────┘
         │
         │ CDP Commands
         ▼
┌─────────────────┐
│   MCPService    │
│   - Forward to  │
│     native lib  │
└────────┬────────┘
         │
         │ JNI Call
         ▼
┌─────────────────┐
│ libmcp_server   │
│ - Execute CDP   │
│ - Control WebView│
└────────┬────────┘
         │
         │ Result
         ▼
     WebView
     (Browser)
```

### MCP Server Request Flow

```
External Client (claude-code)
         │
         │ HTTP POST
         │ http://<device-ip>:9225/mcp
         ▼
┌─────────────────┐
│  Android Network│
│  Stack          │
└────────┬────────┘
         │
         │ localhost:9225
         ▼
┌─────────────────┐
│   MCPService    │
│   - Receive req │
│   - Validate    │
└────────┬────────┘
         │
         │ JNI Call
         ▼
┌─────────────────┐
│ libmcp_server   │
│ - Process MCP   │
│ - Execute CDP   │
└────────┬────────┘
         │
         │ Response
         ▼
    External Client
    (Result JSON)
```

## Component Interactions

```
┌──────────────┐         ┌──────────────┐
│   UI Layer   │◀───────▶│  ViewModel   │
└──────┬───────┘         └──────────────┘
       │
       │ Binding
       │
┌──────▼───────────────────────────────────┐
│         Service Layer                    │
│                                           │
│  ┌─────────────┐      ┌─────────────┐   │
│  │ MCPService  │      │AgentService │   │
│  │             │      │             │   │
│  │ - Lifecycle │      │ - AI Logic  │   │
│  │ - Ports     │◀────▶│ - Tasks     │   │
│  │ - Health    │      │ - Providers │   │
│  └──────┬──────┘      └──────┬──────┘   │
│         │                    │           │
└─────────┼────────────────────┼───────────┘
          │                    │
          │ JNI                │ HTTP/WebSocket
          │                    │
┌─────────▼────────────────────▼───────────┐
│         Native Layer                     │
│                                           │
│  libmcp_server.so                        │
│  - CDP Server                            │
│  - MCP Server                            │
│  - Browser Control                       │
│                                           │
└───────────────────────────────────────────┘
```

## Lifecycle States

### MCPService Lifecycle

```
App Launch
     │
     ▼
onCreate()
     │
     │ Initialize
     ▼
onStartCommand()
     │
     │ Start Foreground
     │ Show Notification
     ▼
startMCPServer()
     │
     │ Find Ports
     │ Load Native Lib
     ▼
Server Running
     │
     │ Health Checks (30s)
     │ ├─ OK → Continue
     │ └─ FAIL → Restart
     │
     │ User closes app
     ▼
Service Continues
(Foreground)
     │
     │ System low memory
     │ or User stops
     ▼
onDestroy()
     │
     │ Stop Server
     │ Cleanup Resources
     ▼
Service Stopped
```

### AgentService Lifecycle

```
User Initiates Task
     │
     ▼
Bind Service
     │
     ▼
onBind()
     │
     ▼
executeAgentTask()
     │
     ├─ onProgress()
     │  └─ Update UI
     │
     ├─ Execute Steps
     │  └─ CDP Commands
     │
     ├─ onComplete()
     │  └─ Show Result
     │
     └─ onError()
        └─ Handle Error
     │
     ▼
Unbind Service
     │
     ▼
onUnbind()
     │
     ▼
Service Idle
(or Destroyed)
```

## Thread Model

```
┌─────────────────────────────────────────┐
│          Main Thread (UI)               │
│  - Activity Lifecycle                   │
│  - Compose Recomposition                │
│  - User Input Handling                  │
└────────────┬────────────────────────────┘
             │
             │ Intent/Binding
             │
┌────────────▼────────────────────────────┐
│       Service Threads                   │
│                                          │
│  ┌─────────────────────────────────┐   │
│  │ Main Thread                     │   │
│  │ - Service Lifecycle             │   │
│  │ - Binder Calls                  │   │
│  └────────┬────────────────────────┘   │
│           │                             │
│  ┌────────▼────────────────────────┐   │
│  │ Background Threads (Coroutines) │   │
│  │ - Network IO                    │   │
│  │ - Health Checks                 │   │
│  │ - AI Provider Calls             │   │
│  └────────┬────────────────────────┘   │
│           │                             │
└───────────┼─────────────────────────────┘
            │
            │ JNI
            │
┌───────────▼─────────────────────────────┐
│       Native Threads (C++)              │
│  - WebSocket Server                     │
│  - HTTP Server                          │
│  - CDP Processing                       │
└─────────────────────────────────────────┘
```

## Security Architecture

```
┌───────────────────────────────────────────┐
│           Android Security                │
├───────────────────────────────────────────┤
│                                            │
│  ┌─────────────────────────────────┐     │
│  │     App Sandbox                 │     │
│  │  - Private storage              │     │
│  │  - Process isolation            │     │
│  └─────────────────────────────────┘     │
│                                            │
│  ┌─────────────────────────────────┐     │
│  │     Network Security            │     │
│  │  - HTTPS only (external)        │     │
│  │  - Cleartext OK (localhost)     │     │
│  │  - Certificate pinning          │     │
│  └─────────────────────────────────┘     │
│                                            │
│  ┌─────────────────────────────────┐     │
│  │     Data Security               │     │
│  │  - Android Keystore (API keys)  │     │
│  │  - Encrypted SharedPrefs        │     │
│  │  - Secure file storage          │     │
│  └─────────────────────────────────┘     │
│                                            │
│  ┌─────────────────────────────────┐     │
│  │     Runtime Permissions         │     │
│  │  - Internet                     │     │
│  │  - Notifications                │     │
│  │  - Storage (optional)           │     │
│  └─────────────────────────────────┘     │
│                                            │
└───────────────────────────────────────────┘
```

## Storage Architecture

```
┌─────────────────────────────────────────┐
│        Android Storage                  │
├─────────────────────────────────────────┤
│                                          │
│  App Private Storage                    │
│  (/data/data/com.browseros.app/)        │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  SharedPreferences             │    │
│  │  - MCP port settings           │    │
│  │  - AI provider config          │    │
│  │  - User preferences            │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  Android Keystore              │    │
│  │  - OpenAI API key              │    │
│  │  - Anthropic API key           │    │
│  │  - Other secrets               │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  Room Database                 │    │
│  │  - Agent task history          │    │
│  │  - Conversation logs           │    │
│  │  - Bookmarks                   │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  Cache                         │    │
│  │  - WebView cache               │    │
│  │  - Temp files                  │    │
│  └────────────────────────────────┘    │
│                                          │
│  External Storage (Scoped)              │
│  (/storage/emulated/0/Android/data/)    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  Downloads                     │    │
│  │  - User downloaded files       │    │
│  └────────────────────────────────┘    │
│                                          │
└─────────────────────────────────────────┘
```

---

These diagrams provide a comprehensive view of the Android port architecture and should help developers understand how all components interact.

