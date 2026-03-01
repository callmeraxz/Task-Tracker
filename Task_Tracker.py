#!/usr/bin/env python3
"""Task Tracker — Recursive workspace & task management."""

import json
import os
import platform
import sys
import uuid
from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCalendarWidget,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ── Constants ──────────────────────────────────────────────────────────────────
SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "task_tracker_data.json"
)
DT_FMT, D_FMT, UPD_MS = "%Y-%m-%d %H:%M", "%Y-%m-%d", 60_000

# ── Palette ────────────────────────────────────────────────────────────────────
BG, PANEL, SURFACE, BORDER = "#0a0a18", "#0f0f1e", "#161628", "#222244"
ACCENT, ALIGHT = "#7c6ff7", "#a09cf9"
SUCCESS, WARN, DANGER = "#4ade80", "#fbbf24", "#f87171"
TEXT, MUTED, SEL = "#e2e8f0", "#64748b", "#1a1a3e"

STATUS_INFO = {
    "done": ("✅ Done", SUCCESS),
    "on_track": ("🟢 On Track", SUCCESS),
    "at_risk": ("🟡 At Risk", WARN),
    "not_started": ("⬜ Not Started", MUTED),
    "overdue": ("🔴 Overdue", DANGER),
    "no_data": ("—  No Data", MUTED),
}

# ── Stylesheet ─────────────────────────────────────────────────────────────────
QSS = f"""
* {{ font-family: 'Segoe UI', 'Inter', Arial, sans-serif; font-size: 13px; }}
QMainWindow, QWidget {{ background-color: {BG}; color: {TEXT}; }}
QSplitter::handle {{ background: {BORDER}; width: 1px; height: 1px; }}
QTreeWidget {{
    background: {PANEL}; border: none; outline: 0; padding: 4px;
    show-decoration-selected: 1;
}}
QTreeWidget::item {{ height: 34px; padding-left: 4px; border-radius: 6px; }}
QTreeWidget::item:selected {{ background: {SEL}; color: {ALIGHT}; }}
QTreeWidget::item:hover:!selected {{ background: rgba(124,111,247,0.07); }}
QScrollBar:vertical {{ background: {PANEL}; width: 5px; border: none; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 2px; min-height: 16px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: {PANEL}; height: 5px; border: none; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 2px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QPushButton {{
    background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER};
    border-radius: 7px; padding: 7px 16px;
}}
QPushButton:hover {{ background: {BORDER}; border-color: {ACCENT}; color: {ALIGHT}; }}
QPushButton:pressed {{ background: {SEL}; }}
QPushButton[role="accent"] {{ background: {ACCENT}; color: #fff; border: none; font-weight: bold; }}
QPushButton[role="accent"]:hover {{ background: {ALIGHT}; }}
QPushButton[role="danger"] {{
    background: transparent; color: {DANGER};
    border: 1px solid rgba(248,113,113,.4);
}}
QPushButton[role="danger"]:hover {{ background: rgba(248,113,113,.1); }}
QPushButton[role="muted"] {{
    background: transparent; color: {MUTED};
    border: 1px solid {BORDER}; font-size: 12px; padding: 5px 10px;
}}
QPushButton[role="muted"]:hover {{ color: {TEXT}; border-color: {ACCENT}; }}
QLineEdit, QSpinBox {{
    background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER};
    border-radius: 7px; padding: 7px 10px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QSpinBox:focus {{ border-color: {ACCENT}; background: {SEL}; }}
QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: none; background: none; }}
QProgressBar {{
    background: {SURFACE}; border: none; border-radius: 6px;
    max-height: 14px; min-height: 14px; font-size: 0px;
}}
QProgressBar::chunk {{
    border-radius: 6px;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {ACCENT}, stop:1 {ALIGHT});
}}
QProgressBar[status="done"]::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #16a34a, stop:1 {SUCCESS});
}}
QProgressBar[status="overdue"]::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #dc2626, stop:1 {DANGER});
}}
QProgressBar[status="at_risk"]::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #b45309, stop:1 {WARN});
}}
QMenu {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 4px 0;
}}
QMenu::item {{ padding: 7px 20px; margin: 1px 4px; border-radius: 4px; }}
QMenu::item:selected {{ background: {SEL}; color: {ALIGHT}; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 3px 10px; }}
QDialog {{ background: {PANEL}; }}
QMessageBox {{ background: {PANEL}; }}
QFormLayout QLabel {{ color: {MUTED}; font-size: 12px; background: transparent; }}
QTextEdit {{
    background: {BG}; color: {TEXT}; border: none;
    border-radius: 4px; padding: 6px; selection-background-color: {ACCENT};
}}
QTextEdit:focus {{ border: 1px solid {BORDER}; }}
QComboBox {{
    background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 4px 10px; min-width: 130px;
}}
QComboBox:hover {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER};
    selection-background-color: {ACCENT}; selection-color: #fff; outline: 0;
}}
QCalendarWidget {{ background: {SURFACE}; color: {TEXT}; border: none; }}
QCalendarWidget QAbstractItemView {{
    background: {SURFACE}; color: {TEXT}; border: none; outline: 0;
    selection-background-color: {ACCENT}; selection-color: #fff;
}}
QCalendarWidget QAbstractItemView:disabled {{ color: {BORDER}; }}
QCalendarWidget QToolButton {{
    background: transparent; color: {TEXT};
    border: none; border-radius: 4px; padding: 4px 8px;
}}
QCalendarWidget QToolButton:hover {{ background: {BORDER}; color: {ALIGHT}; }}
QCalendarWidget QMenu {{ background: {SURFACE}; color: {TEXT}; }}
QCalendarWidget #qt_calendar_navigationbar {{
    background: {PANEL}; border-radius: 6px 6px 0 0; padding: 2px;
}}
"""


# ── Helpers ────────────────────────────────────────────────────────────────────
def uid() -> str:
    return uuid.uuid4().hex[:10]


def parse_dt(s: str) -> Optional[datetime]:
    for fmt in (DT_FMT, D_FMT):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, AttributeError):
            pass
    return None


