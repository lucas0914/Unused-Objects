import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QFileDialog,
    QListWidget, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QFont
from PyQt6.QtCore import Qt


class MDLAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDL Analyzer")
        self.setMinimumSize(1200, 700)

        self.button_open = QPushButton("Open Directory")
        self.button_check_all = QPushButton("Check All")
        self.button_uncheck_all = QPushButton("Uncheck All")
        self.button_clean = QPushButton("Remove Unused and Save")
        self.button_clean.setEnabled(False)

        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(300)

        self.text_edit_original = QTextEdit()
        self.text_edit_cleaned = QTextEdit()

        for editor in (self.text_edit_original, self.text_edit_cleaned):
            editor.setFont(QFont("Courier New", 10))
            editor.setReadOnly(True)
            editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.button_open)
        top_layout.addWidget(self.button_check_all)
        top_layout.addWidget(self.button_uncheck_all)
        top_layout.addWidget(self.button_clean)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_list)

        text_layout = QHBoxLayout()
        text_layout.addWidget(self.text_edit_original)
        text_layout.addWidget(self.text_edit_cleaned)

        file_layout.addLayout(text_layout)

        layout.addLayout(top_layout)
        layout.addLayout(file_layout)
        self.setLayout(layout)

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
