from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class DashboardModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        title = QLabel("Панель управления")
        title.setProperty("class", "ModuleTitle") # Используем класс из QSS
        
        layout.addWidget(title)
        layout.addWidget(QLabel("Здесь пока пусто"))
        layout.addStretch()