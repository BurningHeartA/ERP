# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
#     QFormLayout, QComboBox, QDateEdit, QTimeEdit,
#     QDoubleSpinBox, QMessageBox
# )
# from PyQt5.QtCore import Qt, QDate, QTime
# from widgets import populate_table, save_report


# class OperationsModule(QWidget):
#     COLUMN_NAMES = {
#         'equipment_name': 'Оборудование',
#         'operation_type_name': 'Тип операции',
#         'employee_name': 'Сотрудник',
#         'order_id': 'Заказ',
#         'start_time': 'Начало',
#         'end_time': 'Конец',
#         'duration_hours': 'Длит. (ч)',
#         'meter_reading': 'Показания',
#     }

#     def __init__(self, api_client):
#         super().__init__()
#         self.api = api_client
#         self.current_data = []
#         self.equipment_list = []
#         self.employees = []
#         self.operation_types = []
#         self.orders_list = []
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(16, 16, 16, 16)

#         title = QLabel("Операции на оборудовании")
#         title.setStyleSheet("font-size: 18px; font-weight: bold;")
#         layout.addWidget(title)

#         btn_layout = QHBoxLayout()
#         btn_add = QPushButton("+ Добавить")
#         btn_add.clicked.connect(self.add_operation)
#         btn_edit = QPushButton("Редактировать")
#         btn_edit.clicked.connect(self.edit_operation)
#         btn_delete = QPushButton("Удалить")
#         btn_delete.clicked.connect(self.delete_operation)

#         btn_equip = QPushButton("Доступное оборудование")
#         btn_equip.clicked.connect(self.show_available_equipment)
#         btn_load = QPushButton("Загрузка")
#         btn_load.clicked.connect(self.show_load_report)
#         btn_types = QPushButton("Виды операций")
#         btn_types.clicked.connect(self.show_types_report)

#         btn_layout.addWidget(btn_add)
#         btn_layout.addWidget(btn_edit)
#         btn_layout.addWidget(btn_delete)
#         btn_layout.addStretch()
#         btn_layout.addWidget(btn_equip)
#         btn_layout.addWidget(btn_load)
#         btn_layout.addWidget(btn_types)
#         layout.addLayout(btn_layout)

#         self.table = QTableWidget()
#         self.table.setEditTriggers(QTableWidget.NoEditTriggers)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.horizontalHeader().setStretchLastSection(True)
#         layout.addWidget(self.table)

#         self._load_dictionaries()
#         self.load_data()

#     def _load_dictionaries(self):
#         resp = self.api.get("equipment/")
#         if resp.status_code == 200:
#             self.equipment_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

#         resp = self.api.get("employees/")
#         if resp.status_code == 200:
#             self.employees = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

#         resp = self.api.get("operation-types/")
#         if resp.status_code == 200:
#             self.operation_types = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

#         resp = self.api.get("orders/")
#         if resp.status_code == 200:
#             self.orders_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

#     def load_data(self):
#         resp = self.api.get("operations/")
#         if resp.status_code == 200:
#             raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
#             allowed = set(self.COLUMN_NAMES.keys()) | {'id'}
#             self.current_data = []
#             for item in raw:
#                 item['equipment_name'] = item.get('equipment_name', '')
#                 item['operation_type_name'] = item.get('operation_type_name', '')
#                 item['employee_name'] = item.get('employee_name', '')
#                 item['duration_hours'] = item.get('duration_hours', '')
#                 item['meter_reading'] = item.get('meter_reading', '')
#                 # Заказ
#                 order_id = item.get('order')
#                 if order_id:
#                     order_info = next((o for o in self.orders_list if o.get('id') == order_id), None)
#                     if order_info:
#                         item['order_id'] = f"Заказ №{order_id} — {order_info.get('product_name', '')}"
#                     else:
#                         item['order_id'] = f"Заказ №{order_id}"
#                 else:
#                     item['order_id'] = '—'
#                 # Время — только часы:минуты
#                 item['start_time'] = self._format_time(item.get('start_time', ''))
#                 item['end_time'] = self._format_time(item.get('end_time', ''))
#                 filtered = {k: v for k, v in item.items() if k in allowed}
#                 self.current_data.append(filtered)
#             populate_table(self.table, self.current_data, self.COLUMN_NAMES)
#         else:
#             QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")

