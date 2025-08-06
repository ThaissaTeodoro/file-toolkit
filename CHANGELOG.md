# Changelog - file_toolkit

All significant changes to this project will be documented in this file.

The format follows the guidelines from [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [v0.1.0] - 2025-08-06
### 🚀 Initial Release

**Added**

- Core utilities for file and directory operations (`file_ops`):
  - Copy, Move, Delete, Rename
  - Backup with timestamp
  - Read/Write JSON, Text, and Binary files with logging
  - Robust error handling with logging integration

- Compression module (`zip_ops`):
  - ZIP file compression and extraction
  - Security validations (path traversal protection)
  - Progress tracking during operations

- File hashing and duplicate detection (`hash_ops`):
  - Generate file hashes (`md5`, `sha1`, `sha256`, etc.)
  - Find duplicates based on file contents

- Search utilities (`search_ops`):
  - List directory contents recursively
  - Search files by name, prefix, modification time, and content
  - Detailed metadata retrieval (size, permissions, timestamps)

- Synchronization module (`sync_ops`):
  - Directory synchronization (copy, update, delete, ignore patterns)
  - Detailed operation statistics and logging
  - Support for progress tracking during sync operations

- Monitoring utilities (`monitor_ops`):
  - File change monitoring with callbacks
  - Customizable check intervals and maximum monitoring time

- Temporary file management (`temp_file_utils`):
  - Creation of temporary files and directories with optional content

- Progress tracking (`progress`):
  - Percentage-based progress logging for large file operations

- Disk usage and statistics module (`stats_ops`):
  - Disk space check
  - Retrieve largest files in directories
  - Directory size calculations
  - Identify empty directories

### 🛠 Improvements
- Structured logging across all modules to enhance auditability
- Comprehensive error handling across all file operations

### ✅ Testing & Coverage
- Initial test suite covering main functionalities
- Automated tests with pytest and coverage integration

### 📖 Documentation
- Complete README documentation including installation, usage examples, best practices, and contribution guidelines
"""
