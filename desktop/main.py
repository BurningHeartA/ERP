import os
import sys
import qtawesome as qta

from auth import LoginDialog

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
from PyQt5.QtCore import Qt, QSize, QPoint 
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QStackedWidget, QShortcut)
from PyQt5.QtGui import QKeySequence

from components.title_bar import CustomTitleBar
from modules.dashboard import DashboardModule
from modules.inventory import InventoryModule
from modules.directories import DirectoriesModule
from modules.clients import ClientsModule
from modules.employees import EmployeesModule
from modules.worklog import WorkLogModule
from modules.warehouse import WarehouseModule
from modules.operations import OperationsModule
from modules.finance import FinanceModule
from modules.orders import OrdersModule
from modules.reports import ReportsModule


# Константы Windows API для отслеживания границ окна
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    
    # Константы зон окна (границы, углы, капшн)
    HTCLIENT = 1
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17

class ErpMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Окно входа
        self.api_client = None
        login = LoginDialog()
        if login.exec_() != LoginDialog.Accepted:
            sys.exit(0)
        self.api_client = login.get_client()

        # Заменяем FramelessWindowHint на более гибкий флаг (убирает рамку, но оставляет системное поведение)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)

        # Для Windows убираем стандартную рамку через WinAPI, сохраняя Aero Snap функции
        # Найти и заменить блок настройки стилей win32 в __init__ (main.py):
        if sys.platform == "win32":
            window_handle = int(self.winId()) 
            style = ctypes.windll.user32.GetWindowLongW(window_handle, -16) # GWL_STYLE
            
            # Включаем WS_THICKFRAME (0x00040000) и WS_MAXIMIZEBOX/MINIMIZEBOX. 
            # Это жизненно важно для работы Aero Snap на уровне Windows!
            style |= 0x00040000 | 0x00010000 | 0x00020000
            # Отключаем только стандартный заголовок ОС (WS_CAPTION)
            style &= ~0x00C00000 
            
            ctypes.windll.user32.SetWindowLongW(window_handle, -16, style)
            
            # Принудительно обновляем рамку окна в системе, чтобы флаги применились
            ctypes.windll.user32.SetWindowPos(window_handle, 0, 0, 0, 0, 0, 0x0020 | 0x0002 | 0x0001 | 0x0004)

            
        self.setWindowTitle("ERP Система ООО Экструзионное оборудование")
        QApplication.setFont(QFont("Segoe UI", 10))
        
        # Ограничиваем минимальный размер окна ERP, чтобы интерфейс не сжимался в ноль
        self.setMinimumSize(900, 600)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        global_layout = QVBoxLayout(main_widget)
        global_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.setSpacing(0)
        
        self.title_bar = CustomTitleBar(self)
        global_layout.addWidget(self.title_bar)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setIconSize(QSize(20, 20))
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        
        self.modules_container = QStackedWidget()
        
        self.init_modules()
        self.sidebar.currentRowChanged.connect(self.modules_container.setCurrentIndex)
        
        workspace_layout = QHBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        workspace_layout.addWidget(self.sidebar)
        workspace_layout.addWidget(self.modules_container, stretch=1)
        
        global_layout.addLayout(workspace_layout)
        
        self.load_stylesheet("styles.qss")
        self.sidebar.setCurrentRow(0)


        
        self.shortcut_reload = QShortcut(QKeySequence("F5"), self)
        self.shortcut_reload.activated.connect(lambda: self.load_stylesheet("styles.qss"))

    def init_modules(self):
        navigation_items = [
            ("Главная", "fa5s.chart-pie", DashboardModule()),
            ("Клиенты", "fa5s.users", ClientsModule(self.api_client)),
            ("Заказы", "fa5s.file-invoice", OrdersModule(self.api_client)),
            ("Сотрудники", "fa5s.id-card", EmployeesModule(self.api_client)),
            ("Табель работ", "fa5s.calendar-check", WorkLogModule(self.api_client)),
            ("Операции", "fa5s.cogs", OperationsModule(self.api_client)),
            ("Склад", "fa5s.boxes", WarehouseModule(self.api_client)),
            ("Финансы", "fa5s.ruble-sign", FinanceModule(self.api_client)),
            ("Аналитика", "fa5s.chart-bar", ReportsModule(self.api_client)),
            ("Справочники", "fa5s.book", DirectoriesModule(self.api_client)),
        ]
        for text, icon_name, widget_instance in navigation_items:
            item = QListWidgetItem()
            item.setText(f"  {text}")
            item.setIcon(qta.icon(icon_name, color="#555555", color_active="#0067B8"))
            item.setSizeHint(QSize(0, 45))
            self.sidebar.addItem(item)
            self.modules_container.addWidget(widget_instance)

    def load_stylesheet(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Предупреждение: Файл стилей {filename} не найден.")

    # Метод для перехвата состояния окна и корректной отрисовки скругленных углов
    def changeEvent(self, event):
        # Проверяем, изменилось ли состояние окна (например, развернулось/свернулось)
        if event.type() == event.WindowStateChange:
            # Если окно БОЛЬШЕ НЕ развернуто на весь экран (например, его сдернули руками)
            if not self.isMaximized() and sys.platform == "win32":
                window_handle = int(self.winId())
                
                # Посылаем операционной системе Windows сигнал обновить неклиентскую область.
                # Флаг 0x0020 (SWP_FRAMECHANGED) заставит DWM мгновенно вернуть 
                # скругленные углы и тени, исправляя баг перетаскивания.
                ctypes.windll.user32.SetWindowPos(
                    window_handle, 0, 0, 0, 0, 0, 
                    0x0020 | 0x0002 | 0x0001 | 0x0004  # FrameChanged | Move | Size | NoZOrder
                )
                
                # Обновляем иконку кнопки развертывания в нашей панели на квадрат
                self.title_bar.btn_maximize.setIcon(qta.icon("fa5s.window-maximize", color="#333333"))
                
        super().changeEvent(event)

    # --- САМАЯ ВАЖНАЯ ЧАСТЬ: Возврат стрелочек изменения размера и Split Screen ---
    def nativeEvent(self, event_type, message):
        if sys.platform != "win32" or event_type != b"windows_generic_MSG":
            return super().nativeEvent(event_type, message)
            
        msg = wintypes.MSG.from_address(int(message))

        # Найти и заменить блок WM_NCCALCSIZE в nativeEvent (main.py):
        if msg.message == 0x0083: # WM_NCCALCSIZE
            if msg.wParam:
                # Если окно развернуто на весь экран, мы не делаем дополнительных отступов.
                # Если окно в обычном режиме, мы компенсируем системные пиксели рамки Windows,
                # чтобы интерфейс прижимался ровно к краям экрана без зазоров.
                if self.isMaximized():
                    return True, 0
                
                # Получаем структуру RECT из lParam
                rect = ctypes.cast(msg.lParam, ctypes.POINTER(wintypes.RECT)).contents
                
                # Запрашиваем у ОС стандартную толщину невидимых рамок
                # Это уберет зазор сверху и по бокам при перетаскивании к краям
                border_x = ctypes.windll.user32.GetSystemMetrics(32) # SM_CXSIZEFRAME
                border_y = ctypes.windll.user32.GetSystemMetrics(33) # SM_CYSIZEFRAME
                padd = ctypes.windll.user32.GetSystemMetrics(92)    # SM_CXPADDEDBORDER
                
                # Срезаем системную неклиентскую рамку, делая её частью нашего интерфейса
                rect.left += border_x + padd
                rect.right -= border_x + padd
                rect.bottom -= border_y + padd
                # Верхнюю линию выравниваем идеально в ноль, чтобы убрать зазор над кнопками
                rect.top += 0 
                
                return True, 0


        # Заменить блок WM_NCHUTTEST в nativeEvent (main.py)
        if msg.message == 0x0084: # WM_NCHUTTEST
            if self.isMaximized():
                return True, HTCLIENT
                
            # Получаем экранные координаты мыши из параметров сообщения
            x = msg.lParam & 0xFFFF
            # Обработка отрицательных координат на дополнительных мониторах
            if x >= 32768: x -= 65536
            y = (msg.lParam >> 16) & 0xFFFF
            if y >= 32768: y -= 65536
            
            # Переводим в локальные координаты окна
            local_pos = self.mapFromGlobal(QPoint(x, y))
            lx = local_pos.x()
            ly = local_pos.y()
            
            # Чувствительность зон для изменения размера
            padding = 5 
            is_left = lx < padding
            is_right = lx > self.width() - padding
            is_top = ly < padding # Добавлено для отслеживания верха
            is_bottom = ly > self.height() - padding
            
            # Добавлена проверка верхних углов и верхней грани
            if is_top and is_left: return True, HTTOPLEFT
            if is_top and is_right: return True, HTTOPRIGHT
            if is_bottom and is_left: return True, HTBOTTOMLEFT
            if is_bottom and is_right: return True, HTBOTTOMRIGHT
            if is_left: return True, HTLEFT
            if is_right: return True, HTRIGHT
            if is_top: return True, HTTOP # Возвращает стрелочку вверх
            if is_bottom: return True, HTBOTTOM
            
            return True, HTCLIENT

        # Заменить старый блок WM_MOVING в nativeEvent (main.py)
        elif msg.message == 0x0216: # WM_MOVING
            rect = ctypes.cast(msg.lParam, ctypes.POINTER(wintypes.RECT)).contents
            
            desktop = QApplication.desktop()
            screen_rect = desktop.availableGeometry(self)
            
            win_width = rect.right - rect.left
            win_height = rect.bottom - rect.top
            
            # Удержание по вертикали
            if rect.top < screen_rect.top():
                rect.top = screen_rect.top()
                rect.bottom = rect.top + win_height
            if rect.top > screen_rect.bottom() - 55:
                rect.top = screen_rect.bottom() - 55
                rect.bottom = rect.top + win_height
                
            # Зоны безопасности в пикселях
            title_zone_width = 180   # Иконка + Текст слева
            buttons_zone_width = 165 # Кнопки управления справа
            
            # Ограничение ВЛЕВО: правые кнопки не должны уйти за левый край экрана
            if rect.right < screen_rect.left() + buttons_zone_width:
                rect.right = screen_rect.left() + buttons_zone_width
                rect.left = rect.right - win_width
                
            # Ограничение ВПРАВО: левое название/иконка не должны уйти за правый край экрана
            if rect.left > screen_rect.right() - title_zone_width:
                rect.left = screen_rect.right() - title_zone_width
                rect.right = rect.left + win_width
                
            return True, 0

        return super().nativeEvent(event_type, message)

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    window = ErpMainWindow()
    window.showMaximized()
    sys.exit(app.exec_())