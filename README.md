# 🌌 Multi-tool

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![HTML5](https://img.shields.io/badge/UI-Vanilla%20JS%20%26%20CSS-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](#)

Welcome to **Multi-tool**—a premium, all-in-one developer and system utility application. Featuring a gorgeous glassmorphic **Obsidian Dark** user interface and a local **FastAPI** backend, the suite provides **85 advanced, fully-functioning tools** that run entirely keylessly and offline wherever possible.

---

## ✨ Features

- **85 Advanced Tools**: Multi-threaded, async operations covering audio, video, networking, file cleanups, and data translations.
- **Obsidian-Glassmorphic UI**: Sleek, transparent containers, responsive layouts, active indicator glows, and smooth animations.
- **🎨 Accent Theme Customizer**: Instantly swap accent colors (Purple, Cyan, Green, Pink) with automatic state preservation in `localStorage`.
- **⭐ Favorites Pinning**: Star your most-used tools to access them in a dedicated quick-access folder at the top of the sidebar.
- **📁 Glassmorphic Folder Browser**: Click `📁` next to any file/folder input to visually navigate and select local paths instantly.
- **📺 Fullscreen Console Terminal**: View live streaming stdout/stderr logs from background tasks, toggle fullscreen mode, and **Download Logs** as `.txt` files.
- **🔑 Keyless Out-Of-The-Box**: No API keys required. All integrations (Spotify, YouTube, iTunes, RDAP, etc.) utilize keyless web scrapers or offline standard library math/subprocesses.

---

## 🛠️ Tool Catalog (85 Tools)

The tools are organized into 7 distinct categories in the sidebar:

### 1. 🎵 Audio & Music Tools (7 Tools)
- **Spotify Downloader**: Extract tracklists keylessly from playlists and download matching high-quality MP3s via yt-dlp.
- **MP3 Tagger**: Identify and write ID3 metadata (Title, Artist, Album, Genre) and embed 600x600 cover art keylessly.
- **Audio Trimmer**: Trim MP3/WAV audio files using exact start/end timestamps via FFmpeg.
- **BPM & Key Detector**: Estimates tempo (BPM) and musical key signature from raw audio samples.
- **ID3 Metadata Cleaner**: Strips all ID3 metadata, tag frames, and cover art from MP3 files for privacy.
- **Stereo Downmixer**: Downmixes multi-channel/surround audio tracks into normalized mono/stereo files.
- **Text-to-Speech (TTS)**: Converts text blocks to spoken voice MP3s using Google's keyless TTS stream.

### 2. 🖼️ Video & Image Tools (14 Tools)
- **Video Stabilizer**: Stabilizes shaky videos using FFmpeg's two-pass `vid.stab` filters.
- **Image Background Remover**: Strips image backgrounds to create transparent PNGs.
- **Video to Audio**: Extracts raw audio streams from video containers (MP4, MKV) to MP3/WAV.
- **GIF to MP4**: Converts animated GIFs to space-efficient MP4 videos.
- **HEIC Converter**: Bulk converts iPhone HEIC photos to JPEG/PNG while preserving EXIF capture dates.
- **Video/Audio Compressor**: Shrinks large media files using H.264/AAC to fit email or Discord upload limits.
- **GIF Maker/Extractor**: Loops videos into GIFs or extracts individual frames as image series.
- **Subtitles Tool**: Extracts embedded subtitle tracks (SRT, VTT) from MKV/MP4 files.
- **Image Bulk Tool**: Resizes, formats (PNG, JPG, WEBP, BMP), watermarks, and crops images in bulk.
- **Video Thumbnailer**: Generates high-res image index thumbnail sheets for videos.
- **PDF Page Extractor**: Exports PDF pages as individual high-res PNG/JPG images.
- **Color Palette Extractor**: Uses k-means clustering to detect dominant hex codes in an image.
- **Image EXIF Viewer**: Displays camera settings, focal lengths, lenses, and GPS capture locations.
- **Video Rotator/Flipper**: Rotates videos 90/180/270 degrees or flips them vertically/horizontally.

### 3. 📁 File Operations (13 Tools)
- **Duplicate Finder**: Scans directories for identical files (via MD5 hashing) and deletes duplicates.
- **Secure Shredder**: Securely wipes files using multi-pass zero-filling to prevent recovery.
- **Bulk File Renamer**: Batch renames files using regex searches, string replacements, and casings.
- **Archive Manager**: Compresses or extracts ZIP, TAR, RAR, and GZ archives.
- **Folder Size Analyzer**: Analyzes disk usage space and draws interactive directory size trees.
- **File Hash Generator**: Computes MD5, SHA-1, SHA-256, and SHA-512 hashes.
- **AES File Cryptographer**: Encrypts and decrypts files using secure AES-256-CBC.
- **Directory Tree Generator**: Renders printable ASCII/Markdown folder trees of any path.
- **Broken Symlinks Cleaner**: Scans for and prunes broken/dangling symbolic links.
- **Empty Folders Cleaner**: Recursively sweeps and deletes empty directories.
- **File Splitter & Joiner**: Splits files into customized chunk sizes and re-assembles them.
- **Server Log Analyzer**: Parses Nginx/Apache logs to extract codes (2xx, 4xx, 5xx) and traffic spikes.
- **Temp Cache Cleaner**: Safely deletes temporary OS files, log piles, and app caches.

### 4. ☁️ Cloud & Backup (10 Tools)
- **Google Photos Combiner**: Merges Google Photos JSON metadata back into image files to restore timestamps.
- **Date Recognizer**: Re-organizes files into structured date folders based on EXIF metadata.
- **Snapchat Processor**: Parses exported Snapchat memory packages and compiles backup indexes.
- **Metadata Swapper**: Swaps or strips EXIF metadata blocks to anonymize files.
- **Extension Organizer**: Auto-sorts files in a directory into folders based on file extensions.
- **S3 Public Bucket Downloader**: Downloads public Amazon S3 buckets recursively keylessly.
- **Web Scraper**: Extracts headings, paragraphs, and anchor links from any HTML page.
- **GitHub Repository Backuper**: Backs up git repository main branches as ZIP files keylessly.
- **RSS Feed Reader**: Reads syndication XML feeds to display articles and links.
- **GDrive Direct Link Converter**: Converts sharing URLs into direct API download endpoints.

### 5. 🌐 Network & Web Tools (15 Tools)
- **Dir Bruteforcer**: Scans web application routes for hidden pages using custom wordlists.
- **Local Port Scanner**: Scans local or remote hosts to check for open/active TCP ports.
- **Network Diagnostics**: Standard Ping, Traceroute, GeoIP, and DNS lookups.
- **Network Speed Tester**: Measures download, upload, and ping latencies.
- **Weather Station**: Pulls live city weather metrics keylessly from OpenMeteo.
- **QR Code Generator**: Encodes text or URLs into printable QR Codes.
- **DNS Propagation Checker**: Checks DNS resolution state across global public DNS resolvers.
- **WHOIS Lookup**: Queries domain name registration dates, servers, and registrars keylessly.
- **HTTP Header Inspector**: Examines server response headers, cookies, and redirect hops.
- **SSL Expiry Checker**: Warns about TLS certificate expiration dates and domain mismatches.
- **Subnet Calculator**: Calculates network subnet masks, broadcasts, and IP ranges.
- **MAC Vendor Lookup**: Resolves hardware manufacturers from MAC addresses keylessly.
- **User-Agent Parser**: Decodes browser User-Agent strings into OS and device details.
- **URL Shortener & Expander**: Shortens links via TinyURL or expands redirect trails.
- **Local Subnet Ping Sweeper**: Performs fast ICMP pings to list active IP addresses in a local subnet.

### 6. ⚙️ System Utilities (9 Tools)
- **Resource Monitor**: Displays real-time CPU, RAM, and Disk storage usage graphs.
- **Credentials Safe**: Cryptographic password manager vault secured with a Master Key.
- **Hosts File Editor**: Edits local hosts DNS mappings to block or redirect web routing.
- **CPU Stress Tester**: Runs safe parallel mathematical workloads to test thermals.
- **Disk Benchmark Speed**: Benchmarks disk write/read throughput in MB/s.
- **Nearby Wi-Fi Scanner**: Lists reachable wireless networks, signal decibels, and security.
- **Process Manager & Killer**: Lists active system processes and kills tasks using PIDs.
- **Cron Schedule Explainer**: Translates standard cron syntax into plain English.
- **Bulk UUID Generator**: Generates bulk UUID v1 or v4 unique string tokens.

### 7. 💻 Code & Data Tools (17 Tools)
- **Letter Generator**: Computes combinations and permutations for passwords or tests.
- **Code Formatter**: Beautifies Python, JS, HTML, and CSS code blocks.
- **CSV ↔ JSON Translator**: Converts tabular CSV data into structured JSON objects.
- **base64/URL Tool**: Encodes and decodes base64, URL, and hex strings.
- **Regex Extractor**: Tests regex expressions against files to output matching groups.
- **Markdown Converter**: Translates and previews Markdown strings as styled HTML.
- **PDF Document Tool**: Merges and splits PDF pages.
- **JSON Formatter/Minifier**: Validates and formats JSON strings with error highlights.
- **SQL Query Formatter**: Formats SQL queries with uppercase keywords and clean indents.
- **XML ➔ JSON Converter**: Translates XML tags into JSON objects.
- **Diff Side-By-Side Checker**: Compares text blocks and highlights changes.
- **Word & Text Counter**: Counts words, syllables, lines, and estimates reading times.
- **IP Address Validator**: Validates IPv4/IPv6 address ranges and CIDR blocks.
- **Markdown To PDF Compiler**: Compiles Markdown documentation into clean styled PDFs.
- **Password Strength Evaluator**: Computes bit entropy and brute-force crack estimates.
- **JWT Token Decoder**: Decodes JWT headers and payload claims keylessly.
- **Lorem Ipsum Generator**: Outputs designer dummy placeholder text paragraphs.

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.10+ and `ffmpeg` installed on your system:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-venv python3-pip ffmpeg
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tarikab7/multitool.git
   cd multitool
   ```

2. Set up virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Launch the suite:
   ```bash
   python3 main.py
   ```

4. Open your browser and navigate to:
   👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Obsidian Cyber-Glow theme), Vanilla JS.
- **Backend**: FastAPI, Uvicorn, Python standard libraries.
- **Core Integrations**: FFmpeg (Subprocesses), Pillow (Image manipulation), BeautifulSoup4 (Web parsing).

---

## 🔒 Security

No data ever leaves your machine. The FastAPI backend runs entirely locally, and all file operations, encryption, shredding, and database credentials safes are isolated on your local hard disk.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
