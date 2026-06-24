from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox, QComboBox
)

from PyQt5.QtCore import Qt
from widgets import populate_table

class DirectoriesModule(QWidget):
    COLUMN_NAMES = {
        'name': 'Наименование',
        'coefficient': 'Коэффициент',
        'description': 'Описание',
        'processing_type': 'Тип обработки',
        'purchase_cost': 'Стоимость',
        'purchase_date': 'Дата приобретения',
        'power_rating': 'Мощность (кВт)',
        'status': 'Статус',
        'material_type': 'Тип материала',
        'material_kind': 'Вид материала',
        'stock_form': 'Тип проката',
        'unit_price': 'Цена за ед.',
        'notes': 'Примечания',
        'price_per_unit': 'Цена за ед.',
        'quantity': 'Количество',
        'amount': 'Сумма',
        'total_price': 'Итого',
    }


    def __init__(self, api_client):
        super().__init__()
        self.api = api_client
        self.current_endpoint = None
        self.current_data = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Справочники")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Выбор справочника
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Выберите справочник:"))

        self.directory_combo = QComboBox()
        self.directory_combo.addItem("Должности", "positions")
        self.directory_combo.addItem("Графики работы", "work-schedules")
        self.directory_combo.addItem("Компетенции", "competences")
        self.directory_combo.addItem("Категории работ", "work-categories")
        self.directory_combo.addItem("Типы операций", "operation-types")
        self.directory_combo.addItem("Категории расходов", "expense-categories")
        self.directory_combo.addItem("Изделия", "products")
        self.directory_combo.addItem("Оборудование", "equipment")
        self.directory_combo.addItem("Материалы", "materials")
        self.directory_combo.currentIndexChanged.connect(self.load_directory)
        selector_layout.addWidget(self.directory_combo)
        selector_layout.addStretch()

        btn_add = QPushButton("+ Добавить")
        btn_add.clicked.connect(self.add_item)
        selector_layout.addWidget(btn_add)

        layout.addWidget(title)
        layout.addLayout(selector_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # сортировочка
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel) # прокрутка
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        layout.addWidget(self.table)

        # Кнопки действий
        action_layout = QHBoxLayout()
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_item)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_item)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(lambda: self.load_directory())
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addStretch()
        action_layout.addWidget(btn_refresh)
        layout.addLayout(action_layout)

        self.load_directory()

    # def load_directory(self):
    #     self.table.setSortingEnabled(False)
    #     self.table.clear()
    #     self.table.setRowCount(0)
    #     self.table.setColumnCount(0)
    #     endpoint = self.directory_combo.currentData()
    #     self.current_endpoint = endpoint
    #     resp = self.api.get(endpoint + "/")
    #     if resp.status_code == 200:
    #         self.current_data = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
    #         self.populate_table()
    #     else:
    #         self.current_data = []
    #         self.populate_table()
    #         QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {resp.status_code}")
    def load_directory(self):
        endpoint = self.directory_combo.currentData()
        self.current_endpoint = endpoint
        resp = self.api.get(endpoint + "/")
        if resp.status_code == 200:
            self.current_data = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
            # Берём только те колонки, которые есть в данных
            if self.current_data:
                available_keys = set(self.current_data[0].keys())
                filtered_columns = {k: v for k, v in self.COLUMN_NAMES.items() if k in available_keys}
            else:
                filtered_columns = self.COLUMN_NAMES
            populate_table(self.table, self.current_data, filtered_columns)
        else:
            self.current_data = []
            populate_table(self.table, [], {})
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {resp.status_code}")
    
    def populate_table(self):
        populate_table(self.table, self.current_data, self.COLUMN_NAMES)

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return None
        return self.current_data[row].get('id')

    def add_item(self):
        dialog = DirectoryItemDialog(self.current_endpoint, self.api)
        if dialog.exec_() == QDialog.Accepted:
            self.load_directory()

    def edit_item(self):
        item_id = self.get_selected_id()
        if not item_id:
            return
        dialog = DirectoryItemDialog(self.current_endpoint, self.api, item_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_directory()

    def delete_item(self):
        item_id = self.get_selected_id()
        if not item_id:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить запись?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            resp = self.api.delete(f"{self.current_endpoint}/{item_id}/")
            if resp.status_code == 204:
                self.load_directory()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {resp.status_code}")


class DirectoryItemDialog(QDialog):
    def __init__(self, endpoint, api_client, item_id=None):
        super().__init__()
        self.endpoint = endpoint
        self.api = api_client
        self.item_id = item_id
        self.fields = {}
        self.setWindowTitle("Редактирование записи" if item_id else "Новая запись")
        self.setFixedWidth(400)
        self.init_ui()
        if item_id:
            self.load_item()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        # Определяем поля в зависимости от endpoint
        field_config = {
            'positions': [('name', 'Наименование', 'text'), ('coefficient', 'Коэффициент', 'decimal')],
            'work-schedules': [('name', 'Наименование', 'text'), ('coefficient', 'Коэффициент', 'decimal')],
            'competences': [('name', 'Наименование', 'text'), ('coefficient', 'Коэффициент премии', 'decimal')],
            'work-categories': [('name', 'Наименование', 'text')],
            'operation-types': [('name', 'Наименование', 'text')],
            'expense-categories': [('name', 'Наименование', 'text')],
            'products': [('name', 'Наименование', 'text'), ('description', 'Описание', 'text')],
            'equipment': [
                ('name', 'Наименование', 'text'),
                ('processing_type', 'Тип обработки', 'text'),
                ('purchase_cost', 'Стоимость', 'decimal'),
                ('power_rating', 'Мощность (кВт)', 'decimal'),
            ],
            'materials': [
                ('name', 'Наименование', 'text'),
                ('material_type', 'Тип (raw/consumable)', 'text'),
                ('unit_price', 'Цена', 'decimal'),
            ],
        }

        for field_name, label, field_type in field_config.get(self.endpoint, [('name', 'Наименование', 'text')]):
            if field_type == 'text':
                widget = QLineEdit()
            elif field_type == 'decimal':
                widget = QDoubleSpinBox()
                widget.setMaximum(9999999.99)
                widget.setDecimals(2)
            form.addRow(label, widget)
            self.fields[field_name] = widget

        layout.addLayout(form)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def load_item(self):
        resp = self.api.get(f"{self.endpoint}/{self.item_id}/")
        if resp.status_code == 200:
            data = resp.json()
            for field_name, widget in self.fields.items():
                value = data.get(field_name, "")
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value) if value else 0)

    def save(self):
        data = {}
        for field_name, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text()
            elif isinstance(widget, QDoubleSpinBox):
                data[field_name] = widget.value()

        if self.item_id:
            resp = self.api.put(f"{self.endpoint}/{self.item_id}/", data)
        else:
            resp = self.api.post(f"{self.endpoint}/", data)

        if resp.status_code in [200, 201]:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {resp.status_code}\n{resp.text}")