#     def _format_time(self, datetime_str):
#         if not datetime_str:
#             return ''
#         try:
#             t_pos = datetime_str.index('T')
#             return datetime_str[t_pos + 1:t_pos + 6]
#         except (ValueError, IndexError):
#             return datetime_str

#     def get_selected_id(self):
#         row = self.table.currentRow()
#         if row < 0:
#             QMessageBox.warning(self, "Ошибка", "Выберите запись")
#             return None
#         return self.current_data[row].get('id')

#     def add_operation(self):
#         dialog = OperationDialog(self.api, self.equipment_list, self.employees,
#                                  self.operation_types, self.orders_list)
#         if dialog.exec_() == QDialog.Accepted:
#             self.load_data()

#     def edit_operation(self):
#         op_id = self.get_selected_id()
#         if not op_id:
#             return
#         dialog = OperationDialog(self.api, self.equipment_list, self.employees,
#                                  self.operation_types, self.orders_list, op_id)
#         if dialog.exec_() == QDialog.Accepted:
#             self.load_data()

#     def delete_operation(self):
#         op_id = self.get_selected_id()
#         if not op_id:
#             return
#         reply = QMessageBox.question(self, "Подтверждение", "Удалить операцию?",
#                                      QMessageBox.Yes | QMessageBox.No)
#         if reply == QMessageBox.Yes:
#             resp = self.api.delete(f"operations/{op_id}/")
#             if resp.status_code == 204:
#                 self.load_data()
#             else:
#                 QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")

#     def show_available_equipment(self):
#         resp = self.api.get("reports/equipment-load/")
#         if resp.status_code == 200:
#             data = resp.json()
#             dialog = QDialog(self)
#             dialog.setWindowTitle("Доступное оборудование")
#             dialog.setMinimumSize(400, 300)
#             layout = QVBoxLayout(dialog)
#             table = QTableWidget()
#             table.setEditTriggers(QTableWidget.NoEditTriggers)
#             table.setColumnCount(2)
#             table.setHorizontalHeaderLabels(["Оборудование", "Операций"])
#             table.horizontalHeader().setStretchLastSection(True)
#             table.setRowCount(len(data))
#             for i, item in enumerate(data):
#                 table.setItem(i, 0, QTableWidgetItem(str(item.get('name', ''))))
#                 table.setItem(i, 1, QTableWidgetItem(str(item.get('operations', 0))))
#             btn_save = QPushButton("Сохранить отчёт")
#             btn_save.clicked.connect(lambda: save_report(
#                 self, "Доступное оборудование", table,
#                 summary_rows=[f"Всего единиц: {len(data)}"]
#             ))
#             layout.addWidget(table)
#             layout.addWidget(btn_save)
#             dialog.exec_()

#     def show_load_report(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Загрузка оборудования")
#         dialog.setMinimumSize(400, 300)
#         layout = QVBoxLayout(dialog)
#         table = QTableWidget()
#         table.setEditTriggers(QTableWidget.NoEditTriggers)
#         table.setColumnCount(2)
#         table.setHorizontalHeaderLabels(["Оборудование", "Кол-во операций"])
#         table.horizontalHeader().setStretchLastSection(True)

#         resp = self.api.get("reports/equipment-load/")
#         if resp.status_code == 200:
#             data = resp.json()
#             table.setRowCount(len(data))
#             for i, item in enumerate(data):
#                 table.setItem(i, 0, QTableWidgetItem(str(item.get('name', ''))))
#                 table.setItem(i, 1, QTableWidgetItem(str(item.get('operations', 0))))
        
#         btn_save = QPushButton("Сохранить отчёт")
#         btn_save.clicked.connect(lambda: save_report(
#             self, "Загрузка оборудования", table,
#             summary_rows=[f"Всего единиц: {table.rowCount()}"]
#         ))
#         layout.addWidget(table)
#         layout.addWidget(btn_save)
#         dialog.exec_()

