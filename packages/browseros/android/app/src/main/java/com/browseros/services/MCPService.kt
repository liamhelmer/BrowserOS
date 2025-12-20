package com.browseros.app.services

import android.app.Notification
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.browseros.app.BrowserOSApplication
import com.browseros.app.MainActivity
import com.browseros.app.R
import kotlinx.coroutines.*
import java.io.IOException
import java.net.ServerSocket

/**
 * MCP Service - Manages the MCP (Model Context Protocol) server
 * 
 * This service runs as a foreground service and manages:
 * - CDP (Chrome DevTools Protocol) WebSocket server
 * - MCP HTTP endpoints
 * - Health monitoring and auto-restart
 * 
 * The service is implemented as a pure Kotlin service for now.
 * In a full implementation, this would load and manage native
 * MCP server libraries.
 */
class MCPService : Service() {

    private val binder = MCPBinder()
    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    private var cdpPort: Int = 0
    private var mcpPort: Int = 0
    private var isServerRunning = false

    // Native library hooks (to be implemented)
    private external fun startNativeMCPServer(cdpPort: Int, mcpPort: Int): Boolean
    private external fun stopNativeMCPServer()
    private external fun isNativeMCPServerRunning(): Boolean

    companion object {
        private const val TAG = "MCPService"
        private const val NOTIFICATION_ID = 1001
        private const val CDP_PORT_START = 9222
        private const val MCP_PORT_START = 9225
        
        init {
            try {
                // Load native library if available
                System.loadLibrary("mcp_server")
            } catch (e: UnsatisfiedLinkError) {
                Log.w(TAG, "Native MCP server library not available, running in stub mode")
            }
        }
    }

    inner class MCPBinder : Binder() {
        fun getService(): MCPService = this@MCPService
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "MCP Service created")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "MCP Service starting")

        // Start as foreground service with notification
        startForeground(NOTIFICATION_ID, createNotification())

        // Start MCP server in background
        serviceScope.launch {
            startMCPServer()
        }

        return START_STICKY // Restart service if killed
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "MCP Service destroying")
        
        stopMCPServer()
        serviceScope.cancel()
    }

    private fun createNotification(): Notification {
        val notificationIntent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            notificationIntent,
            PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, BrowserOSApplication.CHANNEL_MCP_SERVICE)
            .setContentTitle("BrowserOS")
            .setContentText("MCP server running")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build()
    }

    private suspend fun startMCPServer() = withContext(Dispatchers.IO) {
        try {
            // Find available ports
            cdpPort = findAvailablePort(CDP_PORT_START)
            mcpPort = findAvailablePort(MCP_PORT_START)

            Log.i(TAG, "Starting MCP server on CDP:$cdpPort, MCP:$mcpPort")

            // TODO: Start native MCP server
            // For now, this is a stub implementation
            isServerRunning = true
            
            // Start health monitoring
            monitorServerHealth()

            Log.i(TAG, "MCP server started successfully")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start MCP server", e)
            isServerRunning = false
        }
    }

    private fun stopMCPServer() {
        if (!isServerRunning) return

        try {
            Log.i(TAG, "Stopping MCP server")
            
            // TODO: Stop native MCP server
            isServerRunning = false
            
            Log.i(TAG, "MCP server stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping MCP server", e)
        }
    }

    private suspend fun monitorServerHealth() = withContext(Dispatchers.IO) {
        while (isServerRunning && isActive) {
            try {
                // TODO: Check server health via HTTP endpoint
                // For now, just log status
                Log.d(TAG, "MCP server health check: OK")
                delay(30000) // Check every 30 seconds
            } catch (e: Exception) {
                Log.e(TAG, "Health check failed", e)
                // Attempt restart
                restartServer()
                break
            }
        }
    }

    private suspend fun restartServer() {
        Log.w(TAG, "Restarting MCP server")
        stopMCPServer()
        delay(1000)
        startMCPServer()
    }

    private fun findAvailablePort(startPort: Int): Int {
        var port = startPort
        while (port < startPort + 100) {
            if (isPortAvailable(port)) {
                return port
            }
            port++
        }
        throw IOException("No available ports in range $startPort-${startPort + 100}")
    }

    private fun isPortAvailable(port: Int): Boolean {
        return try {
            ServerSocket(port).use { true }
        } catch (e: IOException) {
            false
        }
    }

    // Public API for binding clients
    fun getCDPPort(): Int = cdpPort
    fun getMCPPort(): Int = mcpPort
    fun isRunning(): Boolean = isServerRunning
}
