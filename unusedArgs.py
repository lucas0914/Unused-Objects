import sys
import os
import re
import base64
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QFileDialog,
    QListWidget, QHBoxLayout, QMessageBox, QListWidgetItem, QSizePolicy
)
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QFont, QPalette
from PyQt6.QtCore import Qt, QSize
from images import *


class MDLAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDL Analyzer")
        self.setMinimumSize(1200, 700)

        self.button_open = QPushButton("Open Directory")

        self.button_check_all = QPushButton()
        self.button_check_all.setIcon(icon_from_base64(select_theme_icon(
            check_all_png_base64l, check_all_png_base64d)))
        self.button_check_all.setIconSize(QSize(24, 24))
        self.button_check_all.setFixedSize(30, 30)
        self.button_check_all.setFlat(True)
        self.button_check_all.setToolTip("Check All")

        self.button_uncheck_all = QPushButton()
        self.button_uncheck_all.setIcon(icon_from_base64(select_theme_icon(
            uncheck_all_png_base64l, uncheck_all_png_base64d)))
        self.button_uncheck_all.setIconSize(QSize(24, 24))
        self.button_uncheck_all.setFixedSize(30, 30)
        self.button_uncheck_all.setFlat(True)
        self.button_uncheck_all.setToolTip("Uncheck All")

        self.button_open = QPushButton()
        self.button_open.setIcon(icon_from_base64(open_folder_png_base64d))
        self.button_open.setIconSize(QSize(24, 24))
        self.button_open.setFixedSize(30, 30)
        self.button_open.setFlat(True)
        self.button_open.setToolTip("Open Directory")

        self.button_clean = QPushButton()
        self.button_clean.setIcon(icon_from_base64(remove_save_png_base64d))
        self.button_clean.setIconSize(QSize(24, 24))
        self.button_clean.setFixedSize(30, 30)
        self.button_clean.setFlat(True)
        self.button_clean.setToolTip("Remove Unused and Save")
        self.button_clean.setEnabled(False)

        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(220)
        self.file_list.setIconSize(QSize(12, 12))
        self.file_list.setStyleSheet("""
                QListWidget::indicator {
                    width: 12px;
                    height: 12px;
                }
            """)

        self.text_edit_original = QTextEdit()
        self.text_edit_cleaned = QTextEdit()

        for editor in (self.text_edit_original, self.text_edit_cleaned):
            editor.setFont(QFont("Courier New", 10))
            editor.setReadOnly(True)
            editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # === LEFT BUTTONS (Open, Check All, Uncheck All) ===
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.addWidget(self.button_open)
        left_buttons_layout.addSpacing(10)
        left_buttons_layout.addWidget(self.button_check_all)
        left_buttons_layout.addWidget(self.button_uncheck_all)
        left_buttons_layout.addWidget(self.button_clean)
        left_buttons_layout.addStretch()

        left_buttons_widget = QWidget()
        left_buttons_widget.setLayout(left_buttons_layout)

        # === FILE LIST ===
        file_list_layout = QVBoxLayout()
        file_list_layout.addWidget(self.file_list)
        file_list_widget = QWidget()
        file_list_widget.setLayout(file_list_layout)

        # Set size policies so editors expand properly
        for editor in (self.text_edit_original, self.text_edit_cleaned):
            editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a widget container for the two editors side by side
        text_edit_widget = QWidget()
        text_edit_layout = QHBoxLayout(text_edit_widget)
        text_edit_layout.setContentsMargins(0, 0, 0, 0)
        text_edit_layout.addWidget(self.text_edit_original)
        text_edit_layout.addWidget(self.text_edit_cleaned)
        text_edit_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.text_edit_original.setMinimumHeight(300)
        self.text_edit_cleaned.setMinimumHeight(300)

        # Create layout for the buttons stacked vertically on the left
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.addWidget(self.button_open)
        left_buttons_layout.addWidget(self.button_check_all)
        left_buttons_layout.addWidget(self.button_uncheck_all)
        left_buttons_layout.addWidget(self.button_clean)
        left_buttons_layout.addStretch()  # Push buttons to top

        # Combine buttons and file list horizontally
        file_list_layout = QHBoxLayout()
        file_list_layout.addLayout(left_buttons_layout)
        file_list_layout.addWidget(self.file_list)

        # Right side: editors stacked vertically with stretch so they expand fully
        right_side_layout = QVBoxLayout()
        right_side_layout.addWidget(text_edit_widget)
        right_side_layout.setStretch(0, 1)  # make editors expand vertically

        # Main layout: left side with files/buttons, right side with editors + clean button
        main_layout = QHBoxLayout()
        main_layout.addLayout(file_list_layout)
        main_layout.addLayout(right_side_layout)

        # Make sure editors area gets more horizontal space
        main_layout.setStretch(0, 1)  # left: file list
        main_layout.setStretch(1, 3)  # right: text editors

        self.setLayout(main_layout)

        def apply_os_theme(widget):
            palette = widget.palette()
            is_dark_mode = palette.color(QPalette.ColorRole.Window).value() < 128

            if is_dark_mode:
                dark_palette = QPalette()
                dark_palette.setColor(QPalette.ColorRole.Window, QColor("#121212"))
                dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
                dark_palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
                dark_palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
                dark_palette.setColor(QPalette.ColorRole.Button, QColor("#1e1e1e"))
                dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
                widget.setPalette(dark_palette)
            else:
                widget.setPalette(QApplication.style().standardPalette())

        apply_os_theme(self)

        # Connect signals as before...
        self.button_open.clicked.connect(self.open_directory)
        self.button_check_all.clicked.connect(self.check_all_files)
        self.button_uncheck_all.clicked.connect(self.uncheck_all_files)
        self.button_clean.clicked.connect(self.remove_and_save_unused)
        self.file_list.itemClicked.connect(self.file_selected)

        self.unused_line_indexes = set()
        self.current_file = ""
        self.modified_lines = []
        self.original_lines_map = {}
        self.checked_files = []

        # --- Sync vertical scrollbars ---
        self._scroll_syncing = False
        # Vertical scrollbar sync
        self.text_edit_original.verticalScrollBar().valueChanged.connect(
            self.sync_scroll_original_to_cleaned_vertical
        )
        self.text_edit_cleaned.verticalScrollBar().valueChanged.connect(
            self.sync_scroll_cleaned_to_original_vertical
        )
        # Horizontal scrollbar sync
        self.text_edit_original.horizontalScrollBar().valueChanged.connect(
            self.sync_scroll_original_to_cleaned_horizontal
        )
        self.text_edit_cleaned.horizontalScrollBar().valueChanged.connect(
            self.sync_scroll_cleaned_to_original_horizontal
        )

    def sync_scroll_original_to_cleaned_vertical(self, value):
        if self._scroll_syncing:
            return
        self._scroll_syncing = True
        self.text_edit_cleaned.verticalScrollBar().setValue(value)
        self._scroll_syncing = False

    def sync_scroll_cleaned_to_original_vertical(self, value):
        if self._scroll_syncing:
            return
        self._scroll_syncing = True
        self.text_edit_original.verticalScrollBar().setValue(value)
        self._scroll_syncing = False

    def sync_scroll_original_to_cleaned_horizontal(self, value):
        if self._scroll_syncing:
            return
        self._scroll_syncing = True
        self.text_edit_cleaned.horizontalScrollBar().setValue(value)
        self._scroll_syncing = False

    def sync_scroll_cleaned_to_original_horizontal(self, value):
        if self._scroll_syncing:
            return
        self._scroll_syncing = True
        self.text_edit_original.horizontalScrollBar().setValue(value)
        self._scroll_syncing = False

    def open_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not dir_path:
            return

        self.file_list.clear()
        self.original_lines_map.clear()

        for root, _, files in os.walk(dir_path):  # Recursively walk through all subdirectories
            for file in files:
                if file.endswith(".mdl"):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r") as f:
                        content = f.readlines()
                    _, unused = self.process_mdl(content)
                    if unused:
                        item = QListWidgetItem(full_path)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.file_list.addItem(item)
                        self.original_lines_map[full_path] = content

        self.button_clean.setEnabled(self.file_list.count() > 0)

    def check_all_files(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)

    def uncheck_all_files(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

    def file_selected(self, item):
        self.current_file = item.text()
        lines = self.original_lines_map.get(self.current_file)
        if not lines:
            with open(self.current_file, "r") as f:
                lines = f.readlines()

        self.modified_lines, self.unused_line_indexes = self.process_mdl(lines)

        self.text_edit_original.setPlainText("".join(lines))
        self.text_edit_original.moveCursor(QTextCursor.MoveOperation.End)
        self.text_edit_original.moveCursor(QTextCursor.MoveOperation.Start)

        self.text_edit_cleaned.setPlainText("".join(
            line for i, line in enumerate(lines) if i not in self.unused_line_indexes
        ))

        self.highlight_unused_lines(self.text_edit_original, self.unused_line_indexes)

    def remove_and_save_unused(self):
        self.checked_files = [
            self.file_list.item(i).text()
            for i in range(self.file_list.count())
            if self.file_list.item(i).checkState() == Qt.CheckState.Checked
        ]

        if not self.checked_files:
            QMessageBox.warning(self, "No files selected", "Please check at least one file.")
            return

        for file_path in self.checked_files:
            with open(file_path, "r") as f:
                original_lines = f.readlines()

            _, unused_indexes = self.process_mdl(original_lines)

            cleaned_original = [
                line for i, line in enumerate(original_lines) if i not in unused_indexes
            ]

            # Create backup file first
            backup_path = file_path.replace(".mdl", "_bkp.mdl")
            with open(backup_path, "w") as bkp_f:
                bkp_f.writelines(original_lines)

            # Now overwrite original file with cleaned content
            with open(file_path, "w") as f:
                f.writelines(cleaned_original)

        QMessageBox.information(self, "Saved", "Backups created and original files updated.")

    def process_mdl(self, lines):
        system_line_re = re.compile(r"\*System\s*\(\s*([\w]+)\s*,\s*\"[^\"]*\"\s*,\s*([\w]+)\s*\)")
        define_system_re = re.compile(r"\*DefineSystem\s*\(\s*([\w]+)\s*\)")
        decl_types = ("*Point", "*Marker", "*Body", "*Vector")
        set_line_re = re.compile(r"\*Set\w*", re.IGNORECASE)
        var_regex = re.compile(r'\b([a-zA-Z_][a-zA-Z_0-9]*)\b')
        skip_words = {'true', 'false', 'TRANS', 'P_Global_Origin', 'B_Ground', 'MODEL'}

        begin_context_re = re.compile(r"\*BeginContext\s*\(\s*([\w]+)\s*\)")
        end_context_re = re.compile(r"\*EndContext")

        system_instances = []
        for line in lines:
            m = system_line_re.match(line.strip())
            if m:
                sys_name, defsys_name = m.group(1), m.group(2)
                system_instances.append((sys_name, defsys_name))

        define_system_counter = 0
        current_sys_name = None
        inside_defsys = False
        inside_context = False
        current_context_sys = None

        declared_vars = set()
        used_vars = set()
        output_lines = []
        line_sys_context = []

        for i, line in enumerate(lines):
            line_strip = line.strip()

            if begin_context_re.match(line_strip):
                inside_context = True
                current_context_sys = begin_context_re.match(line_strip).group(1)
                output_lines.append(line)
                line_sys_context.append(None)
                continue

            if end_context_re.match(line_strip):
                inside_context = False
                current_context_sys = None
                output_lines.append(line)
                line_sys_context.append(None)
                continue

            if line_strip.startswith("*DefineSystem"):
                m = define_system_re.match(line_strip)
                current_defsys = m.group(1) if m else None
                inside_defsys = True
                current_sys_name = (
                    system_instances[define_system_counter][0]
                    if define_system_counter < len(system_instances)
                    else current_defsys
                )
                define_system_counter += 1
                output_lines.append(line)
                line_sys_context.append(None)
                continue

            if line_strip.startswith("*EndDefine"):
                inside_defsys = False
                current_sys_name = None
                output_lines.append(line)
                line_sys_context.append(None)
                continue

            sys_prefix = current_sys_name if inside_defsys else None
            if inside_context and current_context_sys:
                sys_prefix = current_context_sys

            line_sys_context.append(sys_prefix)

            is_decl_line = any(line_strip.startswith(dt) for dt in decl_types)

            quote_pattern = re.compile(r'(\".*?\"|\'.*?\')')
            quoted_spans = [(m.start(), m.end()) for m in quote_pattern.finditer(line)]

            def inside_quotes(pos):
                return any(start <= pos < end for start, end in quoted_spans)

            new_line = ""
            last_pos = 0
            tokens = list(var_regex.finditer(line))

            keyword_match = re.match(r"\*\w+", line_strip)
            keyword_len = len(keyword_match.group(0)) if keyword_match else 0
            first_var_pos = line.find(line_strip) + keyword_len + 1

            for tok in tokens:
                start, end = tok.start(), tok.end()
                var_name = tok.group(1)

                if inside_quotes(start) or start < first_var_pos or var_name in skip_words:
                    continue

                before = line[max(0, start - 20):start]
                if re.search(r'\bMODEL(\.\w+)*\.$', before):
                    continue

                new_line += line[last_pos:start]

                qname = f"MODEL.{sys_prefix}.{var_name}" if sys_prefix else f"MODEL.{var_name}"

                if is_decl_line:
                    declared_vars.add(qname)
                else:
                    if not set_line_re.match(line_strip):
                        used_vars.add(qname)

                new_line += qname
                last_pos = end

            new_line += line[last_pos:]
            output_lines.append(new_line)

        unused_vars = declared_vars - used_vars
        unused_indexes = set()
        final_lines = []

        for i, line in enumerate(output_lines):
            stripped = line.strip()
            is_unused = False

            if any(stripped.startswith(dt) for dt in decl_types):
                m = re.search(r'\bMODEL(?:\.\w+)+\b', line)
                if m and m.group(0) in unused_vars:
                    unused_indexes.add(i)
                    is_unused = True

            elif set_line_re.match(stripped):
                tokens = var_regex.findall(line)
                current_sys_prefix = line_sys_context[i]
                for tok in tokens:
                    if tok in skip_words:
                        continue

                    if current_sys_prefix:
                        scoped_qname = f"MODEL.{current_sys_prefix}.{tok}"
                    else:
                        scoped_qname = f"MODEL.{tok}"

                    if scoped_qname in unused_vars:
                        unused_indexes.add(i)
                        is_unused = True
                        break

            if not is_unused:
                final_lines.append(line)

        return final_lines, unused_indexes

    def highlight_unused_lines(self, editor, unused_line_indexes):
        editor.blockSignals(True)  # Stop repainting during formatting
        doc = editor.document()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("red"))
        fmt.setFontWeight(QFont.Weight.Bold)

        for line_idx in unused_line_indexes:
            block = doc.findBlockByNumber(line_idx)
            if block.isValid():
                cursor = QTextCursor(block)
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                cursor.mergeCharFormat(fmt)

        editor.blockSignals(False)  # Resume updates
        editor.viewport().update()  # Force a repaint


if __name__ == "__main__":
    app = QApplication(sys.argv)
    analyzer = MDLAnalyzer()
    analyzer.show()
    sys.exit(app.exec())