#     def show_types_report(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Виды операций")
#         dialog.setMinimumSize(400, 300)
#         layout = QVBoxLayout(dialog)
#         table = QTableWidget()
#         table.setEditTriggers(QTableWidget.NoEditTriggers)
#         table.setColumnCount(2)
#         table.setHorizontalHeaderLabels(["Тип операции", "Кол-во"])
#         table.horizontalHeader().setStretchLastSection(True)

#         resp = self.api.get("operations/")
#         if resp.status_code == 200:
#             raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
#             # Группировка по типам
#             from collections import Counter
#             counts = Counter(op.get('operation_type_name', 'Неизвестно') for op in raw)
#             table.setRowCount(len(counts))
#             for i, (name, count) in enumerate(counts.items()):
#                 table.setItem(i, 0, QTableWidgetItem(str(name)))
#                 table.setItem(i, 1, QTableWidgetItem(str(count)))

#         btn_save = QPushButton("Сохранить отчёт")
#         btn_save.clicked.connect(lambda: save_report(
#             self, "Виды операций", table,
#             summary_rows=[f"Всего операций: {sum(1 for _ in raw) if 'raw' in dir() else table.rowCount()}"]
#         ))
#         layout.addWidget(table)
#         layout.addWidget(btn_save)
#         dialog.exec_()


# class OperationDialog(QDialog):
#     def __init__(self, api_client, equipment, employees, op_types, orders, op_id=None):
#         super().__init__()
#         self.api = api_client
#         self.equipment = equipment
#         self.employees = employees
#         self.op_types = op_types
#         self.orders = orders
#         self.op_id = op_id
#         self.setWindowTitle("Редактирование операции" if op_id else "Новая операция")
#         self.setMinimumWidth(450)
#         self.init_ui()
#         if op_id:
#             self._load_operation()

#     def init_ui(self):
#         layout = QVBoxLayout()
#         form = QFormLayout()

#         self.equipment_combo = QComboBox()
#         for e in self.equipment:
#             self.equipment_combo.addItem(e.get('name', ''), e.get('id'))
#         form.addRow("Оборудование", self.equipment_combo)

#         self.type_combo = QComboBox()
#         for t in self.op_types:
#             self.type_combo.addItem(t.get('name', ''), t.get('id'))
#         form.addRow("Тип операции", self.type_combo)

#         self.employee_combo = QComboBox()
#         for emp in self.employees:
#             self.employee_combo.addItem(
#                 f"{emp.get('full_name', '')} — {emp.get('position_name', '')}",
#                 emp.get('id')
#             )
#         form.addRow("Сотрудник", self.employee_combo)

#         self.order_combo = QComboBox()
#         self.order_combo.addItem("— Без заказа —", None)
#         for o in self.orders:
#             self.order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
#         form.addRow("Заказ", self.order_combo)

#         self.date = QDateEdit()
#         self.date.setCalendarPopup(True)
#         self.date.setDate(QDate.currentDate())
#         form.addRow("Дата", self.date)

#         self.start_time = QTimeEdit()
#         self.start_time.setTime(QTime(8, 0))
#         form.addRow("Начало", self.start_time)

#         self.end_time = QTimeEdit()
#         self.end_time.setTime(QTime(12, 0))
#         form.addRow("Конец", self.end_time)

#         self.meter = QDoubleSpinBox()
#         self.meter.setMaximum(999999)
#         self.meter.setDecimals(2)
#         form.addRow("Показания счётчика", self.meter)

#         layout.addLayout(form)
#         btn_save = QPushButton("Сохранить")
#         btn_save.clicked.connect(self.save)
#         layout.addWidget(btn_save)
#         self.setLayout(layout)

