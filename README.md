# 🗂️ Task Tracker

A modern, dark-themed desktop task tracker with recursive folder/tracker hierarchy, live progress stats, and auto-saving. Built with Python and PySide6.

---

## ✨ Features

### 🗂️ Hierarchical Workspaces
- **Folders** can contain other folders or trackers — unlimited nesting depth
- **Drag-and-drop** to move trackers between folders directly in the sidebar
- **Reorder** items with ↑ / ↓ via right-click context menu
- **Rename / Delete** any node via right-click

### 📋 Tracker Details
- **Inline name editing** — click to edit, auto-saves on focus-out
- **Start & Target dates** with 🗓️ calendar popup picker
- **Total tasks** spinbox + **± buttons** for completed count
- **Notes field** — freeform text, auto-saved 700ms after typing stops
- All fields **auto-save continuously** — no save button needed

### 📊 Live Stats (per tracker)
- **Time Remaining / Elapsed** — live time progress bar
- **Tasks / Day Needed** — exact rate to hit the deadline
- **Est. Completion** — velocity-based ETA (`tasks done ÷ elapsed days × remaining`)

### 📁 Folder Aggregation
Folders recursively aggregate all descendants:
| Stat | Logic |
|---|---|
| **Total Tasks** | Sum of all tasks in all descendant trackers |
| **Completed** | Sum of all done tasks |
| **Trackers** | Count of all leaf trackers |
| **Nearest Deadline** | `min(end_dt)` across all descendants |
| **Status Badge** | Driven by nearest deadline + aggregate progress |

### 🎯 Focus Board (per folder)
Every folder page shows a **⚠️ Needs Attention** section at the bottom — a contextual board showing all overdue and at-risk trackers within that folder's scope. At "All Projects" root, this becomes a **global priority board**.

### Status Badges
| Badge | Meaning |
|---|---|
| ✅ Done | All tasks completed |
| 🟢 On Track | On pace to meet the deadline |
| 🟡 At Risk | Time elapsed > % tasks done |
| ⬜ Not Started | No tasks completed yet (and not overdue) |
| 🔴 Overdue | Deadline has passed |
| — No Data | No tasks or dates set |

### 🔍 Sidebar Features
- **Live search** — filters the tree by name as you type, auto-expands parent folders
- **Adjustable width** — drag the splitter handle to resize
- **Status icons** next to each item
- **Quick-add** buttons (📁+ 📋+) for root-level creation

### ⚙️ Sorting
A global sort selector appears in every folder header:
- Default Order (insertion)
- Name A→Z
- Deadline ↑ (earliest first)
- Status (overdue → at risk → not started → on track → done)
- Progress ↑ (least complete first)

Sort is applied consistently at every folder level.

---

## 🔧 Requirements

- **Python** 3.9+
- **PySide6** 6.x

Install the dependency:

```bash
pip install PySide6
# or, if using uv:
uv pip install PySide6
```

---

## 🚀 Running the App

### Linux
```bash
chmod +x Task_Tracker.py
./Task_Tracker.py
# or:
python3 Task_Tracker.py
```
> The app automatically forces **XWayland** on Linux to enable proper splitter resizing.

### macOS
```bash
python3 Task_Tracker.py
```
> To make it double-clickable: use **Automator** → *Run Shell Script* → `python3 /path/to/Task_Tracker.py`

### Windows
```bash
python Task_Tracker.py
```
> **Tip:** Rename to `Task_Tracker.pyw` to launch without a console window.

---

## 💾 Data Storage

All data is saved automatically to:
```
task_tracker_v2_data.json
```
in the same directory as the script. The file is plain JSON — human-readable and easy to back up. No database, no cloud dependency.

---

## 🖱️ Usage Guide

### Creating structure
- **Right-click** any sidebar item → Add Tracker Here / Add Folder Here
- Use the **📁+ / 📋+** buttons in the sidebar header to add at the root level

### Editing a tracker
1. Click any tracker in the sidebar or on a folder's Contents card
2. Edit the name directly in the header
3. Set **Start** and **Target** dates — type `YYYY-MM-DD` or use the **🗓️** calendar button
4. Set **Total Tasks**, then use **+** / **−** to increment completed count
5. Everything saves automatically

### Moving trackers
- **Drag** a tracker from the sidebar and **drop it onto a folder** to move it inside
- Drop between/above items to place it at the same level as the target
- Use **right-click → Move Up / Move Down** for fine ordering

### Search
Type in the **🔍 Search** bar at the top of the sidebar to filter trackers by name. Clear with the × button to restore the full tree.

### Sort
Open any folder/root view — use the **Default Order** dropdown in the top-right of the content area to switch sort mode globally.

---

## 📐 Architecture

```
Task_Tracker.py          # Single-file application
task_tracker_v2_data.json  # Auto-generated data file
```

**Internal structure (data model):**
```
root (folder)
 ├─ Folder A
 │   ├─ Tracker 1   { id, name, start, end, total, done, notes }
 │   └─ Tracker 2
 └─ Folder B
     └─ Sub-Folder
         └─ Tracker 3
```

**Key classes:**
| Class | Role |
|---|---|
| `DataManager` | Loads/saves JSON, manages node map, handles moves/reorders |
| `FolderPage` | Renders folder aggregate view + contents grid + attention board |
| `TrackerPage` | Renders tracker detail — dates, tasks, live stats, notes |
| `Sidebar` | Tree navigation with search, drag-drop, context menus |
| `WorkspaceTree` | `QTreeWidget` subclass handling custom drag-drop events |

---

## 🎨 Design

- **Dark** theme (`#0a0a18` base, surface layers, accent purple `#7c6ff7`)
- **Inter / Segoe UI** font family
- Gradient progress bars color-coded by status
- Smooth hover states throughout

---

*No external dependencies beyond PySide6. No telemetry. No internet required.*
