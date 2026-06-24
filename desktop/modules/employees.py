from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QCheckBox, QScrollArea,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from widgets import populate_table


class EmployeesModule(QWidget):
    COLUMN_NAMES = {
        'full_name': 'ФИО',
        'position_name': 'Должность',
        'work_schedule_name': 'График',
        'status': 'Статус',
        'phone': 'Телефон',
    }

    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_data = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Сотрудники")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_add.clicked.connect(self.add_employee)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_employee)
        btn_delete = QPushButton("Уволить")
        btn_delete.clicked.connect(self.dismiss_employee)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        layout.addWidget(self.table)

        self.load_data()

    # def load_data(self):
    #     resp = self.api.get("employees/")
    #     if resp.status_code == 200:
    #         raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
    #         self.current_data = []
    #         for item in raw:
    #             item['full_name'] = item.get('full_name', '')
    #             item['position_name'] = item.get('position_name', '')
    #             item['work_schedule_name'] = item.get('work_schedule_name', '')
    #             self.current_data.append(item)
    #         populate_table(self.table, self.current_data, self.COLUMN_NAMES)
    #     else:
    #         QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {resp.status_code}")

    def load_data(self):
        resp = self.api.get("employees/")
        if resp.status_code == 200:
            raw = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            allowed_keys = set(self.COLUMN_NAMES.keys()) | {'id'}
            self.current_data = []
            for item in raw:
                # Добавляем вычисляемые поля
                item['full_name'] = f"{item.get('last_name', '')} {item.get('first_name', '')} {item.get('middle_name', '')}".strip()
                item['position_name'] = item.get('position_name', '')
                item['work_schedule_name'] = item.get('work_schedule_name', '')
                # Оставляем только разрешённые ключи
                filtered = {k: v for k, v in item.items() if k in allowed_keys}
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

    def add_employee(self):
        dialog = EmployeeDialog(self.api)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def edit_employee(self):
        emp_id = self.get_selected_id()
        if not emp_id:
            return
        dialog = EmployeeDialog(self.api, emp_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def dismiss_employee(self):
        emp_id = self.get_selected_id()
        if not emp_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Уволить сотрудника?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.patch(f"employees/{emp_id}/", {"status": "dismissed"})
            if resp.status_code in [200, 201]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось: {resp.status_code}")


class EmployeeDialog(QDialog):
    def __init__(self, api_client, emp_id=None):
        super().__init__()
        self.api = api_client
        self.emp_id = emp_id
        self.setWindowTitle("Редактирование сотрудника" if emp_id else "Новый сотрудник")
        self.setMinimumWidth(500)
        self.positions = []
        self.schedules = []
        self.competences = []
        self.competence_checkboxes = []
        self.init_ui()
        self._load_dictionaries()
        if emp_id:
            self._load_employee()

    def init_ui(self):
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)

        self.last_name = QLineEdit()
        form.addRow("Фамилия", self.last_name)
        self.first_name = QLineEdit()
        form.addRow("Имя", self.first_name)
        self.middle_name = QLineEdit()
        form.addRow("Отчество", self.middle_name)

        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate(1990, 1, 1))
        form.addRow("Дата рождения", self.birth_date)

        self.passport = QLineEdit()
        form.addRow("Паспорт", self.passport)
        self.phone = QLineEdit()
        form.addRow("Телефон", self.phone)
        self.email = QLineEdit()
        form.addRow("Email", self.email)
        self.contract = QLineEdit()
        form.addRow("Трудовой договор", self.contract)
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        form.addRow("Дата приёма", self.hire_date)

        self.position_combo = QComboBox()
        form.addRow("Должность", self.position_combo)

        self.schedule_combo = QComboBox()
        form.addRow("График", self.schedule_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Нанят", "hired")
        self.status_combo.addItem("Уволен", "dismissed")
        form.addRow("Статус", self.status_combo)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Компетенции
        comp_label = QLabel("Компетенции:")
        layout.addWidget(comp_label)
        self.comp_layout = QVBoxLayout()
        layout.addLayout(self.comp_layout)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _load_dictionaries(self):
        # Должности
        resp = self.api.get("positions/")
        if resp.status_code == 200:
            self.positions = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            for p in self.positions:
                self.position_combo.addItem(p.get('name', ''), p.get('id'))

        # Графики
        resp = self.api.get("work-schedules/")
        if resp.status_code == 200:
            self.schedules = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            for s in self.schedules:
                self.schedule_combo.addItem(s.get('name', ''), s.get('id'))

        # Компетенции (список с галочками)
        resp = self.api.get("competences/")
        if resp.status_code == 200:
            self.competences = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            for c in self.competences:
                cb = QCheckBox(c.get('name', ''))
                cb.setProperty('competence_id', c.get('id'))
                self.competence_checkboxes.append(cb)
                self.comp_layout.addWidget(cb)

    def _load_employee(self):
        resp = self.api.get(f"employees/{self.emp_id}/")
        if resp.status_code != 200:
            return
        data = resp.json()

        self.last_name.setText(data.get('last_name', ''))
        self.first_name.setText(data.get('first_name', ''))
        self.middle_name.setText(data.get('middle_name', ''))

        if data.get('birth_date'):
            self.birth_date.setDate(QDate.fromString(data['birth_date'], 'yyyy-MM-dd'))

        self.passport.setText(data.get('passport_number', ''))
        self.phone.setText(data.get('phone', ''))
        self.email.setText(data.get('email', ''))
        self.contract.setText(data.get('contract_number', ''))
        if data.get('hire_date'):
            self.hire_date.setDate(QDate.fromString(data['hire_date'], 'yyyy-MM-dd'))

        idx = self.position_combo.findData(data.get('position'))
        if idx >= 0:
            self.position_combo.setCurrentIndex(idx)
        idx = self.schedule_combo.findData(data.get('work_schedule'))
        if idx >= 0:
            self.schedule_combo.setCurrentIndex(idx)
        idx = self.status_combo.findData(data.get('status'))
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        # Компетенции сотрудника
        comp_resp = self.api.get(f"employee-competences/?employee={self.emp_id}")
        emp_comp_ids = set()
        if comp_resp.status_code == 200:
            comps = comp_resp.json() if isinstance(comp_resp.json(), list) else comp_resp.json().get('results', [])
            emp_comp_ids = {c.get('competence') for c in comps}

        for cb in self.competence_checkboxes:
            if cb.property('competence_id') in emp_comp_ids:
                cb.setChecked(True)

    def save(self):
        data = {
            'last_name': self.last_name.text(),
            'first_name': self.first_name.text(),
            'middle_name': self.middle_name.text(),
            'birth_date': self.birth_date.date().toString('yyyy-MM-dd'),
            'passport_number': self.passport.text(),
            'phone': self.phone.text(),
            'email': self.email.text(),
            'contract_number': self.contract.text(),
            'hire_date': self.hire_date.date().toString('yyyy-MM-dd'),
            'position': self.position_combo.currentData(),
            'work_schedule': self.schedule_combo.currentData(),
            'status': self.status_combo.currentData(),
        }

        if self.emp_id:
            resp = self.api.put(f"employees/{self.emp_id}/", data)
        else:
            resp = self.api.post("employees/", data)

        if resp.status_code not in [200, 201]:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")
            return

        # Сохраняем компетенции
        saved_emp_id = self.emp_id or resp.json().get('id')
        selected_ids = [cb.property('competence_id') for cb in self.competence_checkboxes if cb.isChecked()]

        # Получаем текущие компетенции
        comp_resp = self.api.get(f"employee-competences/?employee={saved_emp_id}")
        current_comps = []
        if comp_resp.status_code == 200:
            current_comps = comp_resp.json() if isinstance(comp_resp.json(), list) else comp_resp.json().get('results', [])

        current_ids = {c.get('competence') for c in current_comps}
        current_map = {c.get('competence'): c.get('id') for c in current_comps}

        # Удалить снятые
        for comp_id in current_ids - set(selected_ids):
            if comp_id in current_map:
                self.api.delete(f"employee-competences/{current_map[comp_id]}/")

        # Добавить новые
        for comp_id in set(selected_ids) - current_ids:
            self.api.post("employee-competences/", {
                'employee': saved_emp_id,
                'competence': comp_id
            })

        self.accept()