# Unicorn Commander - NPU Voice Assistant Pro
## Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-07-03

### 🎉 Major Fixes - Production Ready

#### Fixed
- **CRITICAL**: Fixed XRT environment setup failure that was causing NPU systems to fall back to demo mode
- **CRITICAL**: Fixed GUI backend integration - AdvancedNPUBackend now properly operational
- **CRITICAL**: Fixed `_get_backend_model_name` method scope issue causing initialization errors
- **UI**: Updated tray app to use unicorn-aware.png icon instead of generic placeholder
- **INSTALL**: Fixed installation script paths and desktop integration

#### Added
- **NPU**: Improved XRT environment variable parsing and setup (11 variables now properly configured)
- **NPU**: Added `_start_advanced_always_listening()` method for AdvancedNPUBackend integration
- **NPU**: Enhanced error handling and logging for XRT environment issues
- **INSTALL**: Comprehensive installation script with dependency management and verification
- **INSTALL**: Desktop integration with custom icon and autostart support
- **INSTALL**: Uninstall script for clean removal
- **DOCS**: Updated NPU development documentation with recent fixes and solutions

#### Changed
- **NPU**: XRT environment setup now uses `bash -c` for proper environment sourcing
- **NPU**: GUI start/stop methods now properly handle both AdvancedNPUBackend and legacy AlwaysListeningNPU
- **UI**: Tray app now uses PySide6 for consistency with main GUI
- **UI**: Desktop entry includes proper icon path and application categories

#### Technical Details
- **NPU Detection**: ✅ AMD Phoenix NPU with firmware 1.5.5.391 fully operational
- **XRT Integration**: ✅ 11 environment variables properly configured
- **Backend Status**: ✅ AdvancedNPUBackend with real NPU acceleration
- **Demo Mode**: ❌ No longer falls back to demo mode in production

---

## [2.0.0] - 2025-06-30

### 🚀 Major Release - NPU Always-Listening System

#### Added
- **NPU**: Complete AMD Phoenix NPU integration with XRT runtime
- **NPU**: AdvancedNPUBackend for high-performance speech processing
- **NPU**: Custom NPU kernels for matrix multiplication and attention mechanisms
- **AUDIO**: Real-time voice activity detection with Silero VAD + NPU
- **AUDIO**: Wake word detection with OpenWakeWord + NPU integration
- **SPEECH**: ONNX Whisper integration with NPU acceleration
- **GUI**: Qt6/PySide6 interface with comprehensive NPU controls
- **GUI**: System diagnostics and performance monitoring
- **GUI**: Topical filtering and conversation analysis
- **INSTALL**: Desktop integration and launcher scripts

#### Performance
- **10-45x real-time processing** speed with NPU acceleration
- **Sub-50ms VAD latency** for responsive voice detection
- **Concurrent processing** of VAD, Wake Word, and Whisper on NPU
- **Memory efficient** with optimized model caching

---

## [1.x.x] - Earlier Versions

### Legacy Development
- Initial NPU exploration and proof-of-concept implementations
- Basic Whisper integration without NPU acceleration
- Command-line interfaces and basic GUI prototypes

---

## 🔮 Upcoming Features

### [2.2.0] - Planned
- **NPU**: XRT-SMI turbo mode configuration for maximum performance
- **NPU**: Vulkan compute integration for iGPU hybrid execution
- **AI**: OGA (ONNX Generator API) integration for text generation
- **PERF**: Thermal-aware NPU optimization

### [3.0.0] - Future Vision
- **AI**: Complete Ryzen AI v1.4 feature parity
- **NPU**: Advanced hybrid scheduling (NPU+iGPU+CPU)
- **AI**: Multi-modal processing (speech + vision + text)
- **CLOUD**: Optional cloud integration for advanced AI features

---

## Technical Notes

### System Requirements
- **NPU**: AMD Ryzen AI Phoenix/Hawk Point/Strix
- **OS**: Ubuntu 25.04+ (Linux kernel 6.14+)
- **Memory**: 16GB+ RAM recommended
- **Storage**: 20GB+ free space for models and cache

### Dependencies Resolved
- **XRT Runtime**: Properly configured with 11 environment variables
- **MLIR-AIE**: Iron framework for low-level NPU programming
- **Python**: PySide6, PyTorch, ONNX Runtime, Transformers
- **Audio**: Librosa, SoundDevice, WebRTC VAD

### Performance Benchmarks
- **Real-time Factor**: 0.010x - 0.045x (10-45x faster than real-time)
- **Processing Time**: ~0.25-0.30s regardless of audio length
- **NPU Utilization**: Active on all 6 Phoenix NPU accelerator instances
- **Reliability**: 100% success rate across test scenarios