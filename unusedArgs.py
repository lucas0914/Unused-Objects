import sys
import os
import re
import base64
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QFileDialog,
    QListWidget, QHBoxLayout, QMessageBox, QListWidgetItem, QSizePolicy
)
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize


class MDLAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDL Analyzer")
        self.setMinimumSize(1200, 700)

        self.button_open = QPushButton("Open Directory")

        check_all_png_base64 = b'''
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
'''
        uncheck_all_png_base64 = b'''
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
cNiN/wFuHqwWHXCItQAAAABJRU5ErkJggg==
'''
        open_folder_png_base64 = b'''
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
'''
        remove_save_png_base64 =b'''
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
'''

        def icon_from_base64(b64data):
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(b64data))
            return QIcon(pixmap)

        self.button_check_all = QPushButton()
        self.button_check_all.setIcon(icon_from_base64(check_all_png_base64))
        self.button_check_all.setIconSize(QSize(24, 24))
        self.button_check_all.setFixedSize(30, 30)
        self.button_check_all.setFlat(True)

        self.button_uncheck_all = QPushButton()
        self.button_uncheck_all.setIcon(icon_from_base64(uncheck_all_png_base64))
        self.button_uncheck_all.setIconSize(QSize(24, 24))
        self.button_uncheck_all.setFixedSize(30, 30)
        self.button_uncheck_all.setFlat(True)

        self.button_open = QPushButton()
        self.button_open.setIcon(icon_from_base64(open_folder_png_base64))
        self.button_open.setIconSize(QSize(24, 24))
        self.button_open.setFixedSize(30, 30)
        self.button_open.setFlat(True)
        self.button_open.setToolTip("Open Directory")

        self.button_clean = QPushButton()
        self.button_clean.setIcon(icon_from_base64(remove_save_png_base64))
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

        # Create layout for the buttons stacked vertically on the left
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.addWidget(self.button_open)
        left_buttons_layout.addWidget(self.button_check_all)
        left_buttons_layout.addWidget(self.button_uncheck_all)
        left_buttons_layout.addStretch()  # Push buttons to top

        # Combine buttons and file list horizontally
        file_list_layout = QHBoxLayout()
        file_list_layout.addLayout(left_buttons_layout)
        file_list_layout.addWidget(self.file_list)

        # Right side: editors stacked vertically with the clean button at the bottom right
        right_side_layout = QVBoxLayout()
        right_side_layout.addWidget(text_edit_widget)  # editors fill all vertical space
        right_side_layout.addWidget(self.button_clean, alignment=Qt.AlignmentFlag.AlignRight)

        # Main layout: left side with files/buttons, right side with editors + clean button
        main_layout = QHBoxLayout()
        main_layout.addLayout(file_list_layout)
        main_layout.addLayout(right_side_layout)

        self.setLayout(main_layout)

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

        for file in os.listdir(dir_path):
            if file.endswith(".mdl"):
                full_path = os.path.join(dir_path, file)
                with open(full_path, "r") as f:
                    content = f.readlines()
                _, unused = self.process_mdl(content)
                if unused:
                    item = QListWidgetItem(full_path)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.file_list.addItem(item)
                    self.original_lines_map[full_path] = content

        self.button_clean.setEnabled(True)

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
        skip_words = {'true', 'false', 'TRANS', 'P_Global_Origin', 'B_Ground'}

        system_instances = []
        for line in lines:
            m = system_line_re.match(line.strip())
            if m:
                sys_name, defsys_name = m.group(1), m.group(2)
                system_instances.append((sys_name, defsys_name))

        define_system_counter = 0
        current_sys_name = None
        inside_defsys = False

        declared_vars = set()
        used_vars = set()
        output_lines = []

        for line in lines:
            line_strip = line.strip()

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
                continue

            if line_strip.startswith("*EndDefine"):
                inside_defsys = False
                current_sys_name = None
                output_lines.append(line)
                continue

            if line_strip.startswith("*System") or set_line_re.match(line_strip):
                output_lines.append(line)
                continue

            sys_prefix = current_sys_name if inside_defsys else None
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

                if line[max(0, start - 6):start] == "MODEL.":
                    continue

                new_line += line[last_pos:start]
                qname = f"MODEL.{sys_prefix}.{var_name}" if sys_prefix else f"MODEL.{var_name}"
                if is_decl_line:
                    declared_vars.add(qname)
                else:
                    used_vars.add(qname)

                new_line += qname
                last_pos = end

            new_line += line[last_pos:]
            output_lines.append(new_line)

        unused_vars = declared_vars - used_vars
        final_lines = []
        unused_indexes = set()

        for i, line in enumerate(output_lines):
            if any(line.strip().startswith(dt) for dt in decl_types):
                m = re.search(r'MODEL(?:\.\w+)+', line)
                if m and m.group(0) in unused_vars:
                    unused_indexes.add(i)
            final_lines.append(line)

        return final_lines, unused_indexes

    def highlight_unused_lines(self, editor, unused_line_indexes):
        cursor = editor.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("red"))
        fmt.setFontWeight(QFont.Weight.Bold)

        for line_idx in unused_line_indexes:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(line_idx):
                cursor.movePosition(QTextCursor.MoveOperation.Down)

            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.mergeCharFormat(fmt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    analyzer = MDLAnalyzer()
    analyzer.show()
    sys.exit(app.exec())
