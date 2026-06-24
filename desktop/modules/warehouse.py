from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDoubleSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from widgets import populate_table, save_table_to_file, save_report


class WarehouseModule(QWidget):
    COLUMN_NAMES = {
        'material_name': 'Материал',
        'date': 'Дата',
        'movement_type': 'Тип',
        'order_id': 'Заказ',
        'quantity': 'Количество',
        'unit_price': 'Цена за ед.',
        'total_cost': 'Стоимость',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.materials = []
        self.orders_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Складской учёт")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить запись")
        btn_add.clicked.connect(self.add_record)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_record)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_record)
        btn_balance = QPushButton("Остатки")
        btn_balance.clicked.connect(self.show_balance)
        btn_material_report = QPushButton("Расход по заказу")
        btn_material_report.clicked.connect(self.show_order_materials)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_balance)
        btn_layout.addWidget(btn_material_report)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self._load_dictionaries()
        self.load_data()

    def _load_dictionaries(self):
        resp = self.api.get("materials/")
        if resp.status_code == 200:
            self.materials = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("orders/")
        if resp.status_code == 200:
            self.orders_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

    # def load_data(self):
    #     resp = self.api.get("inventory-records/")
    #     if resp.status_code == 200:
    #         raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
    #         allowed = set(self.COLUMN_NAMES.keys()) | {'id'}
    #         self.current_data = []
    #         for item in raw:
    #             item['material_name'] = item.get('material_name', '')
    #             item['total_cost'] = item.get('total_cost', 0)
    #             item['order_id'] = item.get('order', '—')
    #             if item.get('movement_type') == 'receipt':
    #                 item['movement_type'] = 'Поступление'
    #             elif item.get('movement_type') == 'issue':
    #                 item['movement_type'] = 'Выдача'
    #             filtered = {k: v for k, v in item.items() if k in allowed}
    #             self.current_data.append(filtered)
    #         populate_table(self.table, self.current_data, self.COLUMN_NAMES)
    #     else:
    #         QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")


    def load_data(self):
        resp = self.api.get("inventory-records/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            allowed = set(self.COLUMN_NAMES.keys()) | {'id'}
            self.current_data = []
            for item in raw:
                item['material_name'] = item.get('material_name', '')
                item['total_cost'] = item.get('total_cost', 0)
                # Заказ — строка
                order_id = item.get('order')
                if order_id:
                    order_info = next((o for o in self.orders_list if o.get('id') == order_id), None)
                    if order_info:
                        item['order_id'] = f"Заказ №{order_id} — {order_info.get('product_name', '')}"
                    else:
                        item['order_id'] = f"Заказ №{order_id}"
                else:
                    item['order_id'] = '—'
                if item.get('movement_type') == 'receipt':
                    item['movement_type'] = 'Поступление'
                elif item.get('movement_type') == 'issue':
                    item['movement_type'] = 'Выдача'
                filtered = {k: v for k, v in item.items() if k in allowed}
                self.current_data.append(filtered)
            populate_table(self.table, self.current_data, self.COLUMN_NAMES)
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")


    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return None
        return self.current_data[row].get('id')

    def add_record(self):
        dialog = InventoryDialog(self.api, self.materials, self.orders_list)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_record(self):
        rec_id = self.get_selected_id()
        if not rec_id:
            return
        dialog = InventoryDialog(self.api, self.materials, self.orders_list, rec_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def delete_record(self):
        rec_id = self.get_selected_id()
        if not rec_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить запись?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.delete(f"inventory-records/{rec_id}/")
            if resp.status_code == 204:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")

    # def show_balance(self):
    #     resp = self.api.get("reports/warehouse-balance/")
    #     if resp.status_code == 200:
    #         data = resp.json()
    #         dialog = QDialog(self)
    #         dialog.setWindowTitle("Остатки на складе")
    #         dialog.setMinimumSize(500, 300)
    #         layout = QVBoxLayout(dialog)

    #         table = QTableWidget()
    #         table.setEditTriggers(QTableWidget.NoEditTriggers)
    #         table.setColumnCount(3)
    #         table.setHorizontalHeaderLabels(["Материал", "Остаток", "Стоимость"])
    #         table.horizontalHeader().setStretchLastSection(True)
    #         table.setRowCount(len(data))
    #         for i, item in enumerate(data):
    #             table.setItem(i, 0, QTableWidgetItem(str(item.get('material', ''))))
    #             table.setItem(i, 1, QTableWidgetItem(str(item.get('balance', 0))))
    #             table.setItem(i, 2, QTableWidgetItem(f"{item.get('total_cost', 0):.2f}"))

    #         btn_save = QPushButton("Сохранить отчёт")
    #         btn_save.clicked.connect(lambda: save_table_to_file(self, table, "остатки_на_складе"))
    #         layout.addWidget(table)
    #         layout.addWidget(btn_save)
    #         dialog.exec_()
    #     else:
    #         QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")

    def show_balance(self):
        resp = self.api.get("reports/warehouse-balance/")
        if resp.status_code == 200:
            data = resp.json()
            dialog = QDialog(self)
            dialog.setWindowTitle("Остатки на складе")
            dialog.setMinimumSize(500, 300)
            layout = QVBoxLayout(dialog)

            table = QTableWidget()
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Материал", "Остаток", "Стоимость"])
            table.horizontalHeader().setStretchLastSection(True)
            table.setRowCount(len(data))
            
            total_cost = 0
            for i, item in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(str(item.get('material', ''))))
                table.setItem(i, 1, QTableWidgetItem(str(item.get('balance', 0))))
                cost = item.get('total_cost', 0)
                total_cost += cost
                table.setItem(i, 2, QTableWidgetItem(f"{cost:.2f}"))

            btn_save = QPushButton("Сохранить отчёт")
            btn_save.clicked.connect(lambda: save_report(
                self, "Остатки на складе", table,
                summary_rows=[
                    f"Всего позиций: {len(data)}",
                    f"Общая стоимость остатков: {total_cost:.2f} руб.",
                ]
            ))
            layout.addWidget(table)
            layout.addWidget(btn_save)
            dialog.exec_()

    # def show_order_materials(self):
    #     order_id, ok = self._input_order_id()
    #     if not ok:
    #         return
    #     resp = self.api.get(f"reports/warehouse-balance/")  # временно, пока нет отдельного эндпоинта
    #     # Используем фильтрацию по заказу из списка записей
    #     resp = self.api.get("inventory-records/")
    #     if resp.status_code == 200:
    #         raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
    #         filtered = [r for r in raw if r.get('order') == order_id and r.get('movement_type') == 'issue']
            
    #         dialog = QDialog(self)
    #         dialog.setWindowTitle(f"Расход материалов по заказу №{order_id}")
    #         dialog.setMinimumSize(500, 300)
    #         layout = QVBoxLayout(dialog)

    #         table = QTableWidget()
    #         table.setEditTriggers(QTableWidget.NoEditTriggers)
    #         table.setColumnCount(3)
    #         table.setHorizontalHeaderLabels(["Материал", "Количество", "Стоимость"])
    #         table.horizontalHeader().setStretchLastSection(True)
    #         table.setRowCount(len(filtered))
    #         for i, item in enumerate(filtered):
    #             table.setItem(i, 0, QTableWidgetItem(str(item.get('material_name', ''))))
    #             table.setItem(i, 1, QTableWidgetItem(str(item.get('quantity', 0))))
    #             table.setItem(i, 2, QTableWidgetItem(str(item.get('total_cost', 0))))

    #         btn_save = QPushButton("Сохранить отчёт")
    #         btn_save.clicked.connect(lambda: save_table_to_file(self, table, f"расход_заказ_{order_id}"))
    #         layout.addWidget(table)
    #         layout.addWidget(btn_save)
    #         dialog.exec_()
    def show_order_materials(self):
        # Диалог выбора заказа
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите заказ")
        layout = QFormLayout(dialog)
        order_combo = QComboBox()
        for o in self.orders_list:
            order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
        layout.addRow("Заказ", order_combo)
        btn = QPushButton("Показать")
        layout.addRow(btn)
        order_id = None

        def on_click():
            nonlocal order_id
            order_id = order_combo.currentData()
            dialog.accept()
        btn.clicked.connect(on_click)
        dialog.exec_()

        if order_id is None:
            return

        resp = self.api.get("inventory-records/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            filtered = [r for r in raw if r.get('order') == order_id and r.get('movement_type') == 'issue']

            report_dialog = QDialog(self)
            report_dialog.setWindowTitle(f"Расход материалов по заказу №{order_id}")
            report_dialog.setMinimumSize(500, 300)
            rl = QVBoxLayout(report_dialog)

            table = QTableWidget()
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Материал", "Количество", "Стоимость"])
            table.horizontalHeader().setStretchLastSection(True)
            table.setRowCount(len(filtered))
            for i, item in enumerate(filtered):
                table.setItem(i, 0, QTableWidgetItem(str(item.get('material_name', ''))))
                table.setItem(i, 1, QTableWidgetItem(str(item.get('quantity', 0))))
                table.setItem(i, 2, QTableWidgetItem(str(item.get('total_cost', 0))))

            # btn_save = QPushButton("Сохранить отчёт")
            # btn_save.clicked.connect(lambda: save_table_to_file(self, table, f"расход_заказ_{order_id}"))
            btn_save = QPushButton("Сохранить отчёт")
            btn_save.clicked.connect(lambda: save_report(
                self, f"Расход материалов по заказу №{order_id}", table,
                summary_rows=[
                    f"Заказ №{order_id}",
                    f"Всего позиций: {len(filtered)}",
                    f"Общая стоимость: {sum(float(r.get('total_cost', 0) or 0) for r in filtered):.2f} руб.",
    ]
))
            rl.addWidget(table)
            rl.addWidget(btn_save)
            report_dialog.exec_()

    # def _input_order_id(self):
    #     from PyQt5.QtWidgets import QInputDialog
    #     order_id, ok = QInputDialog.getInt(self, "Номер заказа", "Введите номер заказа:")
    #     return order_id, ok


class InventoryDialog(QDialog):
    def __init__(self, api_client, materials, orders, rec_id=None):
        super().__init__()
        self.api = api_client
        self.materials = materials
        self.orders = orders
        self.rec_id = rec_id
        self.setWindowTitle("Редактирование записи" if rec_id else "Новая запись")
        self.setMinimumWidth(600)
        self.init_ui()
        if rec_id:
            self._load_record()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.material_combo = QComboBox()
        for m in self.materials:
            self.material_combo.addItem(f"{m.get('name', '')} ({m.get('unit_price', 0)} руб.)", m.get('id'))
        form.addRow("Материал", self.material_combo)

        self.movement_combo = QComboBox()
        self.movement_combo.addItem("Поступление", "receipt")
        self.movement_combo.addItem("Выдача", "issue")
        form.addRow("Тип движения", self.movement_combo)

        self.quantity = QDoubleSpinBox()
        self.quantity.setMaximum(999999)
        self.quantity.setDecimals(2)
        self.quantity.setValue(1)
        form.addRow("Количество", self.quantity)

        self.price = QDoubleSpinBox()
        self.price.setMaximum(9999999)
        self.price.setDecimals(2)
        form.addRow("Цена за ед.", self.price)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        form.addRow("Дата", self.date)

        self.order_combo = QComboBox()
        self.order_combo.addItem("— Без заказа —", None)
        for o in self.orders:
            self.order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
        form.addRow("Заказ", self.order_combo)

        layout.addLayout(form)
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def _load_record(self):
        resp = self.api.get(f"inventory-records/{self.rec_id}/")
        if resp.status_code != 200:
            return
        data = resp.json()
        idx = self.material_combo.findData(data.get('material'))
        if idx >= 0:
            self.material_combo.setCurrentIndex(idx)
        idx = self.movement_combo.findData(data.get('movement_type'))
        if idx >= 0:
            self.movement_combo.setCurrentIndex(idx)
        self.quantity.setValue(float(data.get('quantity', 1)))
        self.price.setValue(float(data.get('unit_price', 0)))
        if data.get('date'):
            self.date.setDate(QDate.fromString(data['date'], 'yyyy-MM-dd'))
        if data.get('order'):
            idx = self.order_combo.findData(data.get('order'))
            if idx >= 0:
                self.order_combo.setCurrentIndex(idx)

    def save(self):
        data = {
            'material': self.material_combo.currentData(),
            'movement_type': self.movement_combo.currentData(),
            'quantity': self.quantity.value(),
            'unit_price': self.price.value(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'order': self.order_combo.currentData(),
        }
        if self.rec_id:
            resp = self.api.put(f"inventory-records/{self.rec_id}/", data)
        else:
            resp = self.api.post("inventory-records/", data)

        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")