def fmt_delta(delta: timedelta) -> str:
    past = delta.total_seconds() < 0
    secs = int(abs(delta).total_seconds())
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    parts = (
        ([f"{d}d"] if d else [])
        + ([f"{h}h"] if h else [])
        + ([f"{m}m"] if m or (not d and not h) else [])
    )
    return (" ".join(parts) or "0m") + (" ago" if past else " remaining")


def new_tracker(name: str = "New Tracker") -> dict:
    return {
        "id": uid(),
        "type": "tracker",
        "name": name,
        "start": "",
        "end": "",
        "total": 0,
        "done": 0,
    }


def new_folder(name: str = "New Folder") -> dict:
    return {
        "id": uid(),
        "type": "folder",
        "name": name,
        "start": "",
        "end": "",
        "children": [],
    }


def make_root() -> dict:
    return {"id": "root", "type": "folder", "name": "All Projects", "children": []}


# ── Aggregation & Status ───────────────────────────────────────────────────────
def aggregate(node: dict) -> dict:
    if node["type"] == "tracker":
        return {
            "total": node.get("total", 0),
            "done": node.get("done", 0),
            "count": 1,
            "start_dt": parse_dt(node.get("start", "")),
            "end_dt": parse_dt(node.get("end", "")),
        }
    total = done = count = 0
    ends = []
    for ch in node.get("children", []):
        s = aggregate(ch)
        total += s["total"]
        done += s["done"]
        count += s["count"]
        if s.get("end_dt"):
            ends.append(s["end_dt"])
    return {
        "total": total,
        "done": done,
        "count": count,
        "start_dt": None,
        "end_dt": min(ends) if ends else None,
    }


def node_status(node: dict) -> str:
    st = aggregate(node)
    total, done, end_dt = st["total"], st["done"], st.get("end_dt")
    now = datetime.now()
    if total == 0 and end_dt is None:
        return "no_data"
    if total > 0 and done >= total:
        return "done"
    if end_dt and end_dt < now:
        return "overdue"
    if total > 0 and done == 0:
        return "not_started"
    if node["type"] == "tracker":
        s, e = st.get("start_dt"), end_dt
        if s and e and total > 0:
            tspan = (e - s).total_seconds()
            if tspan > 0:
                time_pct = max(0.0, min((now - s).total_seconds() / tspan, 1.0))
                if time_pct > done / total:
                    return "at_risk"
    return "on_track"


# ── Sort & Focus helpers ───────────────────────────────────────────────────────
_SORT_MODE: str = "default"
_SORT_LABELS = ["Default Order", "Name A→Z", "Deadline ↑", "Status", "Progress ↑"]
_SORT_KEYS = ["default", "name", "deadline", "status", "progress"]
_STATUS_ORDER = {
    "overdue": 0,
    "at_risk": 1,
    "not_started": 2,
    "on_track": 3,
    "done": 4,
    "no_data": 5,
}


def sorted_children(children: list) -> list:
    if _SORT_MODE == "name":
        return sorted(children, key=lambda n: n["name"].lower())
    if _SORT_MODE == "deadline":
        return sorted(
            children, key=lambda n: aggregate(n).get("end_dt") or datetime.max
        )
    if _SORT_MODE == "status":
        return sorted(children, key=lambda n: _STATUS_ORDER.get(node_status(n), 9))
    if _SORT_MODE == "progress":

        def _pct(n):
            st = aggregate(n)
            return (st["done"] / st["total"]) if st["total"] > 0 else 0.0

        return sorted(children, key=_pct)
    return list(children)


def collect_attention_nodes(node: dict) -> list:
    """Recursively collect trackers with status overdue/at_risk/not_started."""
    result = []
    if node["type"] == "tracker":
        if node_status(node) in ("overdue", "at_risk"):
            result.append(node)
    for ch in node.get("children", []):
        result.extend(collect_attention_nodes(ch))
    return result