#     def _load_operation(self):
#         resp = self.api.get(f"operations/{self.op_id}/")
#         if resp.status_code != 200:
#             return
#         data = resp.json()
#         idx = self.equipment_combo.findData(data.get('equipment'))
#         if idx >= 0:
#             self.equipment_combo.setCurrentIndex(idx)
#         idx = self.type_combo.findData(data.get('operation_type'))
#         if idx >= 0:
#             self.type_combo.setCurrentIndex(idx)
#         idx = self.employee_combo.findData(data.get('employee'))
#         if idx >= 0:
#             self.employee_combo.setCurrentIndex(idx)
#         if data.get('order'):
#             idx = self.order_combo.findData(data.get('order'))
#             if idx >= 0:
#                 self.order_combo.setCurrentIndex(idx)
#         if data.get('start_time'):
#             dt = data['start_time']
#             self.date.setDate(QDate.fromString(dt[:10], 'yyyy-MM-dd'))
#             self.start_time.setTime(QTime.fromString(dt[11:16], 'HH:mm'))
#         if data.get('end_time'):
#             self.end_time.setTime(QTime.fromString(data['end_time'][11:16], 'HH:mm'))
#         self.meter.setValue(float(data.get('meter_reading', 0) or 0))

#     def save(self):
#         shift_date = self.date.date().toString('yyyy-MM-dd')
#         data = {
#             'equipment': self.equipment_combo.currentData(),
#             'operation_type': self.type_combo.currentData(),
#             'employee': self.employee_combo.currentData(),
#             'order': self.order_combo.currentData(),
#             'start_time': f"{shift_date}T{self.start_time.time().toString('HH:mm')}:00",
#             'end_time': f"{shift_date}T{self.end_time.time().toString('HH:mm')}:00",
#             'meter_reading': self.meter.value() if self.meter.value() > 0 else None,
#         }
#         if self.op_id:
#             resp = self.api.put(f"operations/{self.op_id}/", data)
#         else:
#             resp = self.api.post("operations/", data)
#         if resp.status_code in [200, 201]:
#             self.accept()
#         else:
#             QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")


from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QDateEdit, QTimeEdit,
    QDoubleSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QTime
from widgets import populate_table, save_report


