from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from widgets import populate_table, save_report


class OrdersModule(QWidget):
    COLUMN_NAMES = {
        'id': '№',
        'customer_name': 'Клиент',
        'product_name': 'Изделие',
        'quantity': 'Кол-во',
        'total_price': 'Стоимость',
        'status': 'Статус',
        'accepted_date': 'Принят',
        'planned_completion_date': 'Сдача (план)',
    }

    STATUSES = {
        'pending': 'В очереди',
        'in_progress': 'В производстве',
        'completed': 'Завершён',
        'closed': 'Закрыт',
        'cancelled': 'Отменён',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.customers = []
        self.products = []
        self.requests_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Заказы")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Создать заказ")
        btn_add.clicked.connect(self.add_order)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_order)
        btn_delete = QPushButton("Отменить")
        btn_delete.clicked.connect(self.cancel_order)
        
        btn_profit = QPushButton("Рентабельность заказа")
        btn_profit.clicked.connect(self.show_order_profitability)
        btn_completion = QPushButton("Выполнение заказов")
        btn_completion.clicked.connect(self.show_completion_report)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_profit)
        btn_layout.addWidget(btn_completion)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self._load_dictionaries()
        self.load_data()

    def _load_dictionaries(self):
        resp = self.api.get("customers/")
        if resp.status_code == 200:
            self.customers = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("products/")
        if resp.status_code == 200:
            self.products = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        resp = self.api.get("requests/")
        if resp.status_code == 200:
            self.requests_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

    def load_data(self):
        resp = self.api.get("orders/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            allowed = set(self.COLUMN_NAMES.keys())
            self.current_data = []
            for item in raw:
                item['customer_name'] = item.get('customer_name', '')
                item['product_name'] = item.get('product_name', '')
                item['total_price'] = item.get('total_price', 0)
                item['status'] = self.STATUSES.get(item.get('status', ''), item.get('status', ''))
                filtered = {k: v for k, v in item.items() if k in allowed}
                self.current_data.append(filtered)
            populate_table(self.table, self.current_data, self.COLUMN_NAMES)
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")
            return None
        return self.current_data[row].get('id')

    def add_order(self):
        dialog = OrderDialog(self.api, self.customers, self.products, self.requests_list)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_order(self):
        order_id = self.get_selected_id()
        if not order_id:
            return
        dialog = OrderDialog(self.api, self.customers, self.products, self.requests_list, order_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def cancel_order(self):
        order_id = self.get_selected_id()
        if not order_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Отменить заказ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.patch(f"orders/{order_id}/", {"status": "cancelled"})
            if resp.status_code in [200, 201]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось: {resp.status_code}")

    def show_order_profitability(self):
        order_id = self.get_selected_id()
        if not order_id:
            return

        # Собираем данные
        resp_order = self.api.get(f"orders/{order_id}/")
        if resp_order.status_code != 200:
            return
        order = resp_order.json()

        # Трудозатраты
        resp_entries = self.api.get("work-entries/")
        labor_cost = 0.0
        if resp_entries.status_code == 200:
            entries = resp_entries.json() if isinstance(resp_entries.json(), list) else resp_entries.json().get('results', [])
            for e in entries:
                if e.get('order') == order_id:
                    dur = float(e.get('duration_hours', 0) or 0)
                    # Оценка стоимости часа — упрощённо
                    labor_cost += dur * 500  # базовая ставка, можно запросить реальную

        # Налоги (страховые взносы 30%)
        taxes = labor_cost * 0.30

        # Материалы
        resp_inv = self.api.get("inventory-records/")
        material_cost = 0.0
        if resp_inv.status_code == 200:
            inv_records = resp_inv.json() if isinstance(resp_inv.json(), list) else resp_inv.json().get('results', [])
            for r in inv_records:
                if r.get('order') == order_id and r.get('movement_type') == 'issue':
                    material_cost += float(r.get('total_cost', 0) or 0)

        # Расходы (финансы)
        resp_exp = self.api.get("expenses/")
        fin_expense = 0.0
        if resp_exp.status_code == 200:
            expenses = resp_exp.json() if isinstance(resp_exp.json(), list) else resp_exp.json().get('results', [])
            for e in expenses:
                if e.get('order') == order_id:
                    fin_expense += float(e.get('amount', 0) or 0)

        # Доходы
        resp_inc = self.api.get("incomes/")
        income = 0.0
        if resp_inc.status_code == 200:
            incomes = resp_inc.json() if isinstance(resp_inc.json(), list) else resp_inc.json().get('results', [])
            for inc in incomes:
                if inc.get('order') == order_id:
                    income += float(inc.get('amount', 0) or 0)

        total_costs = labor_cost + taxes + material_cost + fin_expense
        profit = income - total_costs
        profitability = (profit / total_costs * 100) if total_costs > 0 else 0

        # Прибыльность в день
        from datetime import date as dt
        accepted = order.get('accepted_date', '')
        completed = order.get('completion_date', '') or str(dt.today())
        try:
            d1 = dt.fromisoformat(accepted)
            d2 = dt.fromisoformat(completed)
            days = (d2 - d1).days or 1
        except (ValueError, TypeError):
            days = 1
        profit_per_day = profit / days

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Рентабельность заказа №{order_id}")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        table.horizontalHeader().setStretchLastSection(True)

        product_name = order.get('product_name', '')
        status = self.STATUSES.get(order.get('status', ''), '')

        rows = [
            ("Заказ №", order_id),
            ("Изделие", product_name),
            ("Дата принятия", accepted),
            ("Статус", status),
            ("", ""),
            ("Трудозатраты", f"{labor_cost:.2f} руб."),
            ("Налоги (30%)", f"{taxes:.2f} руб."),
            ("Затраты материалов", f"{material_cost:.2f} руб."),
            ("Финансовые расходы", f"{fin_expense:.2f} руб."),
            ("", ""),
            ("Всего затрат", f"{total_costs:.2f} руб."),
            ("Доходы", f"{income:.2f} руб."),
            ("", ""),
            ("Прибыль", f"{profit:.2f} руб."),
            ("Рентабельность", f"{profitability:.1f}%"),
            ("Прибыльность в день", f"{profit_per_day:.2f} руб./день"),
        ]
        table.setRowCount(len(rows))
        for i, (label, value) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(str(label)))
            table.setItem(i, 1, QTableWidgetItem(str(value)))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, f"Рентабельность заказа №{order_id}", table,
            summary_rows=[
                f"Заказ №{order_id} — {product_name}",
                f"Прибыль: {profit:.2f} руб.",
                f"Рентабельность: {profitability:.1f}%",
            ],
            params={
                "Заказ": f"№{order_id}",
                "Изделие": product_name,
                "Статус": status,
            }
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()

    def show_completion_report(self):
        start_date, end_date = self._get_period()
        if not start_date:
            return

        resp = self.api.get("orders/")
        if resp.status_code != 200:
            return
        orders = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

        # Для отладки — выведи завершённые заказы и их даты
        for o in orders:
            if o.get('status') in ['completed', 'closed']:
                print(f"Заказ {o['id']}: status={o['status']}, completion_date={o.get('completion_date')}")

        # Фильтруем завершённые в периоде
        completed = [o for o in orders
                     if o.get('completion_date') and start_date <= o['completion_date'] <= end_date
                     and o.get('status') in ['completed', 'closed']]

        total_profit = 0.0
        total_revenue = 0.0
        for o in completed:
            order_id = o['id']
            # Упрощённый расчёт прибыли
            revenue = float(o.get('total_price', 0) or 0)
            total_revenue += revenue
            total_profit += revenue * 0.2

        from datetime import date as dt
        try:
            d1 = dt.fromisoformat(start_date)
            d2 = dt.fromisoformat(end_date)
            period_days = (d2 - d1).days or 1
        except (ValueError, TypeError):
            period_days = 1

        avg_check = total_revenue / period_days if period_days > 0 else 0

        dialog = QDialog(self)
        dialog.setWindowTitle("Выполнение заказов")
        dialog.setMinimumSize(400, 250)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        table.horizontalHeader().setStretchLastSection(True)

        rows = [
            ("Период", f"{start_date} — {end_date}"),
            ("Выполнено заказов", len(completed)),
            ("Общая прибыль", f"{total_profit:.2f} руб."),
            ("Средний чек (в день)", f"{avg_check:.2f} руб."),
        ]
        table.setRowCount(len(rows))
        for i, (label, value) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(str(label)))
            table.setItem(i, 1, QTableWidgetItem(str(value)))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Выполнение заказов", table,
            summary_rows=[
                f"Период: {start_date} — {end_date}",
                f"Выполнено заказов: {len(completed)}",
            ],
            params={"Период": f"{start_date} — {end_date}"}
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()

    def _get_period(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите период")
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


class OrderDialog(QDialog):
    MATERIAL_SOURCES = [
        ('customer', 'Заказчик'),
        ('waste', 'Отходы'),
        ('purchase', 'Закупка'),
    ]

    def __init__(self, api_client, customers, products, requests_list, order_id=None):
        super().__init__()
        self.api = api_client
        self.customers = customers
        self.products = products
        self.requests = requests_list
        self.order_id = order_id
        self.setWindowTitle("Редактирование заказа" if order_id else "Новый заказ")
        self.setMinimumWidth(450)
        self.init_ui()
        if order_id:
            self._load_order()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.request_combo = QComboBox()
        self.request_combo.addItem("— Без заявки —", None)
        for r in self.requests:
            self.request_combo.addItem(f"Заявка №{r.get('id')} — {r.get('customer_name', '')}", r.get('id'))
        form.addRow("Заявка", self.request_combo)

        self.customer_combo = QComboBox()
        for c in self.customers:
            self.customer_combo.addItem(c.get('name', ''), c.get('id'))
        form.addRow("Клиент", self.customer_combo)

        self.product_combo = QComboBox()
        for p in self.products:
            self.product_combo.addItem(p.get('name', ''), p.get('id'))
        form.addRow("Изделие", self.product_combo)

        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(99999)
        self.quantity.setValue(1)
        form.addRow("Количество", self.quantity)

        self.price = QDoubleSpinBox()
        self.price.setMaximum(99999999)
        self.price.setDecimals(2)
        self.price.setValue(0)
        form.addRow("Цена за ед.", self.price)

        self.material_source = QComboBox()
        for val, label in self.MATERIAL_SOURCES:
            self.material_source.addItem(label, val)
        form.addRow("Источник материала", self.material_source)

        self.accepted_date = QDateEdit()
        self.accepted_date.setCalendarPopup(True)
        self.accepted_date.setDate(QDate.currentDate())
        form.addRow("Дата принятия", self.accepted_date)

        self.planned_date = QDateEdit()
        self.planned_date.setCalendarPopup(True)
        self.planned_date.setDate(QDate.currentDate().addDays(30))
        form.addRow("Плановая дата сдачи", self.planned_date)

        self.launch_date = QDateEdit()
        self.launch_date.setCalendarPopup(True)
        self.launch_date.setSpecialValueText("—")
        self.launch_date.setDate(QDate())
        self.launch_date.setEnabled(False)
        form.addRow("Дата запуска", self.launch_date)

        self.completion_date = QDateEdit()
        self.completion_date.setCalendarPopup(True)
        self.completion_date.setSpecialValueText("—")
        self.completion_date.setDate(QDate())
        self.completion_date.setEnabled(False)
        form.addRow("Дата завершения", self.completion_date)

        self.status_combo = QComboBox()
        self.status_combo.addItem("В очереди", "pending")
        self.status_combo.addItem("В производстве", "in_progress")
        self.status_combo.addItem("Завершён", "completed")
        self.status_combo.addItem("Закрыт", "closed")
        self.status_combo.addItem("Отменён", "cancelled")
        form.addRow("Статус", self.status_combo)

        self.notes = QLineEdit()
        form.addRow("Примечания", self.notes)

        layout.addLayout(form)
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def _load_order(self):
        resp = self.api.get(f"orders/{self.order_id}/")
        if resp.status_code != 200:
            return
        d = resp.json()
        if d.get('request'):
            idx = self.request_combo.findData(d['request'])
            if idx >= 0:
                self.request_combo.setCurrentIndex(idx)
        idx = self.customer_combo.findData(d.get('customer'))
        if idx >= 0:
            self.customer_combo.setCurrentIndex(idx)
        idx = self.product_combo.findData(d.get('product'))
        if idx >= 0:
            self.product_combo.setCurrentIndex(idx)
        self.quantity.setValue(d.get('quantity', 1))
        self.price.setValue(float(d.get('price_per_unit', 0) or 0))
        idx = self.material_source.findData(d.get('material_source'))
        if idx >= 0:
            self.material_source.setCurrentIndex(idx)
        if d.get('accepted_date'):
            self.accepted_date.setDate(QDate.fromString(d['accepted_date'], 'yyyy-MM-dd'))
        if d.get('planned_completion_date'):
            self.planned_date.setDate(QDate.fromString(d['planned_completion_date'], 'yyyy-MM-dd'))
        if d.get('launch_date'):
            self.launch_date.setDate(QDate.fromString(d['launch_date'], 'yyyy-MM-dd'))
        if d.get('completion_date'):
            self.completion_date.setDate(QDate.fromString(d['completion_date'], 'yyyy-MM-dd'))
        idx = self.status_combo.findData(d.get('status'))
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        self.notes.setText(d.get('notes', ''))

    def save(self):
        data = {
            'request': self.request_combo.currentData(),
            'customer': self.customer_combo.currentData(),
            'product': self.product_combo.currentData(),
            'quantity': self.quantity.value(),
            'price_per_unit': self.price.value(),
            'material_source': self.material_source.currentData(),
            'accepted_date': self.accepted_date.date().toString('yyyy-MM-dd'),
            'planned_completion_date': self.planned_date.date().toString('yyyy-MM-dd'),
            'launch_date': self.launch_date.date().toString('yyyy-MM-dd') if self.launch_date.date() > QDate(2000, 1, 1) else None,
            'completion_date': self.completion_date.date().toString('yyyy-MM-dd') if self.completion_date.date() > QDate(2000, 1, 1) else None,
            'status': self.status_combo.currentData(),
            'notes': self.notes.text(),
        }
        if self.order_id:
            resp = self.api.put(f"orders/{self.order_id}/", data)
        else:
            resp = self.api.post("orders/", data)
        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")