# ── DataManager ────────────────────────────────────────────────────────────────
class DataManager:
    def __init__(self):
        self.root: dict = make_root()
        self._map: dict = {}
        self._par: dict = {}

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE) as f:
                    data = json.load(f)
                if isinstance(data, dict) and data.get("type") == "folder":
                    self.root = data
            except Exception:
                pass
        self._rebuild_map()

    def save(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(self.root, f, indent=2)
        except Exception:
            pass

    def _rebuild_map(self):
        self._map.clear()
        self._par.clear()

        def _walk(n, p):
            self._map[n["id"]] = n
            self._par[n["id"]] = p
            for c in n.get("children", []):
                _walk(c, n)

        _walk(self.root, None)

    def get(self, nid: str) -> Optional[dict]:
        return self._map.get(nid)

    def parent_of(self, nid: str) -> Optional[dict]:
        return self._par.get(nid)

    def add_child(self, parent_id: str, child: dict):
        p = self._map.get(parent_id)
        if p and p["type"] == "folder":
            # Inherit defaults for new trackers if fields are empty
            if child["type"] == "tracker":
                s_def = p.get("start", "")
                e_def = p.get("end", "")
                if s_def and not child.get("start"):
                    child["start"] = s_def
                if e_def and not child.get("end"):
                    child["end"] = e_def

            p.setdefault("children", []).append(child)
            self._rebuild_map()
            self.save()

    def update_folder_defaults(
        self, nid: str, start: str, end: str, retro: bool = False
    ):
        n = self._map.get(nid)
        if n and n["type"] == "folder":
            n["start"] = start
            n["end"] = end
            if retro:
                for ch in n.get("children", []):
                    if ch["type"] == "tracker":
                        ch["start"] = start
                        ch["end"] = end
            self.save()

    def remove(self, nid: str):
        p = self._par.get(nid)
        if p:
            p["children"] = [c for c in p.get("children", []) if c["id"] != nid]
            self._rebuild_map()
            self.save()

    def update_tracker(self, nid: str, **kwargs):
        n = self._map.get(nid)
        if n and n["type"] == "tracker":
            n.update(kwargs)
            self.save()

    def rename(self, nid: str, new_name: str):
        n = self._map.get(nid)
        if n:
            n["name"] = new_name
            self.save()

    def reorder(self, nid: str, direction: int):
        p = self._par.get(nid)
        if not p:
            return
        ch = p["children"]
        i = next((i for i, c in enumerate(ch) if c["id"] == nid), -1)
        ni = i + direction
        if 0 <= ni < len(ch):
            ch[i], ch[ni] = ch[ni], ch[i]
            self._rebuild_map()
            self.save()

    def move_node(self, nid: str, new_parent_id: str):
        if nid == "root" or nid == new_parent_id:
            return
        if self._is_descendant(nid, new_parent_id):
            return
        node = self._map.get(nid)
        old_p = self._par.get(nid)
        new_p = self._map.get(new_parent_id)
        if not node or not old_p or not new_p or new_p["type"] != "folder":
            return
        if old_p.get("id") == new_parent_id:
            return
        old_p["children"] = [c for c in old_p.get("children", []) if c["id"] != nid]
        new_p.setdefault("children", []).append(node)
        self._rebuild_map()
        self.save()

    def _is_descendant(self, ancestor_id: str, candidate_id: str) -> bool:
        node = self._map.get(ancestor_id)
        if not node:
            return False
        for child in node.get("children", []):
            if child["id"] == candidate_id or self._is_descendant(
                child["id"], candidate_id
            ):
                return True
        return False


# ── Widget factory helpers ─────────────────────────────────────────────────────
def lbl(
    text: str, size: int = 13, bold: bool = False, color: str = TEXT, wrap: bool = False
) -> QLabel:
    w = QLabel(text)
    f = QFont()
    f.setPointSize(size)
    if bold:
        f.setBold(True)
    w.setFont(f)
    w.setStyleSheet(f"color:{color}; background:transparent;")
    if wrap:
        w.setWordWrap(True)
    return w


def hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background:{BORDER}; border:none; max-height:1px;")
    return f


def btn(text: str, role: str = "", fixed_w: int = 0) -> QPushButton:
    b = QPushButton(text)
    if role:
        b.setProperty("role", role)
    if fixed_w:
        b.setFixedWidth(fixed_w)
    return b


def make_pbar(value: int, status: str, height: int = 10) -> QProgressBar:
    pb = QProgressBar()
    pb.setRange(0, 100)
    pb.setValue(value)
    pb.setProperty("status", status)
    pb.setFixedHeight(height)
    pb.style().unpolish(pb)
    pb.style().polish(pb)
    return pb


def stat_card(label_txt: str, value_txt: str, value_color: str = TEXT) -> QFrame:
    f = QFrame()
    f.setStyleSheet(
        f"QFrame{{background:{SURFACE}; border:1px solid {BORDER}; border-radius:8px;}}"
    )
    lay = QVBoxLayout(f)
    lay.setContentsMargins(12, 8, 12, 10)
    lay.setSpacing(3)
    l = QLabel(label_txt)
    l.setStyleSheet(
        f"color:{MUTED}; font-size:10px; font-weight:600; letter-spacing:.5px; background:transparent;"
    )
    v = QLabel(value_txt)
    v.setStyleSheet(
        f"color:{value_color}; font-size:16px; font-weight:bold; background:transparent;"
    )
    v.setObjectName("stat_val")
    lay.addWidget(l)
    lay.addWidget(v)
    return f


# ── StatusBadge ────────────────────────────────────────────────────────────────
class StatusBadge(QLabel):
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)

    def set_status(self, status: str):
        text, color = STATUS_INFO.get(status, ("— No Data", MUTED))
        self.setText(f"  {text}  ")
        self.setStyleSheet(
            f"color:{color}; background:{color}22; border:1px solid {color}55;"
            f"border-radius:10px; padding:2px 4px; font-size:11px; font-weight:600;"
        )


# ── ChildCard ──────────────────────────────────────────────────────────────────
class ChildCard(QFrame):
    clicked = Signal(str)

    def __init__(self, node: dict, parent=None):
        super().__init__(parent)
        self._nid = node["id"]
        self.setFixedHeight(108)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"QFrame{{background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;}}"
            f"QFrame:hover{{border-color:{ACCENT}; background:{SEL};}}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(6)

        top = QHBoxLayout()
        icon = "📁" if node["type"] == "folder" else "📋"
        top.addWidget(lbl(f"{icon}  {node['name']}", 13, bold=True), 1)
        status = node_status(node)
        top.addWidget(StatusBadge(status))
        lay.addLayout(top)

        st = aggregate(node)
        t, d = st["total"], st["done"]
        pct = (d / t * 100) if t > 0 else 0.0

        pr = QHBoxLayout()
        pr.setSpacing(8)
        pr.addWidget(make_pbar(int(pct), status, 12))
        pl = lbl(f"{pct:.0f}%", 11, color=MUTED)
        pl.setMinimumWidth(32)
        pl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pr.addWidget(pl)
        lay.addLayout(pr)

        info = f"{d}/{t} tasks"
        if node["type"] == "folder":
            info += f"  ·  {st['count']} tracker{'s' if st['count'] != 1 else ''}"
        lay.addWidget(lbl(info, 11, color=MUTED))

    def mousePressEvent(self, ev):
        self.clicked.emit(self._nid)
        super().mousePressEvent(ev)


# ── NameDialog ─────────────────────────────────────────────────────────────────
class NameDialog(QDialog):
    def __init__(
        self, title: str, placeholder: str = "", existing: str = "", parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(360)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)
        lay.addWidget(lbl(title, 14, bold=True))
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setText(existing)
        self._edit.selectAll()
        lay.addWidget(self._edit)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        self._edit.returnPressed.connect(self.accept)
        lay.addWidget(bb)

    def get_name(self) -> str:
        return self._edit.text().strip()


