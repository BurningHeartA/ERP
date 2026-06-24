from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDoubleSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from widgets import populate_table, save_report


class FinanceModule(QWidget):
    INCOME_COLUMNS = {
        'order_id': 'Заказ',
        'amount': 'Сумма',
        'payment_type': 'Тип платежа',
        'date': 'Дата',
        'description': 'Описание',
    }
    EXPENSE_COLUMNS = {
        'expense_category_name': 'Категория',
        'order_id': 'Заказ',
        'amount': 'Сумма',
        'date': 'Дата',
        'description': 'Описание',
    }

    PAYMENT_TYPES = {
        'prepayment': 'Предоплата',
        'final_payment': 'Итоговая оплата',
        'other': 'Прочее',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.orders_list = []
        self.expense_categories = []
        self.current_type = 'incomes'
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Финансы")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Выбор типа
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("Доходы", "incomes")
        self.type_combo.addItem("Расходы", "expenses")
        self.type_combo.currentIndexChanged.connect(self.load_data)
        top_layout.addWidget(self.type_combo)
        top_layout.addStretch()

        btn_add = QPushButton("+ Добавить")
        btn_add.clicked.connect(self.add_record)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_record)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_record)
        btn_report = QPushButton("Прибыли и убытки")
        btn_report.clicked.connect(self.show_profit_loss)

        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_edit)
        top_layout.addWidget(btn_delete)
        top_layout.addWidget(btn_report)
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self._load_dictionaries()
        self.load_data()

    def _load_dictionaries(self):
        resp = self.api.get("orders/")
        if resp.status_code == 200:
            self.orders_list = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
        resp = self.api.get("expense-categories/")
        if resp.status_code == 200:
            self.expense_categories = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])

    @property
    def endpoint(self):
        return self.type_combo.currentData()

    def load_data(self):
        resp = self.api.get(self.endpoint + "/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            columns = self.INCOME_COLUMNS if self.endpoint == 'incomes' else self.EXPENSE_COLUMNS
            allowed = set(columns.keys()) | {'id'}
            self.current_data = []
            for item in raw:
                # Заказ
                order_id = item.get('order')
                if order_id:
                    order_info = next((o for o in self.orders_list if o.get('id') == order_id), None)
                    item['order_id'] = f"Заказ №{order_id} — {order_info.get('product_name', '')}" if order_info else f"Заказ №{order_id}"
                else:
                    item['order_id'] = '—'
                # Тип платежа
                if 'payment_type' in item:
                    item['payment_type'] = self.PAYMENT_TYPES.get(item['payment_type'], item['payment_type'])
                # Категория
                if 'expense_category' in item:
                    cat = next((c for c in self.expense_categories if c.get('id') == item['expense_category']), None)
                    item['expense_category_name'] = cat.get('name', '') if cat else ''
                filtered = {k: v for k, v in item.items() if k in allowed}
                self.current_data.append(filtered)
            populate_table(self.table, self.current_data, columns)
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return None
        return self.current_data[row].get('id')

    def add_record(self):
        if self.endpoint == 'incomes':
            dialog = IncomeDialog(self.api, self.orders_list)
        else:
            dialog = ExpenseDialog(self.api, self.orders_list, self.expense_categories)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_record(self):
        rec_id = self.get_selected_id()
        if not rec_id:
            return
        if self.endpoint == 'incomes':
            dialog = IncomeDialog(self.api, self.orders_list, rec_id)
        else:
            dialog = ExpenseDialog(self.api, self.orders_list, self.expense_categories, rec_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def delete_record(self):
        rec_id = self.get_selected_id()
        if not rec_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить запись?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.delete(f"{self.endpoint}/{rec_id}/")
            if resp.status_code == 204:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")

    def show_profit_loss(self):
        start_date, end_date = self._get_period()
        if not start_date:
            return

        resp_inc = self.api.get("incomes/")
        resp_exp = self.api.get("expenses/")
        if resp_inc.status_code != 200 or resp_exp.status_code != 200:
            return

        incomes = resp_inc.json() if isinstance(resp_inc.json(), list) else resp_inc.json().get('results', [])
        expenses = resp_exp.json() if isinstance(resp_exp.json(), list) else resp_exp.json().get('results', [])

        # Фильтруем по дате
        incomes = [i for i in incomes if start_date <= i.get('date', '') <= end_date]
        expenses = [e for e in expenses if start_date <= e.get('date', '') <= end_date]

        total_income = sum(float(i.get('amount', 0) or 0) for i in incomes)
        total_expense = sum(float(e.get('amount', 0) or 0) for e in expenses)

        # Группировка расходов по категориям
        from collections import defaultdict
        cat_expenses = defaultdict(float)
        for e in expenses:
            cat_id = e.get('expense_category')
            cat = next((c for c in self.expense_categories if c.get('id') == cat_id), None)
            cat_name = cat.get('name', 'Прочее') if cat else 'Прочее'
            cat_expenses[cat_name] += float(e.get('amount', 0) or 0)

        dialog = QDialog(self)
        dialog.setWindowTitle("Прибыли и убытки")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Статья", "Сумма"])
        table.horizontalHeader().setStretchLastSection(True)

        rows = [("Доходы", total_income)]
        rows.append(("Расходы:", ""))
        for cat_name, amount in sorted(cat_expenses.items()):
            rows.append((f"  — {cat_name}", amount))
        rows.append(("Всего расходов", total_expense))
        rows.append(("Прибыль (убыток)", total_income - total_expense))

        table.setRowCount(len(rows))
        for i, (label, amount) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(label))
            table.setItem(i, 1, QTableWidgetItem(f"{amount:.2f}" if isinstance(amount, (int, float)) else amount))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Прибыли и убытки", table,
            summary_rows=[f"Период: {start_date} — {end_date}"],
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


class IncomeDialog(QDialog):
    def __init__(self, api_client, orders, rec_id=None):
        super().__init__()
        self.api = api_client
        self.orders = orders
        self.rec_id = rec_id
        self.setWindowTitle("Редактирование дохода" if rec_id else "Новый доход")
        self.setMinimumWidth(400)
        self.init_ui()
        if rec_id:
            self._load()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.order_combo = QComboBox()
        self.order_combo.addItem("— Без заказа —", None)
        for o in self.orders:
            self.order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
        form.addRow("Заказ", self.order_combo)

        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(99999999)
        self.amount.setDecimals(2)
        form.addRow("Сумма", self.amount)

        self.payment_type = QComboBox()
        self.payment_type.addItem("Предоплата", "prepayment")
        self.payment_type.addItem("Итоговая оплата", "final_payment")
        self.payment_type.addItem("Прочее", "other")
        form.addRow("Тип платежа", self.payment_type)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        form.addRow("Дата", self.date)

        self.description = QLineEdit()
        form.addRow("Описание", self.description)

        layout.addLayout(form)
        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        self.setLayout(layout)

    def _load(self):
        resp = self.api.get(f"incomes/{self.rec_id}/")
        if resp.status_code != 200:
            return
        d = resp.json()
        if d.get('order'):
            idx = self.order_combo.findData(d['order'])
            if idx >= 0:
                self.order_combo.setCurrentIndex(idx)
        self.amount.setValue(float(d.get('amount', 0) or 0))
        idx = self.payment_type.findData(d.get('payment_type'))
        if idx >= 0:
            self.payment_type.setCurrentIndex(idx)
        if d.get('date'):
            self.date.setDate(QDate.fromString(d['date'], 'yyyy-MM-dd'))
        self.description.setText(d.get('description', ''))

    def save(self):
        data = {
            'order': self.order_combo.currentData(),
            'amount': self.amount.value(),
            'payment_type': self.payment_type.currentData(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'description': self.description.text(),
        }
        if self.rec_id:
            resp = self.api.put(f"incomes/{self.rec_id}/", data)
        else:
            resp = self.api.post("incomes/", data)
        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")


class ExpenseDialog(QDialog):
    def __init__(self, api_client, orders, categories, rec_id=None):
        super().__init__()
        self.api = api_client
        self.orders = orders
        self.categories = categories
        self.rec_id = rec_id
        self.setWindowTitle("Редактирование расхода" if rec_id else "Новый расход")
        self.setMinimumWidth(400)
        self.init_ui()
        if rec_id:
            self._load()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.category_combo = QComboBox()
        for c in self.categories:
            self.category_combo.addItem(c.get('name', ''), c.get('id'))
        form.addRow("Категория", self.category_combo)

        self.order_combo = QComboBox()
        self.order_combo.addItem("— Без заказа —", None)
        for o in self.orders:
            self.order_combo.addItem(f"Заказ №{o.get('id')} — {o.get('product_name', '')}", o.get('id'))
        form.addRow("Заказ", self.order_combo)

        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(99999999)
        self.amount.setDecimals(2)
        form.addRow("Сумма", self.amount)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        form.addRow("Дата", self.date)

        self.description = QLineEdit()
        form.addRow("Описание", self.description)

        layout.addLayout(form)
        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        self.setLayout(layout)

    def _load(self):
        resp = self.api.get(f"expenses/{self.rec_id}/")
        if resp.status_code != 200:
            return
        d = resp.json()
        idx = self.category_combo.findData(d.get('expense_category'))
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        if d.get('order'):
            idx = self.order_combo.findData(d['order'])
            if idx >= 0:
                self.order_combo.setCurrentIndex(idx)
        self.amount.setValue(float(d.get('amount', 0) or 0))
        if d.get('date'):
            self.date.setDate(QDate.fromString(d['date'], 'yyyy-MM-dd'))
        self.description.setText(d.get('description', ''))

    def save(self):
        data = {
            'expense_category': self.category_combo.currentData(),
            'order': self.order_combo.currentData(),
            'amount': self.amount.value(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'description': self.description.text(),
        }
        if self.rec_id:
            resp = self.api.put(f"expenses/{self.rec_id}/", data)
        else:
            resp = self.api.post("expenses/", data)
        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")