from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog,
    QFormLayout, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from widgets import save_report


class ReportsModule(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Аналитика и отчёты")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        btn_labor = QPushButton("Трудозатраты по сотрудникам за период")
        btn_labor.clicked.connect(self.show_labor_report)
        btn_layout.addWidget(btn_labor)

        btn_distribution = QPushButton("Распределение работ по заказам")
        btn_distribution.clicked.connect(self.show_work_distribution)
        btn_layout.addWidget(btn_distribution)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def _get_period(self, title="Выберите период"):
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

    def show_labor_report(self):
        start_date, end_date = self._get_period()
        if not start_date:
            return

        # Получаем сотрудников
        resp_emp = self.api.get("employees/")
        if resp_emp.status_code != 200:
            return
        employees = resp_emp.json() if isinstance(resp_emp.json(), list) else resp_emp.json().get('results', [])

        # Получаем табель
        resp_logs = self.api.get("work-logs/")
        if resp_logs.status_code != 200:
            return
        logs = resp_logs.json() if isinstance(resp_logs.json(), list) else resp_logs.json().get('results', [])

        # Собираем данные по сотрудникам
        emp_data = {}
        total_hours_all = 0.0
        total_salary_all = 0.0

        for emp in employees:
            emp_id = emp['id']
            emp_hours = 0.0
            for log in logs:
                if log.get('employee') != emp_id:
                    continue
                if not (start_date <= log.get('shift_date', '') <= end_date):
                    continue
                for e in log.get('entries', []):
                    emp_hours += float(e.get('duration_hours', 0) or 0)
            
            if emp_hours > 0:
                tariff = float(emp.get('tariff_rate', 0) or 0)
                salary = tariff * emp_hours
                tax = salary * 0.152
                emp_data[emp_id] = {
                    'name': emp.get('full_name', ''),
                    'hours': emp_hours,
                    'salary': salary,
                    'tax': tax,
                }
                total_hours_all += emp_hours
                total_salary_all += salary

        if not emp_data:
            QMessageBox.information(self, "Информация", "Нет данных за выбранный период")
            return

        total_tax_all = total_salary_all * 0.152

        dialog = QDialog(self)
        dialog.setWindowTitle("Трудозатраты по сотрудникам")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Сотрудник", "Часов", "Зарплата", "Налоги (15.2%)",
            "% часов", "% зарплаты"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(len(emp_data))

        for i, (emp_id, d) in enumerate(sorted(emp_data.items(), key=lambda x: x[1]['hours'], reverse=True)):
            table.setItem(i, 0, QTableWidgetItem(d['name']))
            table.setItem(i, 1, QTableWidgetItem(f"{d['hours']:.1f}"))
            table.setItem(i, 2, QTableWidgetItem(f"{d['salary']:.2f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{d['tax']:.2f}"))
            pct_hours = (d['hours'] / total_hours_all * 100) if total_hours_all > 0 else 0
            pct_salary = (d['salary'] / total_salary_all * 100) if total_salary_all > 0 else 0
            table.setItem(i, 4, QTableWidgetItem(f"{pct_hours:.1f}%"))
            table.setItem(i, 5, QTableWidgetItem(f"{pct_salary:.1f}%"))

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Трудозатраты по сотрудникам", table,
            summary_rows=[
                f"Период: {start_date} — {end_date}",
                f"Всего часов: {total_hours_all:.1f}",
                f"Общая зарплата: {total_salary_all:.2f} руб.",
                f"Общие налоги: {total_tax_all:.2f} руб.",
            ],
            params={"Период": f"{start_date} — {end_date}"}
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()

    def show_work_distribution(self):
        start_date, end_date = self._get_period()
        if not start_date:
            return

        # Получаем табель
        resp_logs = self.api.get("work-logs/")
        if resp_logs.status_code != 200:
            return
        logs = resp_logs.json() if isinstance(resp_logs.json(), list) else resp_logs.json().get('results', [])

        # Собираем данные: категория -> заказ -> часы
        from collections import defaultdict
        cat_order_hours = defaultdict(lambda: defaultdict(float))
        orders_set = set()
        categories_set = set()
        total_hours = 0.0

        for log in logs:
            if not (start_date <= log.get('shift_date', '') <= end_date):
                continue
            for e in log.get('entries', []):
                cat = e.get('work_category_name', 'Неизвестно')
                order_id = e.get('order')
                order_name = f"Заказ №{order_id}" if order_id else "Без заказа"
                dur = float(e.get('duration_hours', 0) or 0)
                cat_order_hours[cat][order_name] += dur
                orders_set.add(order_name)
                categories_set.add(cat)
                total_hours += dur

        if not categories_set:
            QMessageBox.information(self, "Информация", "Нет данных за выбранный период")
            return

        orders_list = sorted(orders_set)
        categories_list = sorted(categories_set)

        # Колонки: категория | заказ1 | заказ2 | ... | всего часов | %
        dialog = QDialog(self)
        dialog.setWindowTitle("Распределение работ по заказам")
        dialog.setMinimumSize(800, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setColumnCount(1 + len(orders_list) + 2)
        headers = ["Категория"] + orders_list + ["Всего часов", "%"]
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(len(categories_list) + 1)  # +1 для итогов

        # Итоги по заказам
        order_totals = defaultdict(float)

        for i, cat in enumerate(categories_list):
            table.setItem(i, 0, QTableWidgetItem(cat))
            cat_total = 0.0
            for j, order_name in enumerate(orders_list):
                hours = cat_order_hours[cat].get(order_name, 0)
                cat_total += hours
                order_totals[order_name] += hours
                table.setItem(i, 1 + j, QTableWidgetItem(f"{hours:.1f}" if hours > 0 else "—"))
            table.setItem(i, 1 + len(orders_list), QTableWidgetItem(f"{cat_total:.1f}"))
            pct = (cat_total / total_hours * 100) if total_hours > 0 else 0
            table.setItem(i, 1 + len(orders_list) + 1, QTableWidgetItem(f"{pct:.1f}%"))

        # Последняя строка — итоги по заказам
        last_row = len(categories_list)
        table.setItem(last_row, 0, QTableWidgetItem("ИТОГО"))
        for j, order_name in enumerate(orders_list):
            table.setItem(last_row, 1 + j, QTableWidgetItem(f"{order_totals[order_name]:.1f}"))
        table.setItem(last_row, 1 + len(orders_list), QTableWidgetItem(f"{total_hours:.1f}"))
        table.setItem(last_row, 1 + len(orders_list) + 1, QTableWidgetItem("100%"))

        # Жирный шрифт для последней строки
        from PyQt5.QtGui import QFont
        font = QFont()
        font.setBold(True)
        for j in range(table.columnCount()):
            item = table.item(last_row, j)
            if item:
                item.setFont(font)

        btn_save = QPushButton("Сохранить отчёт")
        btn_save.clicked.connect(lambda: save_report(
            self, "Распределение работ по заказам", table,
            summary_rows=[
                f"Период: {start_date} — {end_date}",
                f"Всего часов: {total_hours:.1f}",
            ],
            params={"Период": f"{start_date} — {end_date}"}
        ))
        layout.addWidget(table)
        layout.addWidget(btn_save)
        dialog.exec_()