# ── CalendarDialog ────────────────────────────────────────────────────────────
class CalendarDialog(QDialog):
    def __init__(self, current: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pick a Date")
        self.setFixedWidth(340)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        self._cal = QCalendarWidget()
        self._cal.setGridVisible(False)
        dt = parse_dt(current)
        if dt:
            self._cal.setSelectedDate(QDate(dt.year, dt.month, dt.day))
        self._cal.activated.connect(lambda _: self.accept())
        lay.addWidget(self._cal)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def get_date(self) -> str:
        return self._cal.selectedDate().toString("yyyy-MM-dd")


# ── WelcomePage ────────────────────────────────────────────────────────────────
class WelcomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(14)
        for w in [
            lbl("🗂️", 52),
            lbl("Task Tracker", 24, bold=True),
            lbl(
                "Select a workspace from the sidebar,\nor right-click to create folders and trackers.",
                13,
                color=MUTED,
                wrap=True,
            ),
        ]:
            w.setAlignment(Qt.AlignCenter)
            lay.addWidget(w)


# ── FolderPage ─────────────────────────────────────────────────────────────────
class FolderPage(QWidget):
    navigate_to = Signal(str)

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self._dm = dm
        self._nid: Optional[str] = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("QScrollArea{background:transparent; border:none;}")
        outer.addWidget(self._scroll)

    def load(self, nid: str):
        self._nid = nid
        self._rebuild()

    def refresh(self):
        if self._nid:
            self._rebuild()

    def _rebuild(self):
        node = self._dm.get(self._nid)
        if not node:
            return

        w = QWidget()
        w.setStyleSheet("background:transparent;")
        self._scroll.setWidget(w)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(28, 24, 28, 32)
        lay.setSpacing(16)

        st = aggregate(node)
        status = node_status(node)
        now = datetime.now()
        total, done = st["total"], st["done"]
        pct = (done / total * 100) if total > 0 else 0.0
        end_dt = st.get("end_dt")

        # Header
        hdr = QHBoxLayout()
        icon = "🌐" if node["id"] == "root" else "📁"
        hdr.addWidget(lbl(f"{icon}  {node['name']}", 20, bold=True))
        hdr.addStretch()
        # Sort selector
        sort_cb = QComboBox()
        sort_cb.addItems(_SORT_LABELS)
        sort_cb.blockSignals(True)
        sort_cb.setCurrentIndex(
            _SORT_KEYS.index(_SORT_MODE) if _SORT_MODE in _SORT_KEYS else 0
        )
        sort_cb.blockSignals(False)
        sort_cb.currentIndexChanged.connect(lambda i: self._set_sort(_SORT_KEYS[i]))
        hdr.addWidget(sort_cb)
        hdr.addWidget(StatusBadge(status))
        lay.addLayout(hdr)
        lay.addWidget(hline())

        # Stat cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        time_str = fmt_delta(end_dt - now) if end_dt else "—"
        time_col = (
            DANGER if end_dt and end_dt < now else WARN if status == "at_risk" else TEXT
        )
        for ltext, vtext, vcol in [
            ("TOTAL TASKS", str(total), TEXT),
            ("COMPLETED", str(done), SUCCESS if done > 0 else TEXT),
            (
                "REMAINING",
                str(max(0, total - done)),
                WARN if total - done > 0 else TEXT,
            ),
            ("TRACKERS", str(st["count"]), TEXT),
            ("NEAREST DEADLINE", time_str, time_col),
        ]:
            stats_row.addWidget(stat_card(ltext, vtext, vcol))
        lay.addLayout(stats_row)

        # Overall progress bar
        pb_row = QHBoxLayout()
        pb_row.setSpacing(10)
        pb = make_pbar(int(pct), status, 18)
        pb_row.addWidget(pb)
        pb_row.addWidget(lbl(f"{pct:.1f}%", 13, bold=True, color=ALIGHT))
        lay.addLayout(pb_row)
        lay.addWidget(hline())

        # ── Default Dates for folder ──────────────────────────────────────────
        if node["id"] != "root":
            lay.addWidget(
                lbl("📅  Default Task Dates (Inherited by new trackers)", 12, bold=True, color=MUTED)
            )
            dlay = QHBoxLayout()
            dlay.setSpacing(10)

            # Start
            self._start_edit = QLineEdit(node.get("start", ""))
            self._start_edit.setPlaceholderText("Default Start")
            self._start_edit.setReadOnly(True)
            self._start_edit.setFixedWidth(130)
            dlay.addWidget(self._date_row(self._start_edit, "Start"))

            # End
            self._end_edit = QLineEdit(node.get("end", ""))
            self._end_edit.setPlaceholderText("Default End")
            self._end_edit.setReadOnly(True)
            self._end_edit.setFixedWidth(130)
            dlay.addWidget(self._date_row(self._end_edit, "End"))

            dlay.addStretch()
            lay.addLayout(dlay)
            lay.addWidget(hline())

        # Children grid
        children = sorted_children(node.get("children", []))
        if children:
            ch_hdr = QHBoxLayout()
            ch_hdr.addWidget(lbl(f"Contents  ({len(children)})", 14, bold=True))
            ch_hdr.addStretch()
            lay.addLayout(ch_hdr)
            grid = QGridLayout()
            grid.setSpacing(12)
            for i, child in enumerate(children):
                card = ChildCard(child)
                card.clicked.connect(self.navigate_to)
                grid.addWidget(card, i // 2, i % 2)
            lay.addLayout(grid)
        else:
            empty = lbl(
                "This folder is empty.\nRight-click it in the sidebar to add trackers or sub-folders.",
                13,
                color=MUTED,
                wrap=True,
            )
            empty.setAlignment(Qt.AlignCenter)
            lay.addWidget(empty)

        # ⚠️ Needs Attention (Focus Board)
        attn = collect_attention_nodes(node)
        if attn:
            lay.addWidget(hline())
            ah = QHBoxLayout()
            ah.addWidget(
                lbl(f"⚠️  Needs Attention  ({len(attn)})", 14, bold=True, color=WARN)
            )
            ah.addStretch()
            lay.addLayout(ah)
            attn_grid = QGridLayout()
            attn_grid.setSpacing(12)
            for i, an in enumerate(attn):
                card = ChildCard(an)
                card.clicked.connect(self.navigate_to)
                attn_grid.addWidget(card, i // 2, i % 2)
            lay.addLayout(attn_grid)

        lay.addStretch()

    def _set_sort(self, mode: str):
        global _SORT_MODE
        _SORT_MODE = mode
        self._rebuild()

    def _date_row(self, edit: QLineEdit, label: str) -> QWidget:
        rw = QWidget()
        rw.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(rw)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)
        rl.addWidget(lbl(f"{label}:", 11, color=MUTED))
        rl.addWidget(edit)
        cb = btn("🗓️", fixed_w=34)
        cb.setFixedHeight(34)
        cb.setToolTip("Pick from calendar")
        cb.clicked.connect(lambda: self._pick_date(edit))
        rl.addWidget(cb)
        clr = btn("✕", fixed_w=34)
        clr.setFixedHeight(34)
        clr.setToolTip(f"Clear default {label.lower()}")
        clr.clicked.connect(lambda: self._clear_date(edit))
        rl.addWidget(clr)
        return rw

    def _pick_date(self, target: QLineEdit):
        dlg = CalendarDialog(target.text(), parent=self)
        if dlg.exec() == QDialog.Accepted:
            target.setText(dlg.get_date())
            self._on_defaults_changed()

    def _clear_date(self, target: QLineEdit):
        target.setText("")
        self._on_defaults_changed()

    def _on_defaults_changed(self):
        node = self._dm.get(self._nid)
        if not node:
            return
        s, e = self._start_edit.text(), self._end_edit.text()
        if s == node.get("start", "") and e == node.get("end", ""):
            return

        apply_retro = False
        trackers = [c for c in node.get("children", []) if c["type"] == "tracker"]
        if trackers:
            res = QMessageBox.question(
                self,
                "Update Existing Tasks?",
                "Do you want to apply these new default dates to all existing trackers in this folder?",
                QMessageBox.Yes | QMessageBox.No,
            )
            apply_retro = res == QMessageBox.Yes

        self._dm.update_folder_defaults(self._nid, s, e, apply_retro)
        self.refresh()


# ── TrackerPage ────────────────────────────────────────────────────────────────
class TrackerPage(QWidget):
    request_refresh = Signal()

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self._dm = dm
        self._nid: Optional[str] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent; border:none;}")
        outer.addWidget(scroll)

        w = QWidget()
        w.setStyleSheet("background:transparent;")
        scroll.setWidget(w)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(28, 24, 28, 40)
        lay.setSpacing(18)

        # ── Header (inline name edit) ──────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(10)
        hdr.addWidget(lbl("📋", 18))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Tracker name")
        self._name_edit.setStyleSheet(
            f"font-size:18px; font-weight:bold; background:transparent;"
            f"border:none; border-bottom:1px solid {BORDER}; border-radius:0;"
            f"color:{TEXT}; padding:4px 2px;"
        )
        hdr.addWidget(self._name_edit, 1)
        hdr.addStretch()
        self._badge = StatusBadge("no_data")
        hdr.addWidget(self._badge)
        lay.addLayout(hdr)
        lay.addWidget(hline())

        # ── Date fields ───────────────────────────────────────────────────────
        date_frame = QFrame()
        date_frame.setStyleSheet(
            f"QFrame{{background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;}}"
        )
        dfl = QFormLayout(date_frame)
        dfl.setContentsMargins(16, 14, 16, 14)
        dfl.setSpacing(10)
        self._start_edit = QLineEdit()
        self._start_edit.setPlaceholderText("YYYY-MM-DD  or  YYYY-MM-DD HH:MM")
        self._end_edit = QLineEdit()
        self._end_edit.setPlaceholderText("YYYY-MM-DD  or  YYYY-MM-DD HH:MM")
        dfl.addRow(lbl("Start:", 12, color=MUTED), self._date_row(self._start_edit))
        dfl.addRow(lbl("Target:", 12, color=MUTED), self._date_row(self._end_edit))
        lay.addWidget(date_frame)

        # ── Tasks section ──────────────────────────────────────────────────────
        task_frame = QFrame()
        task_frame.setStyleSheet(
            f"QFrame{{background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;}}"
        )
        tfl = QVBoxLayout(task_frame)
        tfl.setContentsMargins(16, 14, 16, 14)
        tfl.setSpacing(12)

        total_row = QHBoxLayout()
        total_row.addWidget(lbl("Total Tasks:", 12, color=MUTED))
        self._total_spin = QSpinBox()
        self._total_spin.setRange(0, 99999)
        self._total_spin.setFixedWidth(110)
        total_row.addWidget(self._total_spin)
        total_row.addStretch()
        tfl.addLayout(total_row)

        done_row = QHBoxLayout()
        done_row.setSpacing(8)
        done_row.addWidget(lbl("Completed:", 12, color=MUTED))
        done_row.addStretch()
        self._dec_btn = btn("−", fixed_w=38)
        self._dec_btn.setFixedHeight(38)
        self._done_lbl = lbl("0", 20, bold=True, color=ALIGHT)
        self._done_lbl.setAlignment(Qt.AlignCenter)
        self._done_lbl.setMinimumWidth(64)
        self._inc_btn = btn("+", fixed_w=38)
        self._inc_btn.setFixedHeight(38)
        for bw in (self._dec_btn, self._done_lbl, self._inc_btn):
            done_row.addWidget(bw)
        tfl.addLayout(done_row)

        self._task_pb = make_pbar(0, "no_data", 14)
        tfl.addWidget(self._task_pb)
        lay.addWidget(task_frame)

        # ── Live Results section ───────────────────────────────────────────────
        res_frame = QFrame()
        res_frame.setStyleSheet(
            f"QFrame{{background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;}}"
        )
        rfl = QVBoxLayout(res_frame)
        rfl.setContentsMargins(16, 14, 16, 14)
        rfl.setSpacing(10)
        rfl.addWidget(lbl("📊  Live Stats", 12, bold=True, color=MUTED))
        self._time_pb = make_pbar(0, "no_data", 14)
        rfl.addWidget(self._time_pb)
        self._time_lbl = lbl("Time Remaining: —", 13)
        self._pct_lbl = lbl("Time Elapsed: —", 13)
        self._avg_lbl = lbl("Tasks / Day Needed: —", 13)
        self._eta_lbl = lbl("Est. Completion: —", 13, color=MUTED)
        for rl in (self._time_lbl, self._pct_lbl, self._avg_lbl, self._eta_lbl):
            rfl.addWidget(rl)
        lay.addWidget(res_frame)

        # ── Notes field ────────────────────────────────────────────────────────────
        notes_frame = QFrame()
        notes_frame.setStyleSheet(
            f"QFrame{{background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;}}"
        )
        nfl = QVBoxLayout(notes_frame)
        nfl.setContentsMargins(16, 12, 16, 12)
        nfl.setSpacing(8)
        nfl.addWidget(lbl("📝  Notes", 12, bold=True, color=MUTED))
        self._notes_area = QTextEdit()
        self._notes_area.setPlaceholderText(
            "Add notes, links, or context for this tracker..."
        )
        self._notes_area.setFixedHeight(96)
        nfl.addWidget(self._notes_area)
        lay.addWidget(notes_frame)

        lay.addStretch()

        # Connections — all fields auto-save; no manual save button needed
        self._dec_btn.clicked.connect(self._decrement)
        self._inc_btn.clicked.connect(self._increment)
        self._name_edit.editingFinished.connect(self._autosave)
        self._start_edit.editingFinished.connect(self._on_date_changed)
        self._end_edit.editingFinished.connect(self._on_date_changed)
        self._total_spin.valueChanged.connect(self._on_total_changed)
        self._notes_timer = QTimer()
        self._notes_timer.setSingleShot(True)
        self._notes_timer.setInterval(700)
        self._notes_area.textChanged.connect(self._notes_timer.start)
        self._notes_timer.timeout.connect(self._autosave)

    # ── Internal ───────────────────────────────────────────────────────────────
    def _current_done(self) -> int:
        return int(self._done_lbl.text())

    def _refresh_pbar(self, pb: QProgressBar, value: int, status: str):
        pb.setValue(value)
        pb.setProperty("status", status)
        pb.style().unpolish(pb)
        pb.style().polish(pb)

    def _set_done_display(self, done: int, total: int):
        done = max(0, min(done, total))
        self._done_lbl.setText(str(done))
        self._dec_btn.setEnabled(done > 0)
        self._inc_btn.setEnabled(total > done)
        pct = int(done / total * 100) if total > 0 else 0
        status = node_status(self._dm.get(self._nid)) if self._nid else "no_data"
        self._refresh_pbar(self._task_pb, pct, status)

    def load(self, nid: str):
        self._nid = nid
        node = self._dm.get(nid)
        if not node:
            return
        for w in (self._name_edit, self._start_edit, self._end_edit, self._total_spin):
            w.blockSignals(True)
        self._notes_timer.stop()
        self._notes_area.blockSignals(True)
        self._name_edit.setText(node.get("name", ""))
        self._start_edit.setText(node.get("start", ""))
        self._end_edit.setText(node.get("end", ""))
        self._total_spin.setValue(node.get("total", 0))
        self._set_done_display(node.get("done", 0), node.get("total", 0))
        self._notes_area.setPlainText(node.get("notes", ""))
        for w in (self._name_edit, self._start_edit, self._end_edit, self._total_spin):
            w.blockSignals(False)
        self._notes_area.blockSignals(False)
        self._update_stats()

    def refresh(self):
        if self._nid:
            self._update_stats()

    def _increment(self):
        total = self._total_spin.value()
        self._set_done_display(self._current_done() + 1, total)
        self._autosave()
        self._update_stats()

    def _decrement(self):
        total = self._total_spin.value()
        self._set_done_display(self._current_done() - 1, total)
        self._autosave()
        self._update_stats()

    def _date_row(self, edit: QLineEdit) -> QWidget:
        rw = QWidget()
        rw.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(rw)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)
        rl.addWidget(edit)
        cb = btn("🗓️", fixed_w=34)
        cb.setFixedHeight(34)
        cb.setToolTip("Pick from calendar")
        cb.clicked.connect(lambda: self._pick_date(edit))
        rl.addWidget(cb)
        return rw

    def _pick_date(self, target: QLineEdit):
        dlg = CalendarDialog(target.text(), parent=self)
        if dlg.exec() == QDialog.Accepted:
            target.setText(dlg.get_date())
            self._on_date_changed()

    def _on_date_changed(self):
        self._autosave()
        self._update_stats()

    def _on_total_changed(self, val: int):
        self._set_done_display(self._current_done(), val)
        self._autosave()
        self._update_stats()

    def _autosave(self):
        if not self._nid:
            return
        total = self._total_spin.value()
        done = min(self._current_done(), total)
        self._dm.update_tracker(
            self._nid,
            name=self._name_edit.text().strip(),
            start=self._start_edit.text().strip(),
            end=self._end_edit.text().strip(),
            total=total,
            done=done,
            notes=self._notes_area.toPlainText(),
        )
        self.request_refresh.emit()

    def _update_stats(self):
        if not self._nid:
            return
        node = self._dm.get(self._nid)
        if not node:
            return
        start_dt = parse_dt(self._start_edit.text())
        end_dt = parse_dt(self._end_edit.text())
        now = datetime.now()
        status = node_status(node)
        self._badge.set_status(status)

        if start_dt and end_dt and start_dt < end_dt:
            total_s = (end_dt - start_dt).total_seconds()
            elapsed_s = (now - start_dt).total_seconds()
            time_pct = max(0.0, min(elapsed_s / total_s, 1.0)) * 100
            self._time_lbl.setText(f"Time Remaining:  {fmt_delta(end_dt - now)}")
            self._pct_lbl.setText(f"Time Elapsed:  {time_pct:.2f}%")
            self._refresh_pbar(self._time_pb, int(time_pct), status)
            total_t = self._total_spin.value()
            done_t = self._current_done()
            rem_t = max(0, total_t - done_t)
            rem_d = max(0.0, (end_dt - now).total_seconds()) / 86400.0
            if total_t > 0:
                if rem_d > 1e-6 and rem_t > 0:
                    self._avg_lbl.setText(f"Tasks / Day Needed:  {rem_t / rem_d:.2f}")
                elif rem_t == 0:
                    self._avg_lbl.setText("Tasks / Day Needed:  0  — All done! 🎉")
                else:
                    self._avg_lbl.setText("Tasks / Day Needed:  Past due ⚠️")
            else:
                self._avg_lbl.setText("Tasks / Day Needed:  —")
            # Velocity & ETA
            elapsed_d = max(1e-9, elapsed_s) / 86400.0
            if done_t > 0 and rem_t > 0:
                velocity = done_t / elapsed_d
                eta = now + timedelta(days=rem_t / velocity)
                self._eta_lbl.setText(
                    f"Est. Completion:  {eta.strftime('%b %d, %Y')}  ·  {velocity:.1f} tasks/day"
                )
            elif done_t == 0:
                self._eta_lbl.setText("Est. Completion:  —  (not started)")
            else:
                self._eta_lbl.setText("Est. Completion:  All done! 🎉")
        else:
            for l in (self._time_lbl, self._pct_lbl, self._avg_lbl):
                text = l.text().split(":")[0]
                l.setText(f"{text}:  —")
            self._eta_lbl.setText("Est. Completion:  —")
            self._refresh_pbar(self._time_pb, 0, "no_data")


