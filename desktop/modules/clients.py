from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QHeaderView, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from widgets import populate_table, save_report


class ClientsModule(QWidget):
    COLUMN_NAMES = {
        'name': 'Наименование',
        'phone': 'Телефон',
        'email': 'Email',
        'source': 'Источник привлечения',
        'user': 'Пользователь',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Клиенты")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        # left_btns = QHBoxLayout()
        # right_btns = QHBoxLayout()

        btn_add = QPushButton("+ Добавить")
        btn_add.clicked.connect(self.add_client)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_client)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_client)

        # Кнопки отчетов
        btn_client_profit = QPushButton("Рентабельность клиента")
        btn_client_profit.clicked.connect(self.show_client_profitability)
        btn_report = QPushButton("Отчёт: каналы привлечения")
        btn_report.clicked.connect(self.show_channel_report)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_report)
        btn_layout.addWidget(btn_client_profit)
        
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        resp = self.api.get("customers/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            self.current_data = []
            for item in raw:
                # Заменяем user_id на читаемое имя пользователя
                if isinstance(item.get('user'), dict):
                    item['user'] = item['user'].get('username', '')
                elif item.get('user') is None:
                    item['user'] = '—'
                self.current_data.append(item)
            populate_table(self.table, self.current_data, self.COLUMN_NAMES)
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")


    def show_client_profitability(self):
        client_id = self.get_selected_id()
        if not client_id:
            return

        client = next((c for c in self.current_data if c.get('id') == client_id), None)
        if not client:
            return

        # Получаем заказы клиента
        resp = self.api.get("orders/")
        if resp.status_code != 200:
            return
        orders = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
        client_orders = [o for o in orders if o.get('customer') == client_id]

        total_revenue = sum(float(o.get('total_price', 0) or 0) for o in client_orders)
        
        # Расчёт средней прибыли (упрощённо)
        profits = []
        for o in client_orders:
            revenue = float(o.get('total_price', 0) or 0)
            costs = revenue * 0.7  # грубая оценка
            profits.append(revenue - costs)
        avg_profit = sum(profits) / len(profits) if profits else 0

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Рентабельность: {client.get('name', '')}")
        dialog.setMinimumSize(400, 250)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        table.horizontalHeader().setStretchLastSection(True)

        rows = [
            ("Клиент", client.get('name', '')),
            ("Количество заказов", len(client_orders)),
            ("Суммарная стоимость заказов", f"{total_revenue:.2f} руб."),
            ("Средняя прибыль заказа", f"{avg_profit:.2f} руб."),
        ]
        table.setRowCount(len(rows))
        for i, (label, value) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(str(label)))
            table.setItem(i, 1, QTableWidgetItem(str(value)))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, f"Рентабельность {client.get('name', '')}", table,
            summary_rows=[
                f"Клиент: {client.get('name', '')}",
                f"Заказов: {len(client_orders)}",
                f"Сумма: {total_revenue:.2f} руб.",
            ],
            params={"Клиент": client.get('name', '')}
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

    def add_client(self):
        dialog = ClientDialog(self.api)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_client(self):
        client_id = self.get_selected_id()
        if not client_id:
            return
        dialog = ClientDialog(self.api, client_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def delete_client(self):
        client_id = self.get_selected_id()
        if not client_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить клиента?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.delete(f"customers/{client_id}/")
            if resp.status_code == 204:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")

   

    # def show_channel_report(self):
    #     resp = self.api.get("reports/customer-channels/")
    #     if resp.status_code == 200:
    #         data = resp.json()
    #         dialog = QDialog(self)
    #         dialog.setWindowTitle("Эффективность каналов привлечения")
    #         dialog.setMinimumSize(600, 300)
    #         layout = QVBoxLayout(dialog)

    #         table = QTableWidget()
    #         table.setEditTriggers(QTableWidget.NoEditTriggers)
    #         table.setColumnCount(6)
    #         table.setHorizontalHeaderLabels([
    #             "Канал", "Клиентов", "Заказов", "Сумма",
    #             "% заказов", "% суммы"
    #         ])
    #         table.horizontalHeader().setStretchLastSection(True)
    #         table.setRowCount(len(data))

    #         for i, item in enumerate(data):
    #             table.setItem(i, 0, QTableWidgetItem(str(item.get('source', ''))))
    #             table.setItem(i, 1, QTableWidgetItem(str(item.get('client_count', 0))))
    #             table.setItem(i, 2, QTableWidgetItem(str(item.get('order_count', 0))))
    #             table.setItem(i, 3, QTableWidgetItem(f"{item.get('total_sum', 0):.2f}"))
    #             table.setItem(i, 4, QTableWidgetItem(f"{item.get('order_percent', 0)}%"))
    #             table.setItem(i, 5, QTableWidgetItem(f"{item.get('sum_percent', 0)}%"))

    #         btn_save = QPushButton("Сохранить отчёт")
    #         btn_save.clicked.connect(lambda: self._save_report(table, "эффективность_каналов"))
    #         layout.addWidget(btn_save)
    #         layout.addWidget(table)
    #         dialog.exec_()
    #     else:
    #         QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить отчёт: {resp.status_code}")

    def show_channel_report(self):
        resp = self.api.get("reports/customer-channels/")
        if resp.status_code == 200:
            data = resp.json()
            dialog = QDialog(self)
            dialog.setWindowTitle("Эффективность каналов привлечения")
            dialog.setMinimumSize(600, 300)
            layout = QVBoxLayout(dialog)

            table = QTableWidget()
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([
                "Канал", "Клиентов", "Заказов", "Сумма",
                "% заказов", "% суммы"
            ])
            table.horizontalHeader().setStretchLastSection(True)
            table.setRowCount(len(data))

            total_sum = sum(item.get('total_sum', 0) for item in data)
            total_orders = sum(item.get('order_count', 0) for item in data)

            for i, item in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(str(item.get('source', ''))))
                table.setItem(i, 1, QTableWidgetItem(str(item.get('client_count', 0))))
                table.setItem(i, 2, QTableWidgetItem(str(item.get('order_count', 0))))
                table.setItem(i, 3, QTableWidgetItem(f"{item.get('total_sum', 0):.2f}"))
                table.setItem(i, 4, QTableWidgetItem(f"{item.get('order_percent', 0)}%"))
                table.setItem(i, 5, QTableWidgetItem(f"{item.get('sum_percent', 0)}%"))

            btn_save = QPushButton("Сохранить отчёт")
            btn_save.clicked.connect(lambda: save_report(
                self, "Эффективность каналов привлечения", table,
                summary_rows=[
                    f"Всего каналов: {len(data)}",
                    f"Всего заказов: {total_orders}",
                    f"Общая сумма: {total_sum:.2f} руб.",
                ]
            ))
            layout.addWidget(table)
            layout.addWidget(btn_save)
            dialog.exec_()

    def _save_report(self, table, filename):
        from PyQt5.QtWidgets import QFileDialog
        import os

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт",
            os.path.expanduser(f"~\\Desktop\\{filename}.txt"),
            "Текстовые файлы (*.txt);;CSV (*.csv)"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Заголовки
                headers = [table.horizontalHeaderItem(j).text() for j in range(table.columnCount())]
                f.write('\t'.join(headers) + '\n')
                # Данные
                for i in range(table.rowCount()):
                    row = [table.item(i, j).text() if table.item(i, j) else '' for j in range(table.columnCount())]
                    f.write('\t'.join(row) + '\n')

            QMessageBox.information(self, "Готово", f"Отчёт сохранён:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")


