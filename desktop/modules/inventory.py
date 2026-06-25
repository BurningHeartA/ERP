import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QAbstractItemView, QHeaderView)

class InventoryModule(QWidget):
    def __init__(self):
        super().__init__()
        
        # Главный макет модуля с хорошими отступами
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 1. ЗАГОЛОВОК И ПАНЕЛЬ ИНСТРУМЕНТОВ
        header_layout = QHBoxLayout()
        
        title = QLabel("Складской учет")
        title.setProperty("class", "ModuleTitle") # Берет шрифт из QSS
        
        # Поле поиска товаров
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Поиск по названию или артикулу...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_table) # Живой фильтр
        
        # Современная кнопка добавления товара
        add_btn = QPushButton(" Добавить товар")
        add_btn.setObjectName("PrimaryButton") # Будет синей из глобального стиля
        add_btn.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # 2. ТАБЛИЦА ТОВАРОВ
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Артикул", "Наименование товара", "Остаток", "Цена, руб."])
        
        # Настройки поведения таблицы (делаем её интерактивной, но защищенной)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Запрет редактирования прямо в ячейке
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # Выделять строку целиком, а не ячейку
        self.table.setSelectionMode(QAbstractItemView.SingleSelection) # Выделять только одну строку за раз
        self.table.setShowGrid(True) # Включаем сетку, но цвет настроен в QSS
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False) # Скрываем номера строк слева
        
        # Настройка растягивания колонок под размеры экрана
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Артикул по размеру текста
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Название заберет ВСЁ свободное место
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Остаток по тексту
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Цена по тексту
        
        layout.addWidget(self.table)
        
        # Имитируем получение данных от бэкенда Django
        # self.load_fake_django_data()

    def load_fake_django_data(self):
        """
        Сюда мы позже вставим requests.get() от Django.
        Сейчас функция принимает массив словарей — точную копию JSON от бэкенда.
        """
        json_response = [
            {"sku": "10024", "name": "Кабель медный ВВГнг-LS 3х2.5", "qty": 450, "price": 115.00},
            {"sku": "10025", "name": "Автоматический выключатель 16A Schneider", "qty": 32, "price": 420.50},
            {"sku": "10026", "name": "Розетка скрытая одинарная белая Leyard", "qty": 118, "price": 185.00},
            {"sku": "10027", "name": "Светодиодный светильник Armstrong 36W", "qty": 0, "price": 1250.00},
            {"sku": "10028", "name": "Подрозетник пластиковый для бетона", "qty": 1500, "price": 18.20},
        ]
        
        self.table.setRowCount(len(json_response))
        
        for row_idx, item in enumerate(json_response):
            # Создаем ячейки
            sku_item = QTableWidgetItem(item["sku"])
            name_item = QTableWidgetItem(item["name"])
            qty_item = QTableWidgetItem(str(item["qty"]))
            price_item = QTableWidgetItem(f"{item['price']:.2f}")
            
            # Стилизуем текст внутри ячеек остатка и цены (выравнивание по правому краю)
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Если товара нет на складе (qty == 0), сделаем текст предупреждающе красным
            if item["qty"] == 0:
                qty_item.setForeground(Qt.red)
                qty_item.setText("Нет на складе")
            
            # Заполняем строку таблицы
            self.table.setItem(row_idx, 0, sku_item)
            self.table.setItem(row_idx, 1, name_item)
            self.table.setItem(row_idx, 2, qty_item)
            self.table.setItem(row_idx, 3, price_item)

    def filter_table(self):
        """Логика живого поиска: скрывает строки, не подходящие под запрос"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            # Ищем совпадение в Артикуле (колонка 0) или Названии (колонка 1)
            sku = self.table.item(row, 0).text().lower()
            name = self.table.item(row, 1).text().lower()
            
            if search_text in sku or search_text in name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)