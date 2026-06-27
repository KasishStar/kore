"""
DisplayEngine — Terminal formatting for tables, trees, highlights, badges.
No external dependencies, pure ANSI escape codes.
"""

import os
import shutil


class DisplayEngine:
    def __init__(self):
        self.terminal_width = shutil.get_terminal_size((80, 20)).columns

    # ── ANSI CODES ───────────────────────────────────────────────
    class Style:
        BOLD = "\033[1m"
        DIM = "\033[2m"
        ITALIC = "\033[3m"
        UNDERLINE = "\033[4m"
        RESET = "\033[0m"

    class Color:
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        GRAY = "\033[90m"

        BG_RED = "\033[41m"
        BG_GREEN = "\033[42m"
        BG_YELLOW = "\033[43m"
        BG_BLUE = "\033[44m"
        BG_MAGENTA = "\033[45m"
        BG_CYAN = "\033[46m"
        BG_GRAY = "\033[100m"

    @staticmethod
    def bold(text):
        return f"{DisplayEngine.Style.BOLD}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def dim(text):
        return f"{DisplayEngine.Style.DIM}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def italic(text):
        return f"{DisplayEngine.Style.ITALIC}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def color(text, color_code):
        return f"{color_code}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def highlight(text, bg_code=None, fg_code=None):
        parts = []
        if bg_code:
            parts.append(bg_code)
        if fg_code:
            parts.append(fg_code)
        parts.append(text)
        parts.append(DisplayEngine.Style.RESET)
        return "".join(parts)

    # ── BADGES ───────────────────────────────────────────────────

    @staticmethod
    def badge_success(text):
        return f" {DisplayEngine.highlight(' ✓ ', DisplayEngine.Color.BG_GREEN, DisplayEngine.Color.BLACK)} {DisplayEngine.Color.GREEN}{DisplayEngine.Style.BOLD}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def badge_error(text):
        return f" {DisplayEngine.highlight(' ✗ ', DisplayEngine.Color.BG_RED, DisplayEngine.Color.WHITE)} {DisplayEngine.Color.RED}{DisplayEngine.Style.BOLD}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def badge_info(text):
        return f" {DisplayEngine.highlight(' ℹ ', DisplayEngine.Color.BG_BLUE, DisplayEngine.Color.WHITE)} {DisplayEngine.Color.CYAN}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def badge_warn(text):
        return f" {DisplayEngine.highlight(' ⚠ ', DisplayEngine.Color.BG_YELLOW, DisplayEngine.Color.BLACK)} {DisplayEngine.Color.YELLOW}{text}{DisplayEngine.Style.RESET}"

    @staticmethod
    def badge_arrow(text):
        return f" {DisplayEngine.Color.MAGENTA}▸{DisplayEngine.Style.RESET} {DisplayEngine.Style.BOLD}{text}{DisplayEngine.Style.RESET}"

    # ── TABLE ────────────────────────────────────────────────────

    def table(self, headers, rows, max_width=None):
        """Draws a formatted table with borders."""
        if max_width is None:
            max_width = self.terminal_width - 4

        ncols = len(headers)
        col_widths = [len(h) for h in headers]

        for row in rows:
            for i, cell in enumerate(row):
                cell_str = str(cell)
                col_widths[i] = max(col_widths[i], len(cell_str))

        total_width = sum(col_widths) + (ncols * 3) + 1
        if total_width > max_width:
            scale = (max_width - (ncols * 3) - 1) / (total_width - (ncols * 3) - 1)
            col_widths = [max(10, int(w * scale)) for w in col_widths]

        sep = self.dim("─" * (sum(col_widths) + (ncols * 3) + 1))

        lines = []
        lines.append(sep)

        header_cells = []
        for i, h in enumerate(headers):
            padded = h.ljust(col_widths[i])
            header_cells.append(f" {self.bold(self.Color.CYAN(padded))} ")
        lines.append("│" + "│".join(header_cells) + "│")
        lines.append(sep)

        for row_idx, row in enumerate(rows):
            cells = []
            for i, cell in enumerate(row):
                cell_str = str(cell).ljust(col_widths[i])
                cells.append(f" {cell_str} ")
            lines.append("│" + "│".join(cells) + "│")

        lines.append(sep)
        return "\n".join(lines)

    # ── TREE / FLOWCHART ─────────────────────────────────────────

    @staticmethod
    def tree(nodes, indent=0):
        """Draws an ASCII tree from nested list of (label, children) tuples."""
        lines = []
        prefix = "  " * indent
        for i, node in enumerate(nodes):
            if isinstance(node, tuple):
                label, children = node
            else:
                label = node
                children = []

            is_last = (i == len(nodes) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "

            lines.append(f"{prefix}{connector}{label}")
            if children:
                lines.extend(DisplayEngine.tree(children, indent + 1))
        return lines

    @staticmethod
    def flowchart(steps):
        """Draws a simple vertical flow chart from a list of step labels."""
        lines = []
        for i, step in enumerate(steps):
            is_active = isinstance(step, tuple) and step[1]
            label = step[0] if isinstance(step, tuple) else step

            if is_active:
                lines.append(f"  {DisplayEngine.highlight(f' {label} ', DisplayEngine.Color.BG_CYAN, DisplayEngine.Color.BLACK)}")
            else:
                lines.append(f"  ┌─ {DisplayEngine.bold(label)} ─┐")

            if i < len(steps) - 1:
                lines.append(f"     {DisplayEngine.dim('│')}")
                lines.append(f"     {DisplayEngine.dim('▼')}")
        return "\n".join(lines)

    # ── KEY-VALUE LIST ───────────────────────────────────────────

    @staticmethod
    def kv_list(items):
        """Draws a key-value list with aligned values."""
        if not items:
            return ""
        max_k = max(len(str(k)) for k, v in items)
        lines = []
        for k, v in items:
            key_str = str(k).ljust(max_k)
            lines.append(f"  {DisplayEngine.bold(key_str)} : {v}")
        return "\n".join(lines)

    # ── DIVIDER ──────────────────────────────────────────────────

    @staticmethod
    def divider(char="=", width=80):
        try:
            width = shutil.get_terminal_size((80, 20)).columns
        except Exception:
            pass
        return DisplayEngine.dim(char * width)

    def section_header(self, title):
        return f"\n{self.bold(self.Color.CYAN(title))}\n{self.dim('─' * self.terminal_width)}"

    # ── CODE BLOCK ───────────────────────────────────────────────

    @staticmethod
    def code_block(code, language=""):
        lines = code.split("\n")
        result = [f"  {DisplayEngine.dim('┌─ ' + language + ' ' + '─' * 40)}"]
        for line in lines:
            result.append(f"  {DisplayEngine.dim('│')} {line}")
        result.append(f"  {DisplayEngine.dim('└' + '─' * 50)}")
        return "\n".join(result)

    # ── ARCHITECTURE DIAGRAM ─────────────────────────────────────

    @staticmethod
    def architecture_diagram(components):
        """Draws a simple horizontal architecture flow.
        components: list of (label, color_func) tuples
        """
        if not components:
            return ""

        boxes = []
        for label, color_fn in components:
            box = f"[ {color_fn(label)} ]"
            boxes.append(box)

        arrow = f" {DisplayEngine.dim('───►')} "
        return "  " + arrow.join(boxes)