class OperationsModule(QWidget):
    COLUMN_NAMES = {
        'equipment_name': 'Оборудование',
        'operation_type_name': 'Тип операции',
        'employee_name': 'Сотрудник',
        'order_id': 'Заказ',
        'start_time': 'Начало',
        'end_time': 'Конец',
        'duration_hours': 'Длит. (ч)',
        'meter_reading': 'Показания',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.equipment_list = []
        self.employees = []
        self.operation_types = []
        self.orders_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Операции на оборудовании")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_add.clicked.connect(self.add_operation)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_operation)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_operation)

        btn_load = QPushButton("Загрузка")
        btn_load.clicked.connect(self.show_load_report)
        btn_types = QPushButton("Виды операций")
        btn_types.clicked.connect(self.show_types_report)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_load)
        btn_layout.addWidget(btn_types)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self._load_dictionaries()
        self.load_data()

    def _load_dictionaries(self):
        resp = self.api.get("equipment/")
        if resp.status_code == 200:
            self.equipment_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("employees/")
        if resp.status_code == 200:
            self.employees = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("operation-types/")
        if resp.status_code == 200:
            self.operation_types = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("orders/")
        if resp.status_code == 200:
            self.orders_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

    def load_data(self):
        resp = self.api.get("operations/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            allowed = set(self.COLUMN_NAMES.keys()) | {'id'}
            self.current_data = []
            for item in raw:
                item['equipment_name'] = item.get('equipment_name', '')
                item['operation_type_name'] = item.get('operation_type_name', '')
                item['employee_name'] = item.get('employee_name', '')
                item['duration_hours'] = item.get('duration_hours', '')
                item['meter_reading'] = item.get('meter_reading', '')
                order_id = item.get('order')
                if order_id:
                    order_info = next((o for o in self.orders_list if o.get('id') == order_id), None)
                    item['order_id'] = f"Заказ №{order_id} — {order_info.get('product_name', '')}" if order_info else f"Заказ №{order_id}"
                else:
                    item['order_id'] = '—'
                item['start_time'] = self._format_time(item.get('start_time', ''))
                item['end_time'] = self._format_time(item.get('end_time', ''))
                filtered = {k: v for k, v in item.items() if k in allowed}
                self.current_data.append(filtered)
            populate_table(self.table, self.current_data, self.COLUMN_NAMES)
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")

    def _format_time(self, datetime_str):
        if not datetime_str:
            return ''
        try:
            t_pos = datetime_str.index('T')
            return datetime_str[t_pos + 1:t_pos + 6]
        except (ValueError, IndexError):
            return datetime_str

    def _get_period(self, title):
        """Диалог выбора периода. Возвращает (start_date, end_date) или (None, None)."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedWidth(300)
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

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return None
        return self.current_data[row].get('id')

    def add_operation(self):
        dialog = OperationDialog(self.api, self.equipment_list, self.employees,
                                 self.operation_types, self.orders_list)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_operation(self):
        op_id = self.get_selected_id()
        if not op_id:
            return
        dialog = OperationDialog(self.api, self.equipment_list, self.employees,
                                 self.operation_types, self.orders_list, op_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def delete_operation(self):
        op_id = self.get_selected_id()
        if not op_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить операцию?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.delete(f"operations/{op_id}/")
            if resp.status_code == 204:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")

    def show_load_report(self):
        start_date, end_date = self._get_period("Загрузка оборудования")
        if not start_date:
            return

        resp = self.api.get("operations/")
        if resp.status_code != 200:
            return
        raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        # Фильтруем по дате
        filtered = [op for op in raw if op.get('start_time', '')[:10] >= start_date
                    and op.get('start_time', '')[:10] <= end_date]

        # Группировка по оборудованию
        from collections import defaultdict
        equip_data = defaultdict(lambda: {'count': 0, 'hours': 0.0})
        total_hours = 0.0
        for op in filtered:
            eq_name = op.get('equipment_name', 'Неизвестно')
            dur = float(op.get('duration_hours', 0) or 0)
            equip_data[eq_name]['count'] += 1
            equip_data[eq_name]['hours'] += dur
            total_hours += dur

        dialog = QDialog(self)
        dialog.setWindowTitle("Загрузка оборудования")
        dialog.setMinimumSize(500, 300)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Оборудование", "Операций", "% времени"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(len(equip_data))

        for i, (name, d) in enumerate(sorted(equip_data.items())):
            table.setItem(i, 0, QTableWidgetItem(name))
            table.setItem(i, 1, QTableWidgetItem(str(d['count'])))
            pct = (d['hours'] / total_hours * 100) if total_hours > 0 else 0
            table.setItem(i, 2, QTableWidgetItem(f"{pct:.1f}%"))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Загрузка оборудования", table,
            summary_rows=[
                f"Период: {start_date} — {end_date}",
                f"Всего операций: {len(filtered)}",
                f"Общее машинное время: {total_hours:.1f} ч",
            ],
            params={"Период": f"{start_date} — {end_date}"}
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()

    def show_types_report(self):
        start_date, end_date = self._get_period("Виды операций")
        if not start_date:
            return

        resp = self.api.get("operations/")
        if resp.status_code != 200:
            return
        raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        # Фильтруем по дате
        filtered = [op for op in raw if op.get('start_time', '')[:10] >= start_date
                    and op.get('start_time', '')[:10] <= end_date]

        # Группировка по типам
        from collections import defaultdict
        type_data = defaultdict(lambda: {'count': 0, 'hours': 0.0})
        total_hours = 0.0
        for op in filtered:
            type_name = op.get('operation_type_name', 'Неизвестно')
            dur = float(op.get('duration_hours', 0) or 0)
            type_data[type_name]['count'] += 1
            type_data[type_name]['hours'] += dur
            total_hours += dur

        dialog = QDialog(self)
        dialog.setWindowTitle("Виды операций")
        dialog.setMinimumSize(500, 300)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Тип операции", "Операций", "% времени"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(len(type_data))

        for i, (name, d) in enumerate(sorted(type_data.items())):
            table.setItem(i, 0, QTableWidgetItem(name))
            table.setItem(i, 1, QTableWidgetItem(str(d['count'])))
            pct = (d['hours'] / total_hours * 100) if total_hours > 0 else 0
            table.setItem(i, 2, QTableWidgetItem(f"{pct:.1f}%"))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Виды операций", table,
            summary_rows=[
                f"Период: {start_date} — {end_date}",
                f"Всего операций: {len(filtered)}",
                f"Общее машинное время: {total_hours:.1f} ч",
            ],
            params={"Период": f"{start_date} — {end_date}"}
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()


class OperationDialog(QDialog):
    def __init__(self, api_client, equipment, employees, op_types, orders, op_id=None):
        super().__init__()
        self.api = api_client
        self.equipment = equipment
        self.employees = employees
        self.op_types = op_types
        self.orders = orders
        self.op_id = op_id
        self.setWindowTitle("Редактирование операции" if op_id else "Новая операция")
        self.setMinimumWidth(450)
        self.init_ui()
        if op_id:
            self._load_operation()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.equipment_combo = QComboBox()
        for e in self.equipment:
            self.equipment_combo.addItem(e.get('name', ''), e.get('id'))
        form.addRow("Оборудование", self.equipment_combo)

        self.type_combo = QComboBox()
        for t in self.op_types:
            self.type_combo.addItem(t.get('name', ''), t.get('id'))
        form.addRow("Тип операции", self.type_combo)

        self.employee_combo = QComboBox()
        for emp in self.employees:
            self.employee_combo.addItem(
                f"{emp.get('full_name', '')} — {emp.get('position_name', '')}",
                emp.get('id')
            )
        form.addRow("Сотрудник", self.employee_combo)

        self.order_combo = QComboBox()
        self.order_combo.addItem("— Без заказа —", None)
        for o in self.orders:
            self.order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
        form.addRow("Заказ", self.order_combo)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        form.addRow("Дата", self.date)

        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(8, 0))
        form.addRow("Начало", self.start_time)

        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(12, 0))
        form.addRow("Конец", self.end_time)

        self.meter = QDoubleSpinBox()
        self.meter.setMaximum(999999)
        self.meter.setDecimals(2)
        form.addRow("Показания счётчика", self.meter)

        layout.addLayout(form)
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def _load_operation(self):
        resp = self.api.get(f"operations/{self.op_id}/")
        if resp.status_code != 200:
            return
        data = resp.json()
        idx = self.equipment_combo.findData(data.get('equipment'))
        if idx >= 0:
            self.equipment_combo.setCurrentIndex(idx)
        idx = self.type_combo.findData(data.get('operation_type'))
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        idx = self.employee_combo.findData(data.get('employee'))
        if idx >= 0:
            self.employee_combo.setCurrentIndex(idx)
        if data.get('order'):
            idx = self.order_combo.findData(data.get('order'))
            if idx >= 0:
                self.order_combo.setCurrentIndex(idx)
        if data.get('start_time'):
            dt = data['start_time']
            self.date.setDate(QDate.fromString(dt[:10], 'yyyy-MM-dd'))
            self.start_time.setTime(QTime.fromString(dt[11:16], 'HH:mm'))
        if data.get('end_time'):
            self.end_time.setTime(QTime.fromString(data['end_time'][11:16], 'HH:mm'))
        self.meter.setValue(float(data.get('meter_reading', 0) or 0))

    def save(self):
        shift_date = self.date.date().toString('yyyy-MM-dd')
        data = {
            'equipment': self.equipment_combo.currentData(),
            'operation_type': self.type_combo.currentData(),
            'employee': self.employee_combo.currentData(),
            'order': self.order_combo.currentData(),
            'start_time': f"{shift_date}T{self.start_time.time().toString('HH:mm')}:00",
            'end_time': f"{shift_date}T{self.end_time.time().toString('HH:mm')}:00",
            'meter_reading': self.meter.value() if self.meter.value() > 0 else None,
        }
        if self.op_id:
            resp = self.api.put(f"operations/{self.op_id}/", data)
        else:
            resp = self.api.post("operations/", data)
        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")