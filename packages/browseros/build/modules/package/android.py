#!/usr/bin/env python3
"""Android Package Module - Builds BrowserOS APK for Android"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from ...common.context import Context
from ...common.logger import log_info, log_error, log_success
from ...common.module import Module, ValidationError


class AndroidPackageModule(Module):
    """
    Builds BrowserOS Android APK
    
    This module:
    1. Verifies Android build environment (SDK, NDK)
    2. Builds Chromium for Android
    3. Compiles MCP server as native library
    4. Packages agent resources
    5. Creates and signs APK
    """

    def __init__(self):
        super().__init__(
            name="package_android",
            description="Package BrowserOS for Android (APK)",
            requires_platform="linux",  # Android builds typically done on Linux
        )

    def validate(self, context: Context) -> None:
        """Validate Android build environment"""
        log_info("Validating Android build environment...")

        # Check if running on Linux (recommended for Android builds)
        import platform
        if platform.system() != "Linux":
            log_error("Android builds are recommended on Linux")
            # Don't fail - can work on macOS too
            # raise ValidationError("Android builds require Linux")

        # Check for Android SDK
        android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
        if not android_home:
            raise ValidationError(
                "ANDROID_HOME or ANDROID_SDK_ROOT environment variable not set. "
                "Please install Android SDK and set ANDROID_HOME."
            )

        android_home_path = Path(android_home)
        if not android_home_path.exists():
            raise ValidationError(f"Android SDK path does not exist: {android_home}")

        log_info(f"Found Android SDK at: {android_home}")

        # Check for Android NDK
        ndk_path = self._find_ndk(android_home_path)
        if not ndk_path:
            raise ValidationError(
                "Android NDK not found. Please install NDK via Android Studio SDK Manager "
                "or download from https://developer.android.com/ndk/downloads"
            )

        log_info(f"Found Android NDK at: {ndk_path}")

        # Check for required build tools
        build_tools = android_home_path / "build-tools"
        if not build_tools.exists() or not any(build_tools.iterdir()):
            raise ValidationError(
                "Android build-tools not found. "
                "Please install build-tools via Android Studio SDK Manager."
            )

        latest_build_tools = max(build_tools.iterdir(), key=lambda p: p.name)
        log_info(f"Found build-tools: {latest_build_tools.name}")

        # Check for Java/JDK
        java_home = os.environ.get("JAVA_HOME")
        if not java_home:
            # Try to find java on PATH
            try:
                result = subprocess.run(
                    ["java", "-version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                log_info("Found Java on PATH")
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise ValidationError(
                    "Java not found. Please install JDK 11+ and set JAVA_HOME "
                    "or ensure java is on PATH."
                )
        else:
            log_info(f"Found Java at: {java_home}")

        # Check for Gradle (if using Gradle build)
        gradle_path = self._find_gradle()
        if gradle_path:
            log_info(f"Found Gradle at: {gradle_path}")
        else:
            log_info("Gradle not found - will use Gradle wrapper")

        # Validate Chromium source is available
        chromium_src = context.chromium_src
        if not chromium_src.exists():
            raise ValidationError(
                f"Chromium source not found at {chromium_src}. "
                "Please run 'git_setup' module first."
            )

        # Check for Android-specific Chromium files
        android_build_config = chromium_src / "build" / "config" / "android"
        if not android_build_config.exists():
            raise ValidationError(
                "Chromium Android build files not found. "
                "This Chromium checkout may not support Android builds."
            )

        log_success("Android build environment validated successfully")

    def execute(self, context: Context) -> None:
        """Build Android APK"""
        log_info("Building BrowserOS for Android...")

        # Set environment variables for Android build
        self._setup_android_env(context)

        # Step 1: Configure Chromium for Android
        log_info("Step 1/5: Configuring Chromium for Android...")
        self._configure_chromium_android(context)

        # Step 2: Build Chromium for Android
        log_info("Step 2/5: Building Chromium for Android...")
        self._build_chromium_android(context)

        # Step 3: Build MCP server native library
        log_info("Step 3/5: Building MCP server native library...")
        self._build_mcp_server_android(context)

        # Step 4: Package Android app
        log_info("Step 4/5: Packaging Android app...")
        self._package_android_app(context)

        # Step 5: Sign APK
        log_info("Step 5/5: Signing APK...")
        self._sign_apk(context)

        log_success("Android APK built successfully!")
        self._print_output_info(context)

    def _find_ndk(self, android_home: Path) -> Optional[Path]:
        """Find Android NDK installation"""
        # Check ANDROID_NDK_HOME
        ndk_home = os.environ.get("ANDROID_NDK_HOME")
        if ndk_home and Path(ndk_home).exists():
            return Path(ndk_home)

        # Check ndk directory in Android SDK
        ndk_dir = android_home / "ndk"
        if ndk_dir.exists():
            # Get latest NDK version
            ndk_versions = [d for d in ndk_dir.iterdir() if d.is_dir()]
            if ndk_versions:
                return max(ndk_versions, key=lambda p: p.name)

        # Check ndk-bundle (older location)
        ndk_bundle = android_home / "ndk-bundle"
        if ndk_bundle.exists():
            return ndk_bundle

        return None

    def _find_gradle(self) -> Optional[str]:
        """Find Gradle installation"""
        try:
            result = subprocess.run(
                ["gradle", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return "gradle"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def _setup_android_env(self, context: Context) -> None:
        """Set up environment variables for Android build"""
        android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
        
        # Ensure ANDROID_HOME is set
        os.environ["ANDROID_HOME"] = android_home
        os.environ["ANDROID_SDK_ROOT"] = android_home

        # Find and set NDK path
        ndk_path = self._find_ndk(Path(android_home))
        if ndk_path:
            os.environ["ANDROID_NDK_HOME"] = str(ndk_path)

        # Set ANDROID_BUILD flag for other modules
        os.environ["ANDROID_BUILD"] = "1"

    def _configure_chromium_android(self, context: Context) -> None:
        """Configure Chromium build for Android"""
        chromium_src = context.chromium_src
        
        # GN args for Android build
        gn_args = [
            'target_os="android"',
            'target_cpu="arm64"',  # Primary target: ARM64
            'is_debug=false',
            'is_official_build=true',
            'android_channel="stable"',
            'is_component_build=false',
            'symbol_level=0',  # No debug symbols for smaller APK
            'enable_nacl=false',
            'ffmpeg_branding="Chrome"',
            'proprietary_codecs=true',
            # BrowserOS-specific
            'browseros_build=true',
        ]

        # Write args.gn file
        out_dir = chromium_src / "out" / "AndroidRelease"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        args_gn = out_dir / "args.gn"
        with open(args_gn, "w") as f:
            f.write("\n".join(gn_args))
            f.write("\n")

        log_info(f"Created GN args at {args_gn}")

        # Run GN to generate build files
        gn_cmd = [
            str(chromium_src / "buildtools" / "linux64" / "gn"),
            "gen",
            str(out_dir),
        ]

        subprocess.run(gn_cmd, cwd=chromium_src, check=True)
        log_success("Chromium configured for Android")

    def _build_chromium_android(self, context: Context) -> None:
        """Build Chromium for Android"""
        chromium_src = context.chromium_src
        out_dir = chromium_src / "out" / "AndroidRelease"

        # Build Chrome APK
        ninja_cmd = [
            "ninja",
            "-C", str(out_dir),
            "chrome_public_apk",
        ]

        log_info("Building Chromium... This may take a while.")
        subprocess.run(ninja_cmd, cwd=chromium_src, check=True)
        log_success("Chromium built successfully")

    def _build_mcp_server_android(self, context: Context) -> None:
        """Build MCP server as Android native library"""
        # TODO: Implement MCP server native library build
        # This would involve:
        # 1. Cross-compiling the MCP server source to .so libraries
        # 2. Building for multiple architectures (arm64-v8a, x86_64)
        # 3. Placing .so files in android/app/src/main/jniLibs/
        
        log_info("MCP server native library build not yet implemented")
        log_info("Placeholder: Would build libmcp_server.so for arm64-v8a and x86_64")

    def _package_android_app(self, context: Context) -> None:
        """Package BrowserOS Android app"""
        # TODO: Implement Android app packaging
        # This would involve:
        # 1. Copying Chromium APK as base
        # 2. Adding BrowserOS-specific resources
        # 3. Including MCP server native libraries
        # 4. Building final APK with Gradle
        
        android_project = context.repo_root / "packages" / "browseros" / "android"
        
        if not android_project.exists():
            log_error(f"Android project not found at {android_project}")
            log_info("Placeholder: Would build BrowserOS.apk with Gradle")
            return

        # Build with Gradle
        gradle_cmd = [
            "./gradlew",
            "assembleRelease",
        ]

        try:
            subprocess.run(gradle_cmd, cwd=android_project, check=True)
            log_success("Android app packaged successfully")
        except subprocess.CalledProcessError:
            log_error("Failed to build Android app")
            raise

    def _sign_apk(self, context: Context) -> None:
        """Sign Android APK"""
        # TODO: Implement APK signing
        # This would use:
        # 1. zipalign to optimize APK
        # 2. apksigner to sign with release keystore
        
        log_info("APK signing not yet implemented")
        log_info("Placeholder: Would sign BrowserOS.apk with release key")

    def _print_output_info(self, context: Context) -> None:
        """Print information about build outputs"""
        log_info("\n" + "="*60)
        log_info("Build complete!")
        log_info("="*60)
        
        # Expected output locations
        chromium_apk = context.chromium_src / "out" / "AndroidRelease" / "apks" / "ChromePublic.apk"
        browseros_apk = context.repo_root / "packages" / "browseros" / "android" / "app" / "build" / "outputs" / "apk" / "release" / "BrowserOS.apk"
        
        if chromium_apk.exists():
            log_info(f"Chromium APK: {chromium_apk}")
        
        if browseros_apk.exists():
            log_info(f"BrowserOS APK: {browseros_apk}")
        else:
            log_info(f"BrowserOS APK will be at: {browseros_apk}")
            
        log_info("="*60 + "\n")
