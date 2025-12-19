package com.browseros.app

import android.content.Intent
import android.os.Bundle
import android.webkit.WebView
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.browseros.app.services.MCPService
import com.browseros.app.ui.BrowserScreen
import com.browseros.app.ui.theme.BrowserOSTheme

/**
 * Main Activity for BrowserOS
 * Manages the browser UI and MCP service lifecycle
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Enable WebView debugging in debug builds
        if (BuildConfig.DEBUG) {
            WebView.setWebContentsDebuggingEnabled(true)
        }

        // Start MCP service
        startMCPService()

        setContent {
            BrowserOSTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    BrowserScreen(
                        onSettingsClick = { openSettings() },
                        onNewTabClick = { /* Handle new tab */ }
                    )
                }
            }
        }

        // Handle intent (deep links, web intents)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        intent?.let { handleIntent(it) }
    }

    private fun handleIntent(intent: Intent) {
        when (intent.action) {
            Intent.ACTION_VIEW -> {
                // Handle web URL
                val url = intent.dataString
                // TODO: Load URL in browser
            }
        }
    }

    private fun startMCPService() {
        val intent = Intent(this, MCPService::class.java)
        startForegroundService(intent)
    }

    private fun openSettings() {
        // TODO: Open settings activity
    }

    override fun onDestroy() {
        super.onDestroy()
        // Note: MCP service continues running as foreground service
    }
}