# ── WorkspaceTree ────────────────────────────────────────────────────────────
class WorkspaceTree(QTreeWidget):
    node_moved = Signal(str, str)  # (nid, new_parent_id)

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self._dm = dm
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dragEnterEvent(self, event):
        item = self.currentItem()
        if item and item.data(0, Qt.UserRole) != "root":
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        dragged = self.currentItem()
        if not dragged:
            event.ignore()
            return
        nid = dragged.data(0, Qt.UserRole)
        if nid == "root":
            event.ignore()
            return

        target = self.itemAt(event.position().toPoint())
        drop_pos = self.dropIndicatorPosition()

        if target is None or drop_pos == QAbstractItemView.OnViewport:
            new_parent_id = "root"
        else:
            target_nid = target.data(0, Qt.UserRole)
            target_node = self._dm.get(target_nid)
            if (
                drop_pos == QAbstractItemView.OnItem
                and target_node
                and target_node["type"] == "folder"
            ):
                new_parent_id = target_nid
            else:
                p_item = target.parent()
                new_parent_id = p_item.data(0, Qt.UserRole) if p_item else "root"

        event.ignore()  # prevent Qt from rearranging items; we handle it via data model
        if not self._dm._is_descendant(nid, new_parent_id) and new_parent_id != nid:
            self.node_moved.emit(nid, new_parent_id)


