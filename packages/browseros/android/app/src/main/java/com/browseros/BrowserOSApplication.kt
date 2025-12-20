package com.browseros.app

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.work.Configuration
import androidx.work.WorkManager

/**
 * BrowserOS Application class
 * Initializes app-wide components and services
 */
class BrowserOSApplication : Application(), Configuration.Provider {

    override fun onCreate() {
        super.onCreate()
        
        // Initialize notification channels
        createNotificationChannels()
        
        // Initialize WorkManager for background tasks
        WorkManager.initialize(this, workManagerConfiguration)
    }

    override fun getWorkManagerConfiguration(): Configuration {
        return Configuration.Builder()
            .setMinimumLoggingLevel(android.util.Log.INFO)
            .build()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            // MCP Service notification channel
            val mcpChannel = NotificationChannel(
                CHANNEL_MCP_SERVICE,
                "MCP Server",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "BrowserOS MCP server status"
                setShowBadge(false)
            }
            notificationManager.createNotificationChannel(mcpChannel)

            // Agent notifications channel
            val agentChannel = NotificationChannel(
                CHANNEL_AGENT,
                "AI Agent",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "AI Agent task notifications"
                setShowBadge(true)
            }
            notificationManager.createNotificationChannel(agentChannel)

            // Updates channel
            val updatesChannel = NotificationChannel(
                CHANNEL_UPDATES,
                "Updates",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "App update notifications"
                setShowBadge(true)
            }
            notificationManager.createNotificationChannel(updatesChannel)
        }
    }

    companion object {
        const val CHANNEL_MCP_SERVICE = "mcp_service"
        const val CHANNEL_AGENT = "agent"
        const val CHANNEL_UPDATES = "updates"
    }
}
