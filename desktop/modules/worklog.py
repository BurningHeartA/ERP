# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
#     QFormLayout, QLineEdit, QComboBox, QDateEdit,
#     QDoubleSpinBox, QTimeEdit, QMessageBox
# )

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QDateEdit, QTimeEdit, QLineEdit,
    QDoubleSpinBox, QMessageBox
)

from PyQt5.QtCore import Qt, QDate, QTime
from widgets import populate_table, save_report




class WorkLogModule(QWidget):
    COLUMN_NAMES = {
        'employee_name': 'Сотрудник',
        'shift_date': 'Дата',
        'efficiency_score': 'Оценка',
        'comment': 'Комментарий',
        'entries_count': 'Кол-во работ',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.employees = []
        self.categories = []
        self.orders_list = []
        self.init_ui()

    # def init_ui(self):
    #     layout = QVBoxLayout(self)
    #     layout.setContentsMargins(16, 16, 16, 16)

    #     title = QLabel("Табель работ")
    #     title.setStyleSheet("font-size: 18px; font-weight: bold;")
    #     layout.addWidget(title)

    #     btn_layout = QHBoxLayout()
    #     btn_add = QPushButton("+ Добавить смену")
    #     btn_add.clicked.connect(self.add_shift)
    #     btn_edit = QPushButton("Редактировать")
    #     btn_edit.clicked.connect(self.edit_shift)
    #     btn_delete = QPushButton("Удалить")
    #     btn_delete.clicked.connect(self.delete_shift)
    #     btn_layout.addWidget(btn_add)
    #     btn_layout.addWidget(btn_edit)
    #     btn_layout.addWidget(btn_delete)
    #     btn_layout.addStretch()
    #     layout.addLayout(btn_layout)

    #     self.table = QTableWidget()
    #     self.table.setEditTriggers(QTableWidget.NoEditTriggers)
    #     self.table.setSelectionBehavior(QTableWidget.SelectRows)
    #     self.table.horizontalHeader().setStretchLastSection(True)
    #     layout.addWidget(self.table)

    #     self.load_data()

    # def load_data(self):
    #     resp = self.api.get("work-logs/")
    #     if resp.status_code == 200:
    #         raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
    #         allowed = set(self.COLUMN_NAMES.keys()) | {'id'}
    #         self.current_data = []
    #         for item in raw:
    #             # item['entries_count'] = len(item.get('entries', []))
    #             if 'entries' in item:
    #                 item['entries_count'] = len(item['entries'])
    #             else:
    #                 item['entries_count'] = item.get('entries_count', 0)

    #             item['employee_name'] = item.get('employee_name', '')
    #             filtered = {k: v for k, v in item.items() if k in allowed}
    #             self.current_data.append(filtered)
    #         populate_table(self.table, self.current_data, self.COLUMN_NAMES)
    #     else:
    #         QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")


    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Табель работ")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить смену")
        btn_add.clicked.connect(self.add_shift)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_shift)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_shift)
        btn_categories = QPushButton("Категории работ")
        btn_categories.clicked.connect(self.show_categories_report)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_categories)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self._load_dictionaries()
        self.load_data()

    def _load_dictionaries(self):
        resp = self.api.get("employees/")
        if resp.status_code == 200:
            self.employees = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("work-categories/")
        if resp.status_code == 200:
            self.categories = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("orders/")
        if resp.status_code == 200:
            self.orders_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

    def load_data(self):
        resp = self.api.get("work-logs/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            allowed = set(self.COLUMN_NAMES.keys()) | {'id'}
            self.current_data = []
            for item in raw:
                if 'entries' in item:
                    item['entries_count'] = len(item['entries'])
                else:
                    item['entries_count'] = item.get('entries_count', 0)
                item['employee_name'] = item.get('employee_name', '')
                filtered = {k: v for k, v in item.items() if k in allowed}
                self.current_data.append(filtered)
            populate_table(self.table, self.current_data, self.COLUMN_NAMES)
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")


    def _get_period(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите период")
        dialog.setMinimumWidth(500)
        layout = QFormLayout(dialog)
        start = QDateEdit()
        start.setCalendarPopup(True)
        start.setDate(QDate.currentDate().addMonths(-1))
        end = QDateEdit()
        end.setCalendarPopup(True)
        end.setDate(QDate.currentDate())
        layout.addRow("Начальная дата", start)
        layout.addRow("Конечная дата", end)
        btn = QPushButton("Сформировать")
        result = {"start": None, "end": None}

        def on_click():
            result["start"] = start.date().toString('yyyy-MM-dd')
            result["end"] = end.date().toString('yyyy-MM-dd')
            dialog.accept()
        btn.clicked.connect(on_click)
        layout.addRow(btn)
        dialog.exec_()
        return result["start"], result["end"]


    def show_categories_report(self):
        start_date, end_date = self._get_period()
        if not start_date:
            return

        resp = self.api.get("work-logs/")
        if resp.status_code != 200:
            return
        logs = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        # Собираем все записи работ за период
        from collections import defaultdict
        cat_hours = defaultdict(float)
        total_hours = 0.0

        for log in logs:
            if not (start_date <= log.get('shift_date', '') <= end_date):
                continue
            entries = log.get('entries', [])
            for e in entries:
                dur = float(e.get('duration_hours', 0) or 0)
                cat_name = e.get('work_category_name', 'Неизвестно')
                cat_hours[cat_name] += dur
                total_hours += dur

        dialog = QDialog(self)
        dialog.setWindowTitle("Категории работ")
        dialog.setMinimumSize(500, 300)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Категория", "Работ", "Часов", "% времени"])
        table.horizontalHeader().setStretchLastSection(True)

        # Считаем количество работ
        cat_count = defaultdict(int)
        for log in logs:
            if not (start_date <= log.get('shift_date', '') <= end_date):
                continue
            for e in log.get('entries', []):
                cat_name = e.get('work_category_name', 'Неизвестно')
                cat_count[cat_name] += 1

        table.setRowCount(len(cat_hours))
        for i, (name, hours) in enumerate(sorted(cat_hours.items())):
            table.setItem(i, 0, QTableWidgetItem(name))
            table.setItem(i, 1, QTableWidgetItem(str(cat_count.get(name, 0))))
            table.setItem(i, 2, QTableWidgetItem(f"{hours:.1f}"))
            pct = (hours / total_hours * 100) if total_hours > 0 else 0
            table.setItem(i, 3, QTableWidgetItem(f"{pct:.1f}%"))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Категории работ", table,
            summary_rows=[
                f"Период: {start_date} — {end_date}",
                f"Суммарное рабочее время: {total_hours:.1f} ч",
            ],
            params={"Период": f"{start_date} — {end_date}"}
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()


    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return None
        return self.current_data[row].get('id')

    def add_shift(self):
        dialog = WorkLogDialog(self.api)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_shift(self):
        shift_id = self.get_selected_id()
        if not shift_id:
            return
        dialog = WorkLogDialog(self.api, shift_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def delete_shift(self):
        shift_id = self.get_selected_id()
        if not shift_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить смену?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.delete(f"work-logs/{shift_id}/")
            if resp.status_code == 204:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")


class WorkLogDialog(QDialog):
    def __init__(self, api_client, shift_id=None):
        super().__init__()
        self.api = api_client
        self.shift_id = shift_id
        self.employees = []
        self.categories = []
        self.orders_list = []
        self.entries = []  # список словарей для работ
        self.setWindowTitle("Редактирование смены" if shift_id else "Новая смена")
        self.setMinimumWidth(700)
        self.init_ui()
        self._load_dictionaries()
        if shift_id:
            self._load_shift()

    def init_ui(self):
        layout = QVBoxLayout()

        # Основные поля
        form = QFormLayout()
        self.employee_combo = QComboBox()
        form.addRow("Сотрудник", self.employee_combo)

        self.shift_date = QDateEdit()
        self.shift_date.setCalendarPopup(True)
        self.shift_date.setDate(QDate.currentDate())
        form.addRow("Дата смены", self.shift_date)

        self.efficiency = QDoubleSpinBox()
        self.efficiency.setRange(-0.05, 0.05)
        self.efficiency.setDecimals(2)
        self.efficiency.setSingleStep(0.01)
        self.efficiency.setValue(0.0)
        form.addRow("Оценка эффективности", self.efficiency)

        self.comment = QLineEdit()
        form.addRow("Комментарий", self.comment)

        layout.addLayout(form)

        # Мини-таблица работ
        layout.addWidget(QLabel("Работы в смену:"))

        entries_layout = QHBoxLayout()
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(5)
        self.entries_table.setHorizontalHeaderLabels(["Категория", "Заказ", "Начало", "Конец", "Длительность"])
        self.entries_table.horizontalHeader().setStretchLastSection(True)
        entries_layout.addWidget(self.entries_table)

        entry_btn_layout = QVBoxLayout()
        btn_add_entry = QPushButton("+")
        btn_add_entry.clicked.connect(self.add_entry)
        btn_del_entry = QPushButton("–")
        btn_del_entry.clicked.connect(self.remove_entry)
        entry_btn_layout.addWidget(btn_add_entry)
        entry_btn_layout.addWidget(btn_del_entry)
        entry_btn_layout.addStretch()
        entries_layout.addLayout(entry_btn_layout)
        layout.addLayout(entries_layout)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _load_dictionaries(self):
        # Сотрудники
        resp = self.api.get("employees/")
        if resp.status_code == 200:
            self.employees = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            for e in self.employees:
                display = f"{e.get('full_name', '')} — {e.get('position_name', '')}"
                self.employee_combo.addItem(display, e.get('id'))

        # Категории работ
        resp = self.api.get("work-categories/")
        if resp.status_code == 200:
            self.categories = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        # Заказы (для выбора в работе)
        resp = self.api.get("orders/")
        if resp.status_code == 200:
            self.orders_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

    def _load_shift(self):
        resp = self.api.get(f"work-logs/{self.shift_id}/")
        if resp.status_code != 200:
            return
        data = resp.json()

        idx = self.employee_combo.findData(data.get('employee'))
        if idx >= 0:
            self.employee_combo.setCurrentIndex(idx)
        if data.get('shift_date'):
            self.shift_date.setDate(QDate.fromString(data['shift_date'], 'yyyy-MM-dd'))
        self.efficiency.setValue(float(data.get('efficiency_score', 0)))
        self.comment.setText(data.get('comment', ''))

        self.entries = data.get('entries', [])
        self._refresh_entries_table()

    def add_entry(self):
        dialog = WorkEntryDialog(self.categories, self.orders_list)
        if dialog.exec_() == QDialog.Accepted:
            self.entries.append(dialog.get_data())
            self._refresh_entries_table()

    def remove_entry(self):
        row = self.entries_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите работу")
            return
        del self.entries[row]
        self._refresh_entries_table()

    def _format_time(self, datetime_str):
        """Извлекает HH:MM из строки вида '2026-04-15T08:00:00+03:00' или '2026-04-15T08:00:00'."""
        if not datetime_str:
            return ''
        try:
            # Находим T и берём 5 символов после
            t_pos = datetime_str.index('T')
            return datetime_str[t_pos + 1:t_pos + 6]
        except (ValueError, IndexError):
            return datetime_str

    def _refresh_entries_table(self):
        self.entries_table.setRowCount(len(self.entries))
        for i, entry in enumerate(self.entries):
            cat_name = entry.get('work_category_name', entry.get('work_category', ''))
            order_name = entry.get('order_name', entry.get('order', '—'))
            self.entries_table.setItem(i, 0, QTableWidgetItem(str(cat_name)))
            self.entries_table.setItem(i, 1, QTableWidgetItem(str(order_name)))
            self.entries_table.setItem(i, 2, QTableWidgetItem(self._format_time(str(entry.get('start_time', '')))))
            self.entries_table.setItem(i, 3, QTableWidgetItem(self._format_time(str(entry.get('end_time', '')))))
            # Длительность
            dur = entry.get('duration_hours', '')
            self.entries_table.setItem(i, 4, QTableWidgetItem(str(dur) if dur else ''))

    def save(self):
        data = {
            'employee': self.employee_combo.currentData(),
            'shift_date': self.shift_date.date().toString('yyyy-MM-dd'),
            'efficiency_score': self.efficiency.value(),
            'comment': self.comment.text(),
            'entries': [
                {
                    'work_category': e.get('work_category'),
                    'order': e.get('order') or None,
                    'start_time': e.get('start_time'),
                    'end_time': e.get('end_time'),
                }
                for e in self.entries
            ]
        }

        if self.shift_id:
            resp = self.api.put(f"work-logs/{self.shift_id}/", data)
        else:
            resp = self.api.post("work-logs/", data)

        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")


class WorkEntryDialog(QDialog):
    def __init__(self, categories, orders):
        super().__init__()
        self.categories = categories
        self.orders = orders
        self.setWindowTitle("Добавить работу")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.category_combo = QComboBox()
        for c in self.categories:
            self.category_combo.addItem(c.get('name', ''), c.get('id'))
        layout.addRow("Категория", self.category_combo)

        self.order_combo = QComboBox()
        self.order_combo.addItem("— Без заказа —", None)
        for o in self.orders:
            self.order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
        layout.addRow("Заказ", self.order_combo)

        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(8, 0))
        layout.addRow("Начало", self.start_time)

        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(12, 0))
        layout.addRow("Конец", self.end_time)

        btn = QPushButton("Добавить")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

        self.setLayout(layout)

    def get_data(self):
        shift_date = self.parent().shift_date.date().toString('yyyy-MM-dd') if hasattr(self.parent(), 'shift_date') else QDate.currentDate().toString('yyyy-MM-dd')
        return {
            'work_category': self.category_combo.currentData(),
            'order': self.order_combo.currentData(),
            'start_time': f"{shift_date}T{self.start_time.time().toString('HH:mm')}:00",
            'end_time': f"{shift_date}T{self.end_time.time().toString('HH:mm')}:00",
        }