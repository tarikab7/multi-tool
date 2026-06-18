// Antigravity Suite SPA controller v3.0
// Handles collapsible category folders, live search box, forms submits, and SSE streaming logs.

document.addEventListener("DOMContentLoaded", () => {
    // State management
    let activeTaskId = null;
    let eventSource = null;

    // Elements
    const navItems = document.querySelectorAll(".nav-item");
    const panels = document.querySelectorAll(".tool-panel");
    const activeToolTitle = document.getElementById("active-tool-title");
    const globalJobBadge = document.getElementById("global-job-badge");
    const btnCancelTask = document.getElementById("btn-cancel-task");
    const btnClearConsole = document.getElementById("btn-clear-console");
    const consoleOutput = document.getElementById("console-output");
    const progressBar = document.getElementById("operation-progress-bar");
    const progressText = document.getElementById("operation-progress-text");
    
    // Collapsible Categories
    const categoryHeaders = document.querySelectorAll(".category-header");
    
    // Live Search
    const toolSearch = document.getElementById("tool-search");

    // Dynamic Form Elements Toggle
    setupDynamicFormToggles();

    // Initialize

    // Collapsible Category Folders Logic
    categoryHeaders.forEach(header => {
        header.addEventListener("click", () => {
            const category = header.parentElement;
            category.classList.toggle("collapsed");
        });
    });

    // Live Search Logic
    toolSearch.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();

        document.querySelectorAll(".nav-category").forEach(category => {
            let visibleItemsCount = 0;
            const itemsContainer = category.querySelector(".category-items");
            const items = itemsContainer.querySelectorAll(".nav-item");

            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const tags = (item.dataset.tags || "").toLowerCase();
                if (text.includes(query) || tags.includes(query)) {
                    item.style.display = "flex";
                    visibleItemsCount++;
                } else {
                    item.style.display = "none";
                }
            });

            // Hide the entire category folder if no items match
            if (visibleItemsCount === 0 && query !== "") {
                category.style.display = "none";
            } else {
                category.style.display = "flex";
                // If searching, ensure matching categories are expanded
                if (query !== "") {
                    category.classList.remove("collapsed");
                }
            }
        });
    });

    // Sidebar navigation switching
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            if (activeTaskId) {
                alert("A task is currently running. Please stop or wait for it to complete.");
                return;
            }
            // Clear active state
            navItems.forEach(n => n.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));

            // Set active tool
            item.classList.add("active");
            const tool = item.dataset.tool;
            const targetPanel = document.getElementById(`panel-${tool}`);
            if (targetPanel) {
                targetPanel.classList.add("active");
                activeToolTitle.innerText = item.innerText.trim();
            }
        });
    });



    // Clear Console
    btnClearConsole.addEventListener("click", () => {
        consoleOutput.innerHTML = `<div class="terminal-line system-line">[System] Console cleared. Ready.</div>`;
    });

    // Stop active task
    btnCancelTask.addEventListener("click", async () => {
        if (!activeTaskId) return;
        
        appendLog("System", "Sending cancel request...", "system-line");
        try {
            const response = await fetch(`/api/cancel/${activeTaskId}`, { method: "POST" });
            if (response.ok) {
                appendLog("System", "Cancel signal sent successfully.", "system-line");
            } else {
                appendLog("System", "Failed to cancel task on server.", "error-line");
            }
        } catch (err) {
            appendLog("System", `Error requesting cancel: ${err.message}`, "error-line");
        }
    });

    // Handle Forms Submission (Run Tools)
    const forms = document.querySelectorAll(".tool-form");
    forms.forEach(form => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (activeTaskId) {
                alert("A task is already running.");
                return;
            }

            const formId = form.id;
            


            const toolName = formId.replace("form-", "");
            const params = getFormParameters(formId);

            // Set UI running state
            setRunningState(true);
            progressBar.style.width = "0%";
            progressText.innerText = "0%";
            appendLog("System", `Starting operation: ${toolName}...`, "system-line");

            try {
                const response = await fetch(`/api/run/${toolName}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(params)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || "Server error.");
                }

                const data = await response.json();
                activeTaskId = data.task_id;
                
                // Connect to Server-Sent Events stream
                connectStream(activeTaskId);

            } catch (err) {
                appendLog("System", `Launch failed: ${err.message}`, "error-line");
                setRunningState(false);
            }
        });
    });



    // Dynamic Form Elements visibility triggers
    function setupDynamicFormToggles() {
        // Bruteforce mode toggle
        const bruteMode = document.getElementById("brute-mode");
        const bruteEndRow = document.getElementById("brute-end-row");
        if (bruteMode && bruteEndRow) {
            bruteMode.addEventListener("change", (e) => {
                if (e.target.value === "middle") {
                    bruteEndRow.style.display = "block";
                    document.getElementById("brute-end").required = true;
                } else {
                    bruteEndRow.style.display = "none";
                    document.getElementById("brute-end").required = false;
                }
            });
        }

        // GIF mode toggle
        const gifMode = document.getElementById("gif-mode");
        const gifCreationRow = document.getElementById("gif-creation-row");
        if (gifMode && gifCreationRow) {
            gifMode.addEventListener("change", (e) => {
                if (e.target.value === "create") {
                    gifCreationRow.style.display = "grid";
                } else {
                    gifCreationRow.style.display = "none";
                }
            });
        }

        // Credentials safe mode toggle
        const safeAction = document.getElementById("safe-action");
        const safeAddRow = document.getElementById("safe-add-row");
        if (safeAction && safeAddRow) {
            safeAction.addEventListener("change", (e) => {
                if (e.target.value === "add") {
                    safeAddRow.style.display = "grid";
                    document.getElementById("safe-key").required = true;
                    document.getElementById("safe-value").required = true;
                } else {
                    safeAddRow.style.display = "none";
                    document.getElementById("safe-key").required = false;
                    document.getElementById("safe-value").required = false;
                }
            });
        }

        // Hosts editor mode toggle
        const hostsAction = document.getElementById("hosts-action");
        const hostsDomainGroup = document.getElementById("hosts-domain-group");
        if (hostsAction && hostsDomainGroup) {
            hostsAction.addEventListener("change", (e) => {
                if (e.target.value === "add") {
                    hostsDomainGroup.style.display = "flex";
                    document.getElementById("hosts-domain").required = true;
                } else {
                    hostsDomainGroup.style.display = "none";
                    document.getElementById("hosts-domain").required = false;
                }
            });
        }
    }

    // Explicit Form Parameters Mapping
    function getFormParameters(formId) {
        const params = {};

        // Generic fallback using name attribute
        const form = document.getElementById(formId);
        if (form) {
            const inputs = form.querySelectorAll("input, select, textarea");
            inputs.forEach(input => {
                if (input.name) {
                    if (input.type === "checkbox") {
                        params[input.name] = input.checked;
                    } else if (input.type === "radio") {
                        if (input.checked) {
                            params[input.name] = input.value;
                        }
                    } else {
                        params[input.name] = input.value;
                    }
                }
            });
        }

        if (formId === "form-spotify_downloader") {
            params.playlist_urls = document.getElementById("spotify-urls").value;
            params.download_path = document.getElementById("spotify-dest").value;
        } 
        else if (formId === "form-mp3_tagger") {
            params.mp3_directory = document.getElementById("tagger-dir").value;
        } 
        else if (formId === "form-heic_converter") {
            params.input_folder = document.getElementById("heic-input").value;
            params.output_folder = document.getElementById("heic-output").value;
        } 
        else if (formId === "form-audio_converter") {
            params.input_path = document.getElementById("mixer-input").value;
            params.output_folder = document.getElementById("mixer-output").value;
        }
        else if (formId === "form-media_compressor") {
            params.input_path = document.getElementById("comp-input").value;
            params.target_mb = document.getElementById("comp-target").value;
            params.output_folder = document.getElementById("comp-output").value;
        }
        else if (formId === "form-gif_tool") {
            params.mode = document.getElementById("gif-mode").value;
            params.input_path = document.getElementById("gif-input").value;
            params.fps = document.getElementById("gif-fps").value;
            params.width = document.getElementById("gif-width").value;
            params.output_path = document.getElementById("gif-output").value;
        }
        else if (formId === "form-subtitles_extractor") {
            params.video_path = document.getElementById("sub-input").value;
            params.track_index = document.getElementById("sub-track").value;
            params.output_srt = document.getElementById("sub-output").value;
        }
        else if (formId === "form-image_converter") {
            params.input_folder = document.getElementById("img-dir").value;
            params.width = document.getElementById("img-width").value;
            params.target_format = document.getElementById("img-format").value;
            params.output_folder = document.getElementById("img-output").value;
        }
        else if (formId === "form-pdf_tool") {
            params.mode = document.getElementById("pdf-mode").value;
            params.input_path = document.getElementById("pdf-input").value;
            params.output_path = document.getElementById("pdf-output").value;
        }
        else if (formId === "form-thumbnail_sheet") {
            params.video_path = document.getElementById("thumb-input").value;
            params.cols = document.getElementById("thumb-cols").value;
            params.rows = document.getElementById("thumb-rows").value;
            params.output_path = document.getElementById("thumb-output").value;
        }
        else if (formId === "form-google_photos_combiner") {
            params.json_folder = document.getElementById("gphotos-json").value;
            params.media_folder = document.getElementById("gphotos-media").value;
        } 
        else if (formId === "form-date_recognizer") {
            params.directory = document.getElementById("recognizer-dir").value;
        } 
        else if (formId === "form-snapchat_processor") {
            params.file_path = document.getElementById("snap-media").value;
            params.html_path = document.getElementById("snap-html").value;
        } 
        else if (formId === "form-metadata_swapper") {
            params.directory = document.getElementById("swap-dir").value;
        }
        else if (formId === "form-duplicate_finder") {
            params.directory = document.getElementById("dup-dir").value;
            params.min_size_kb = document.getElementById("dup-min-size").value;
            params.action = document.getElementById("dup-action").value;
            params.create_backup = document.getElementById("dup-backup").checked;
        }
        else if (formId === "form-directory_organizer") {
            params.directory = document.getElementById("org-dir").value;
        }
        else if (formId === "form-bulk_renamer") {
            params.directory = document.getElementById("rename-dir").value;
            params.search_pattern = document.getElementById("rename-search").value;
            params.replace_pattern = document.getElementById("rename-replace").value;
            params.use_regex = document.getElementById("rename-regex").value;
            params.casing = document.getElementById("rename-case").value;
        }
        else if (formId === "form-secure_shredder") {
            params.target_path = document.getElementById("shred-path").value;
            params.passes = document.getElementById("shred-passes").value;
        }
        else if (formId === "form-archive_manager") {
            params.mode = document.getElementById("arc-mode").value;
            params.input_path = document.getElementById("arc-input").value;
            params.format = document.getElementById("arc-format").value;
            params.output_folder = document.getElementById("arc-output").value;
        }
        else if (formId === "form-folder_analyzer") {
            params.directory = document.getElementById("size-dir").value;
        }
        else if (formId === "form-directory_bruteforcer") {
            params.mode = document.getElementById("brute-mode").value;
            params.base_url = document.getElementById("brute-base").value;
            params.end_url = document.getElementById("brute-end").value;
            params.wordlist_file = document.getElementById("brute-wordlist").value;
        } 
        else if (formId === "form-port_scanner") {
            params.host = document.getElementById("port-host").value;
            params.range_str = document.getElementById("port-range").value;
        }
        else if (formId === "form-network_diagnostics") {
            params.host = document.getElementById("net-host").value;
            params.op_type = document.getElementById("net-type").value;
        }
        else if (formId === "form-system_monitor") {
            params.interval = document.getElementById("sys-interval").value;
        }
        else if (formId === "form-credentials_safe") {
            params.action = document.getElementById("safe-action").value;
            params.service_name = document.getElementById("safe-key").value;
            params.secret_value = document.getElementById("safe-value").value;
            params.master_key = document.getElementById("safe-master").value;
        }
        else if (formId === "form-hosts_editor") {
            params.action = document.getElementById("hosts-action").value;
            params.domain = document.getElementById("hosts-domain").value;
        }
        else if (formId === "form-speed_tester") {
            // Speed tester takes no config inputs
        }
        else if (formId === "form-combination_generator") {
            params.length = document.getElementById("combo-length").value;
            params.output_file = document.getElementById("combo-output").value;
        }
        else if (formId === "form-code_formatter") {
            params.lang = document.getElementById("fmt-lang").value;
            params.indent_size = document.getElementById("fmt-indent").value;
            params.raw_code = document.getElementById("fmt-input").value;
        }
        else if (formId === "form-data_translator") {
            params.direction = document.getElementById("trans-direction").value;
            params.delimiter = document.getElementById("trans-delimiter").value;
            params.input_path = document.getElementById("trans-input").value;
            params.output_path = document.getElementById("trans-output").value;
        }
        else if (formId === "form-encoder_decoder") {
            params.mode = document.getElementById("enc-mode").value;
            params.scheme = document.getElementById("enc-type").value;
            params.text = document.getElementById("enc-text").value;
        }
        else if (formId === "form-regex_extractor") {
            params.file_path = document.getElementById("rx-file").value;
            params.pattern = document.getElementById("rx-pattern").value;
        }
        else if (formId === "form-markdown_converter") {
            params.input_path = document.getElementById("md-input").value;
            params.output_path = document.getElementById("md-output").value;
        }
        else if (formId === "form-weather_station") {
            params.location = document.getElementById("weather-city").value;
        }
        else if (formId === "form-qr_generator") {
            params.text = document.getElementById("qr-text").value;
            params.size = document.getElementById("qr-size").value;
            params.output_path = document.getElementById("qr-output").value;
        }

        return params;
    }

    // UI State Switcher
    function setRunningState(isRunning) {
        if (isRunning) {
            globalJobBadge.style.display = "flex";
            btnCancelTask.disabled = false;
            document.querySelectorAll(".btn-run").forEach(btn => btn.disabled = true);
        } else {
            globalJobBadge.style.display = "none";
            btnCancelTask.disabled = true;
            document.querySelectorAll(".btn-run").forEach(btn => btn.disabled = false);
            activeTaskId = null;
        }
    }

    // Append output line to monospace terminal
    function appendLog(source, message, styleClass = "log-line") {
        const line = document.createElement("div");
        line.className = `terminal-line ${styleClass}`;
        
        const timestamp = new Date().toLocaleTimeString();
        line.innerText = `[${timestamp}] [${source}] ${message}`;
        
        consoleOutput.appendChild(line);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    // Connect Server-Sent Events Stream
    function connectStream(taskId) {
        eventSource = new EventSource(`/api/stream/${taskId}`);

        eventSource.addEventListener("log", (e) => {
            const data = JSON.parse(e.data);
            appendLog("Info", data.message, "log-line");
        });

        eventSource.addEventListener("progress", (e) => {
            const data = JSON.parse(e.data);
            const pct = parseFloat(data.percent).toFixed(1);
            progressBar.style.width = `${pct}%`;
            progressText.innerText = `${pct}%`;
        });

        eventSource.addEventListener("found", (e) => {
            const data = JSON.parse(e.data);
            appendLog("Found", data.message, "found-line");
        });

        eventSource.addEventListener("success", (e) => {
            const data = JSON.parse(e.data);
            appendLog("Success", data.message, "success-line");
            closeStream();
        });

        eventSource.addEventListener("error", (e) => {
            const data = JSON.parse(e.data);
            appendLog("Error", data.message, "error-line");
            closeStream();
        });

        eventSource.onerror = (err) => {
            appendLog("System", "Event stream disconnected.", "system-line");
            closeStream();
        };
    }

    function closeStream() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        setRunningState(false);
    }

    // === 1. THEME ACCENT SWITCHER ===
    const themeDots = document.querySelectorAll(".theme-dot");
    const savedTheme = localStorage.getItem("antigravity-theme") || "purple";
    
    applyTheme(savedTheme);
    
    themeDots.forEach(dot => {
        dot.addEventListener("click", () => {
            const theme = dot.dataset.theme;
            applyTheme(theme);
        });
    });
    
    function applyTheme(theme) {
        // Remove existing theme classes
        document.body.className = document.body.className.replace(/\btheme-\S+/g, "").trim();
        if (theme !== "purple") {
            document.body.classList.add(`theme-${theme}`);
        }
        
        // Update active class on dots
        themeDots.forEach(dot => {
            if (dot.dataset.theme === theme) {
                dot.classList.add("active");
            } else {
                dot.classList.remove("active");
            }
        });
        
        localStorage.setItem("antigravity-theme", theme);
    }

    const dupAction = document.getElementById("dup-action");
    if (dupAction) {
        dupAction.addEventListener("change", (e) => {
            const backupWrapper = document.getElementById("dup-backup-wrapper");
            if (e.target.value === "delete") {
                backupWrapper.style.display = "flex";
            } else {
                backupWrapper.style.display = "none";
            }
        });
    }

    // === 2. FAVORITES PINNING SYSTEM ===
    const favoritesItemsContainer = document.getElementById("favorites-items");
    const catFavorites = document.getElementById("cat-favorites");
    
    // Load favorites from localStorage
    let favorites = JSON.parse(localStorage.getItem("antigravity-favorites") || "[]");
    
    // Append star buttons to nav-items and initialize favorites
    setupFavorites();
    
    function setupFavorites() {
        // Target all sidebar buttons that represent tools
        document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
            const tool = item.dataset.tool;
            if (!tool) return; // skip items without tool attribute
            
            // Check if star button already exists to avoid duplicates
            if (item.querySelector(".btn-pin-favorite")) return;
            
            const star = document.createElement("button");
            star.type = "button";
            star.className = "btn-pin-favorite";
            star.innerHTML = favorites.includes(tool) ? "★" : "☆";
            star.title = "Pin to Favorites";
            if (favorites.includes(tool)) star.classList.add("pinned");
            
            item.appendChild(star);
            
            star.addEventListener("click", (e) => {
                e.stopPropagation(); // Don't trigger the nav-item click
                toggleFavorite(tool, star);
            });
        });
        
        renderFavorites();
    }
    
    function toggleFavorite(tool, starBtn) {
        const index = favorites.indexOf(tool);
        if (index > -1) {
            favorites.splice(index, 1);
            starBtn.innerHTML = "☆";
            starBtn.classList.remove("pinned");
            appendLog("System", `Unpinned from Favorites: ${tool}`, "system-line");
        } else {
            favorites.push(tool);
            starBtn.innerHTML = "★";
            starBtn.classList.add("pinned");
            appendLog("System", `Pinned to Favorites: ${tool}`, "system-line");
        }
        localStorage.setItem("antigravity-favorites", JSON.stringify(favorites));
        
        // Sync star state in all places
        document.querySelectorAll(`.nav-item[data-tool="${tool}"] .btn-pin-favorite`).forEach(btn => {
            if (favorites.includes(tool)) {
                btn.innerHTML = "★";
                btn.classList.add("pinned");
            } else {
                btn.innerHTML = "☆";
                btn.classList.remove("pinned");
            }
        });
        
        renderFavorites();
    }
    
    function renderFavorites() {
        favoritesItemsContainer.innerHTML = "";
        
        if (favorites.length === 0) {
            catFavorites.style.display = "none";
            return;
        }
        
        catFavorites.style.display = "flex";
        
        favorites.forEach(tool => {
            // Find the original nav item
            const originalItem = document.querySelector(`.sidebar-nav .nav-category:not(#cat-favorites) .nav-item[data-tool="${tool}"]`);
            if (!originalItem) return;
            
            // Clone the item
            const clone = originalItem.cloneNode(true);
            // Remove active state from clone initially
            clone.classList.remove("active");
            
            // Add click listener to the clone to trigger the original click
            clone.addEventListener("click", (e) => {
                // If clicking the star on the clone
                if (e.target.classList.contains("btn-pin-favorite")) {
                    e.stopPropagation();
                    toggleFavorite(tool, e.target);
                    return;
                }
                originalItem.click();
                
                // Highlight the clone as active
                document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
                clone.classList.add("active");
            });
            
            favoritesItemsContainer.appendChild(clone);
        });
    }

    // === 3. TERMINAL LOGS DOWNLOAD & FULLSCREEN ===
    const btnDownloadLogs = document.getElementById("btn-download-logs");
    const btnFullscreenConsole = document.getElementById("btn-fullscreen-console");
    const monitorContainer = document.querySelector(".monitor-container");
    
    if (btnDownloadLogs) {
        btnDownloadLogs.addEventListener("click", () => {
            const logsText = consoleOutput.innerText;
            const blob = new Blob([logsText], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `antigravity_execution_logs_${new Date().toISOString().slice(0,19).replace(/[:T]/g,"-")}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
    
    if (btnFullscreenConsole) {
        btnFullscreenConsole.addEventListener("click", () => {
            monitorContainer.classList.toggle("fullscreen-active");
            btnFullscreenConsole.innerHTML = monitorContainer.classList.contains("fullscreen-active") ? "🖥️ Exit Full" : "🖥️ Fullscreen";
        });
    }

    // === 4. DYNAMIC INTERACTIVE PATH BROWSER MODAL ===
    const modalBrowser = document.getElementById("file-browser-modal");
    const btnCloseBrowser = document.getElementById("btn-close-browser");
    const btnBrowserUp = document.getElementById("btn-browser-up");
    const btnBrowserSelect = document.getElementById("btn-browser-select");
    const browserCurrentPath = document.getElementById("browser-current-path");
    const browserItemsList = document.getElementById("browser-items");
    
    let activeBrowserTargetInput = null;
    let selectedItemPath = null;
    let currentBrowserDirectory = "";
    
    // Inject folder browse icons dynamically next to folder/path inputs
    setupPathInputs();
    
    function setupPathInputs() {
        const pathInputs = document.querySelectorAll(
            'input[type="text"][placeholder*="dir"], ' +
            'input[type="text"][placeholder*="path"], ' +
            'input[type="text"][placeholder*="Folder"], ' +
            'input[type="text"][id*="dir"], ' +
            'input[type="text"][id*="path"], ' +
            'input[type="text"][id*="dest"], ' +
            'input[type="text"][id*="directory"]'
        );
        
        pathInputs.forEach(input => {
            if (input.parentNode.classList.contains("path-input-wrapper")) return;
            
            const wrapper = document.createElement("div");
            wrapper.className = "path-input-wrapper";
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            
            const browseBtn = document.createElement("button");
            browseBtn.type = "button";
            browseBtn.className = "btn-browse-folder";
            browseBtn.innerHTML = "📁";
            browseBtn.title = "Browse file/folder";
            wrapper.appendChild(browseBtn);
            
            browseBtn.addEventListener("click", () => {
                openPathBrowser(input);
            });
        });
    }
    
    function openPathBrowser(targetInput) {
        activeBrowserTargetInput = targetInput;
        modalBrowser.classList.add("show");
        
        let startPath = targetInput.value.trim();
        loadBrowserDirectory(startPath);
    }
    
    async function loadBrowserDirectory(path) {
        browserItemsList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">Loading folder contents...</div>`;
        selectedItemPath = null;
        
        try {
            const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
            if (!response.ok) {
                if (path !== "") {
                    loadBrowserDirectory("");
                    return;
                }
                throw new Error("Unable to read directory");
            }
            
            const data = await response.json();
            currentBrowserDirectory = data.current_path;
            browserCurrentPath.value = currentBrowserDirectory;
            selectedItemPath = currentBrowserDirectory;
            
            browserItemsList.innerHTML = "";
            
            if (data.items.length === 0) {
                browserItemsList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">Folder is empty</div>`;
                return;
            }
            
            data.items.forEach(item => {
                const itemDiv = document.createElement("div");
                itemDiv.className = `browser-item ${item.is_dir ? "is-dir" : ""}`;
                itemDiv.innerHTML = `${item.is_dir ? "📁" : "📄"} <span>${item.name}</span>`;
                
                itemDiv.addEventListener("click", () => {
                    document.querySelectorAll(".browser-item").forEach(el => el.classList.remove("selected"));
                    itemDiv.classList.add("selected");
                    selectedItemPath = item.path;
                });
                
                if (item.is_dir) {
                    itemDiv.addEventListener("dblclick", () => {
                        loadBrowserDirectory(item.path);
                    });
                }
                
                browserItemsList.appendChild(itemDiv);
            });
            
        } catch (err) {
            browserItemsList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--color-red);">Error: ${err.message}</div>`;
        }
    }
    
    if (btnCloseBrowser) {
        btnCloseBrowser.addEventListener("click", () => {
            modalBrowser.classList.remove("show");
        });
    }
    
    window.addEventListener("click", (e) => {
        if (e.target === modalBrowser) {
            modalBrowser.classList.remove("show");
        }
    });
    
    if (btnBrowserUp) {
        btnBrowserUp.addEventListener("click", () => {
            if (currentBrowserDirectory) {
                const parts = currentBrowserDirectory.split("/");
                parts.pop();
                const parentPath = parts.join("/") || "/";
                loadBrowserDirectory(parentPath);
            }
        });
    }
    
    if (btnBrowserSelect) {
        btnBrowserSelect.addEventListener("click", () => {
            if (activeBrowserTargetInput && selectedItemPath) {
                activeBrowserTargetInput.value = selectedItemPath;
                activeBrowserTargetInput.dispatchEvent(new Event("change"));
                modalBrowser.classList.remove("show");
            }
        });
    }
});
