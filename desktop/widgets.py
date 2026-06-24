from PyQt5.QtWidgets import QTableWidgetItem


class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except (ValueError, TypeError):
            return super().__lt__(other)


def try_parse_number(value):
    """Пробует преобразовать значение в int или float. None если не число."""
    if value is None or value == "":
        return None
    try:
        s = str(value)
        if '.' in s or 'e' in s.lower():
            return float(s)
        return int(s)
    except (ValueError, TypeError):
        return None


# def populate_table(table, data, column_names=None):
#     """Заполняет QTableWidget данными из списка словарей."""
#     table.setSortingEnabled(False)
#     table.clear()
#     table.setRowCount(0)
#     table.setColumnCount(0)

#     if not data:
#         table.setColumnCount(1)
#         table.setHorizontalHeaderLabels(["Нет данных"])
#         table.setSortingEnabled(True)
#         return

#     sample = data[0]
#     columns = [k for k in sample.keys() if k != 'id']
#     headers = [column_names.get(c, c) if column_names else c for c in columns]
#     table.setColumnCount(len(columns))
#     table.setHorizontalHeaderLabels(headers)
#     table.setRowCount(len(data))

#     for i, item in enumerate(data):
#         for j, col in enumerate(columns):
#             value = item.get(col, "")
#             numeric_value = try_parse_number(value)
#             if numeric_value is not None:
#                 if isinstance(numeric_value, float):
#                     table_item = NumericTableWidgetItem(f"{numeric_value:.2f}")
#                 else:
#                     table_item = NumericTableWidgetItem(str(numeric_value))
#             else:
#                 table_item = QTableWidgetItem(str(value))
#             table.setItem(i, j, table_item)

#     table.setSortingEnabled(True)
#     table.resizeColumnsToContents()

def populate_table(table, data, column_names=None):
    table.setSortingEnabled(False)
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(0)

    if not data:
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Нет данных"])
        table.setSortingEnabled(True)
        return

    # Порядок колонок — из column_names, если передан
    if column_names:
        columns = list(column_names.keys())
    else:
        sample = data[0]
        columns = [k for k in sample.keys() if k != 'id']

    headers = [column_names.get(c, c) if column_names else c for c in columns]
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(data))

    for i, item in enumerate(data):
        for j, col in enumerate(columns):
            value = item.get(col, "")
            numeric_value = try_parse_number(value)
            if numeric_value is not None:
                if isinstance(numeric_value, float):
                    table_item = NumericTableWidgetItem(f"{numeric_value:.2f}")
                else:
                    table_item = NumericTableWidgetItem(str(numeric_value))
            else:
                table_item = QTableWidgetItem(str(value))
            table.setItem(i, j, table_item)

    table.setSortingEnabled(True)
    table.resizeColumnsToContents()


def save_table_to_file(parent, table, default_name):
    from PyQt5.QtWidgets import QFileDialog, QMessageBox
    import os

    filepath, _ = QFileDialog.getSaveFileName(
        parent, "Сохранить отчёт",
        os.path.expanduser(f"~\\Desktop\\{default_name}.txt"),
        "Текстовые файлы (*.txt);;CSV (*.csv)"
    )
    if not filepath:
        return

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            headers = [table.horizontalHeaderItem(j).text() for j in range(table.columnCount())]
            f.write('\t'.join(headers) + '\n')
            for i in range(table.rowCount()):
                row = [table.item(i, j).text() if table.item(i, j) else '' for j in range(table.columnCount())]
                f.write('\t'.join(row) + '\n')
        QMessageBox.information(parent, "Готово", f"Отчёт сохранён:\n{filepath}")
    except Exception as e:
        QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить: {e}")

def save_report(parent, title, table, summary_rows=None, params=None):
    """Сохраняет отчёт в текстовый файл с заголовком, таблицей и итогами."""
    from PyQt5.QtWidgets import QFileDialog, QMessageBox
    from datetime import datetime
    import os

    filepath, _ = QFileDialog.getSaveFileName(
        parent, "Сохранить отчёт",
        os.path.expanduser(f"~\\Desktop\\{title}.txt"),
        "Текстовые файлы (*.txt);;CSV (*.csv)"
    )
    if not filepath:
        return

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Шапка
            f.write(f"{'=' * 60}\n")
            f.write(f"  {title}\n")
            f.write(f"  Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            if params:
                for key, value in params.items():
                    f.write(f"  {key}: {value}\n")
            f.write(f"{'=' * 60}\n\n")

            # Таблица
            if table.rowCount() > 0:
                headers = [table.horizontalHeaderItem(j).text() for j in range(table.columnCount())]
                col_widths = [len(h) for h in headers]

                for i in range(table.rowCount()):
                    for j in range(table.columnCount()):
                        text = table.item(i, j).text() if table.item(i, j) else ''
                        col_widths[j] = max(col_widths[j], len(text))

                header_line = ' | '.join(h.ljust(col_widths[k]) for k, h in enumerate(headers))
                f.write(header_line + '\n')
                f.write('-' * len(header_line) + '\n')

                for i in range(table.rowCount()):
                    row = [table.item(i, j).text() if table.item(i, j) else '' for j in range(table.columnCount())]
                    f.write(' | '.join(v.ljust(col_widths[k]) for k, v in enumerate(row)) + '\n')

            # Итоги
            if summary_rows:
                f.write('\n' + '-' * 60 + '\n')
                for row in summary_rows:
                    f.write(f"  {row}\n")
                f.write('=' * 60 + '\n')

        QMessageBox.information(parent, "Готово", f"Отчёт сохранён:\n{filepath}")
    except Exception as e:
        QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить: {e}")