class ClientDialog(QDialog):
    SOURCES = [
        ('personal_referral', 'Личное знакомство'),
        ('farpost', 'Farpost'),
        ('avito', 'Avito'),
        ('partner_company', 'Компания-партнёр'),
        ('company_website', 'Сайт компании'),
    ]

    def __init__(self, api_client, client_id=None):
        super().__init__()
        self.api = api_client
        self.client_id = client_id
        self.setWindowTitle("Редактирование клиента" if client_id else "Новый клиент")
        self.setFixedWidth(400)
        self.free_users = []
        self.init_ui()
        if client_id:
            self.load_client()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit()
        form.addRow("Наименование", self.name_input)

        self.phone_input = QLineEdit()
        form.addRow("Телефон", self.phone_input)

        self.email_input = QLineEdit()
        form.addRow("Email", self.email_input)

        self.source_combo = QComboBox()
        for value, label in self.SOURCES:
            self.source_combo.addItem(label, value)
        form.addRow("Источник", self.source_combo)

        # Выбор пользователя
        self.user_combo = QComboBox()
        self.user_combo.addItem("Без учётной записи", None)
        self._load_free_users()
        form.addRow("Пользователь", self.user_combo)

        layout.addLayout(form)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _load_free_users(self):
        resp_users = self.api.get("users/")
        if resp_users.status_code != 200:
            return
        users = resp_users.json() if isinstance(resp_users.json(), list) else resp_users.json().get('results', [])

        # Получаем всех клиентов, чтобы узнать, какие user_id уже заняты
        resp_customers = self.api.get("customers/")
        used_user_ids = set()
        if resp_customers.status_code == 200:
            customers = resp_customers.json() if isinstance(resp_customers.json(), list) else resp_customers.json().get('results', [])
            for c in customers:
                if c.get('user'):
                    used_user_ids.add(c['user'])

        for u in users:
            if u.get('id') not in used_user_ids:
                self.user_combo.addItem(u.get('username', ''), u.get('id'))

    def load_client(self):
        resp = self.api.get(f"customers/{self.client_id}/")
        if resp.status_code == 200:
            data = resp.json()
            self.name_input.setText(data.get('name', ''))
            self.phone_input.setText(data.get('phone', ''))
            self.email_input.setText(data.get('email', ''))
            source = data.get('source', '')
            idx = self.source_combo.findData(source)
            if idx >= 0:
                self.source_combo.setCurrentIndex(idx)
            user_id = data.get('user')
            if user_id:
                idx = self.user_combo.findData(user_id)
                if idx >= 0:
                    self.user_combo.setCurrentIndex(idx)

    def save(self):
        data = {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'email': self.email_input.text(),
            'source': self.source_combo.currentData(),
            'user': self.user_combo.currentData(),
        }
        if self.client_id:
            resp = self.api.put(f"customers/{self.client_id}/", data)
        else:
            resp = self.api.post("customers/", data)

        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")