# ── Sidebar ────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    node_selected = Signal(str)
    tree_changed = Signal()

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self._dm = dm
        self.setMinimumWidth(180)
        self.setMaximumWidth(500)
        self.resize(265, self.height())
        self.setStyleSheet(f"background:{PANEL};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Sidebar header bar
        hdr = QWidget()
        hdr.setStyleSheet(f"background:{PANEL}; border-bottom:1px solid {BORDER};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 10, 10, 10)
        hl.setSpacing(6)
        hl.addWidget(lbl("Workspaces", 13, bold=True))
        hl.addStretch()
        self._af_btn = btn("📁+", role="muted", fixed_w=38)
        self._af_btn.setToolTip("New Folder at root")
        self._at_btn = btn("📋+", role="muted", fixed_w=38)
        self._at_btn.setToolTip("New Tracker at root")
        hl.addWidget(self._af_btn)
        hl.addWidget(self._at_btn)
        lay.addWidget(hdr)

        # Search bar
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search trackers...")
        self._search.setStyleSheet(
            f"QLineEdit{{background:{SURFACE}; border:none;"
            f"border-bottom:1px solid {BORDER}; border-radius:0; padding:7px 12px;}}"
        )
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._filter_tree)
        lay.addWidget(self._search)

        # Tree widget
        self._tree = WorkspaceTree(self._dm)
        self._tree.setHeaderHidden(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.setIndentation(16)
        self._tree.setAnimated(True)
        lay.addWidget(self._tree, 1)

        self._af_btn.clicked.connect(lambda: self._add_node("folder", "root"))
        self._at_btn.clicked.connect(lambda: self._add_node("tracker", "root"))
        self._tree.itemSelectionChanged.connect(self._on_selection)
        self._tree.customContextMenuRequested.connect(self._ctx_menu)
        self._tree.node_moved.connect(self._on_node_moved)

        self.rebuild()

    def rebuild(self, select_id: Optional[str] = None):
        self._tree.blockSignals(True)
        self._tree.clear()

        root_item = QTreeWidgetItem(self._tree)
        root_item.setText(0, f"🌐  {self._dm.root['name']}")
        root_item.setData(0, Qt.UserRole, "root")
        f = root_item.font(0)
        f.setBold(True)
        root_item.setFont(0, f)
        self._populate(root_item, self._dm.root)
        self._tree.expandAll()
        self._tree.blockSignals(False)

        if select_id:
            self._select_by_id(select_id)
        else:
            self._tree.setCurrentItem(root_item)
            self._on_selection()

    def _populate(self, parent_item: QTreeWidgetItem, node: dict):
        for child in node.get("children", []):
            icon = "📁" if child["type"] == "folder" else "📋"
            status = node_status(child)
            s_icon = STATUS_INFO.get(status, ("", MUTED))[0].split()[0]
            item = QTreeWidgetItem(parent_item)
            item.setText(0, f"{icon}  {child['name']}  {s_icon}")
            item.setData(0, Qt.UserRole, child["id"])
            if child["type"] == "folder":
                self._populate(item, child)

    def _select_by_id(self, nid: str):
        it = self._find_item(self._tree.invisibleRootItem(), nid)
        if it:
            self._tree.setCurrentItem(it)

    def _find_item(
        self, parent: QTreeWidgetItem, nid: str
    ) -> Optional[QTreeWidgetItem]:
        for i in range(parent.childCount()):
            ch = parent.child(i)
            if ch.data(0, Qt.UserRole) == nid:
                return ch
            found = self._find_item(ch, nid)
            if found:
                return found
        return None

    def _on_selection(self):
        items = self._tree.selectedItems()
        if items:
            nid = items[0].data(0, Qt.UserRole)
            if nid:
                self.node_selected.emit(nid)

    def _ctx_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        nid = item.data(0, Qt.UserRole)
        node = self._dm.get(nid)
        if not node:
            return

        menu = QMenu(self)
        if node["type"] == "folder":
            a = menu.addAction("📋  Add Tracker Here")
            a.triggered.connect(lambda: self._add_node("tracker", nid))
            b = menu.addAction("📁  Add Folder Here")
            b.triggered.connect(lambda: self._add_node("folder", nid))
            menu.addSeparator()

        ren = menu.addAction("✏️  Rename")
        ren.triggered.connect(lambda: self._rename(nid))

        if nid != "root":
            menu.addSeparator()
            up = menu.addAction("⬆️  Move Up")
            up.triggered.connect(lambda: self._reorder(nid, -1))
            dn = menu.addAction("⬇️  Move Down")
            dn.triggered.connect(lambda: self._reorder(nid, +1))
            menu.addSeparator()
            dl = menu.addAction("🗑️  Delete")
            dl.triggered.connect(lambda: self._delete(nid))

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _add_node(self, kind: str, parent_id: str):
        label = "Folder" if kind == "folder" else "Tracker"
        dlg = NameDialog(f"New {label}", f"Enter {label.lower()} name", parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.get_name():
            child = (
                new_folder(dlg.get_name())
                if kind == "folder"
                else new_tracker(dlg.get_name())
            )
            self._dm.add_child(parent_id, child)
            self.rebuild(child["id"])
            self.tree_changed.emit()

    def _rename(self, nid: str):
        node = self._dm.get(nid)
        if not node:
            return
        dlg = NameDialog("Rename", existing=node["name"], parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.get_name():
            self._dm.rename(nid, dlg.get_name())
            self.rebuild(nid)
            self.tree_changed.emit()

    def _reorder(self, nid: str, direction: int):
        self._dm.reorder(nid, direction)
        self.rebuild(nid)
        self.tree_changed.emit()

    def _delete(self, nid: str):
        node = self._dm.get(nid)
        if not node:
            return
        kind = "folder and all its contents" if node["type"] == "folder" else "tracker"
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f'Delete "{node["name"]}" ({kind})?\nThis cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._dm.remove(nid)
            self.rebuild("root")
            self.tree_changed.emit()

    def _on_node_moved(self, nid: str, new_parent_id: str):
        self._dm.move_node(nid, new_parent_id)
        self.rebuild(nid)
        self.tree_changed.emit()

    def _filter_tree(self, query: str):
        q = query.lower().strip()
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._filter_item(root.child(i), q)

    def _filter_item(self, item: QTreeWidgetItem, q: str) -> bool:
        nid = item.data(0, Qt.UserRole)
        node = self._dm.get(nid)
        name_match = not q or (node and q in node.get("name", "").lower())
        child_visible = False
        for i in range(item.childCount()):
            child_visible |= self._filter_item(item.child(i), q)
        visible = bool(name_match or child_visible)
        item.setHidden(not visible)
        if child_visible and q:
            item.setExpanded(True)
        return visible

    def current_id(self) -> Optional[str]:
        items = self._tree.selectedItems()
        return items[0].data(0, Qt.UserRole) if items else None


# ── MainWindow ─────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._dm = DataManager()
        self._dm.load()
        self.setWindowTitle("Task Tracker")
        self.setMinimumSize(1020, 660)
        self.resize(1160, 740)

        root_w = QWidget()
        self.setCentralWidget(root_w)
        root_lay = QVBoxLayout(root_w)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # Top header bar
        hbar = QWidget()
        hbar.setFixedHeight(56)
        hbar.setStyleSheet(f"background:{PANEL}; border-bottom:1px solid {BORDER};")
        hbl = QHBoxLayout(hbar)
        hbl.setContentsMargins(20, 0, 20, 0)
        hbl.addWidget(lbl("🗂️  Task Tracker", 15, bold=True))
        hbl.addStretch()
        hbl.addWidget(
            lbl(datetime.now().strftime("📅  %A, %B %-d  %Y"), 12, color=MUTED)
        )
        root_lay.addWidget(hbar)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        root_lay.addWidget(splitter, 1)

        self._sidebar = Sidebar(self._dm)
        splitter.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        splitter.addWidget(self._stack)
        self._welcome_page = WelcomePage()
        self._folder_page = FolderPage(self._dm)
        self._tracker_page = TrackerPage(self._dm)
        self._stack.addWidget(self._welcome_page)  # 0
        self._stack.addWidget(self._folder_page)  # 1
        self._stack.addWidget(self._tracker_page)  # 2

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self._sidebar.node_selected.connect(self._show_node)
        self._sidebar.tree_changed.connect(self._on_tree_changed)
        self._folder_page.navigate_to.connect(self._navigate_to)
        self._tracker_page.request_refresh.connect(self._on_tracker_change)

        # Auto-refresh timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._auto_refresh)
        self._timer.start(UPD_MS)

    def _show_node(self, nid: str):
        node = self._dm.get(nid)
        if not node:
            self._stack.setCurrentIndex(0)
            return
        if node["type"] == "folder":
            self._folder_page.load(nid)
            self._stack.setCurrentIndex(1)
        else:
            self._tracker_page.load(nid)
            self._stack.setCurrentIndex(2)

    def _navigate_to(self, nid: str):
        self._sidebar.rebuild(nid)
        self._show_node(nid)

    def _on_tree_changed(self):
        cur = self._sidebar.current_id()
        if cur:
            self._show_node(cur)

    def _on_tracker_change(self):
        self._sidebar.rebuild(self._sidebar.current_id())

    def _auto_refresh(self):
        idx = self._stack.currentIndex()
        if idx == 1:
            self._folder_page.refresh()
        elif idx == 2:
            self._tracker_page.refresh()


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if platform.system().lower() == "linux":
        os.environ.setdefault(
            "QT_QPA_PLATFORM", "xcb"
        )  # force XWayland; fixes splitter mouse-grab
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
