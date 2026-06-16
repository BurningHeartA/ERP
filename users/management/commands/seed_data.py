from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from datetime import date, datetime, timedelta
import random
from calendar import monthrange

from users.models import UserProfile
from directories.models import (
    Position, WorkSchedule, Competence, WorkCategory,
    OperationType, ExpenseCategory, Product, Equipment, Material
)
from clients.models import Customer
from employees.models import Employee, EmployeeCompetence
from orders.models import Request, Order
from worklog.models import WorkLog, WorkEntry
from operations.models import Operation
from warehouse.models import InventoryRecord
from finance.models import Income, Expense
from files.models import File


class Command(BaseCommand):
    help = 'Заполнение базы тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данных...\n')

        # ============================================================
        # 1. ДОЛЖНОСТИ
        # ============================================================
        positions = {
            'director': Position.objects.create(name='Директор', coefficient=3.00),
            'miller': Position.objects.create(name='Фрезеровщик', coefficient=2.50),
            'turner': Position.objects.create(name='Токарь', coefficient=2.35),
            'locksmith': Position.objects.create(name='Слесарь', coefficient=2.00),
            'erosionist': Position.objects.create(name='Эрозионист', coefficient=2.75),
            'handyman': Position.objects.create(name='Разнорабочий', coefficient=1.50),
        }
        self.stdout.write('  Должности созданы (6)')

        # ============================================================
        # 2. ГРАФИКИ РАБОТЫ
        # ============================================================
        schedules = {
            'flexible': WorkSchedule.objects.create(name='Гибкий', coefficient=0.95),
            'strict': WorkSchedule.objects.create(name='Жёсткий', coefficient=1.00),
            'irregular': WorkSchedule.objects.create(name='Ненормированный', coefficient=1.15),
        }
        self.stdout.write('  Графики работы созданы (3)')

        # ============================================================
        # 3-4. ДИРЕКТОР — СУПЕРПОЛЬЗОВАТЕЛЬ И СОТРУДНИК
        # ============================================================
        director_user = User.objects.create_superuser(
            username='director',
            password='director',
            email='director@gmail.com',
            first_name='Марат',
            last_name='Гришков'
        )
        UserProfile.objects.create(user=director_user, is_employee=True, is_director=True)

        director_emp = Employee.objects.create(
            user=director_user,
            position=positions['director'],
            work_schedule=schedules['irregular'],
            last_name='Гришков',
            first_name='Марат',
            middle_name='Алексеевич',
            birth_date='1962-04-17',
            passport_number='0100100100',
            phone='+7 (900) 000-00-01',
            email='director@gmail.com',
            contract_number='00000001',
            hire_date='2018-01-10',
            status='hired'
        )
        self.stdout.write('  Директор создан')

        # ============================================================
        # 5. СОТРУДНИКИ (10 человек)
        # ============================================================
        employee_data = [
            {'last': 'Антонов', 'first': 'Сергей', 'middle': 'Петрович', 'pos': 'miller', 'sched': 'strict', 'birth': '1988-03-15', 'passport': '0200200201', 'contract': '00000002', 'hire': '2020-02-01'},
            {'last': 'Борисов', 'first': 'Андрей', 'middle': 'Викторович', 'pos': 'miller', 'sched': 'strict', 'birth': '1991-07-22', 'passport': '0200200202', 'contract': '00000003', 'hire': '2020-05-15'},
            {'last': 'Волков', 'first': 'Дмитрий', 'middle': 'Сергеевич', 'pos': 'turner', 'sched': 'strict', 'birth': '1985-11-30', 'passport': '0200200203', 'contract': '00000004', 'hire': '2019-09-01'},
            {'last': 'Гусев', 'first': 'Алексей', 'middle': 'Иванович', 'pos': 'turner', 'sched': 'flexible', 'birth': '1993-01-18', 'passport': '0200200204', 'contract': '00000005', 'hire': '2021-03-10'},
            {'last': 'Дятлов', 'first': 'Максим', 'middle': 'Андреевич', 'pos': 'locksmith', 'sched': 'strict', 'birth': '1990-06-05', 'passport': '0200200205', 'contract': '00000006', 'hire': '2020-08-20'},
            {'last': 'Ежов', 'first': 'Николай', 'middle': 'Дмитриевич', 'pos': 'locksmith', 'sched': 'strict', 'birth': '1987-09-14', 'passport': '0200200206', 'contract': '00000007', 'hire': '2019-11-05'},
            {'last': 'Жаров', 'first': 'Игорь', 'middle': 'Михайлович', 'pos': 'erosionist', 'sched': 'strict', 'birth': '1992-04-28', 'passport': '0200200207', 'contract': '00000008', 'hire': '2021-01-15'},
            {'last': 'Зимин', 'first': 'Владимир', 'middle': 'Александрович', 'pos': 'erosionist', 'sched': 'strict', 'birth': '1989-12-03', 'passport': '0200200208', 'contract': '00000009', 'hire': '2020-06-10'},
            {'last': 'Исаев', 'first': 'Роман', 'middle': 'Владимирович', 'pos': 'handyman', 'sched': 'flexible', 'birth': '1995-08-20', 'passport': '0200200209', 'contract': '00000010', 'hire': '2022-02-01'},
            {'last': 'Козлов', 'first': 'Евгений', 'middle': 'Олегович', 'pos': 'handyman', 'sched': 'flexible', 'birth': '1994-10-12', 'passport': '0200200210', 'contract': '00000011', 'hire': '2021-07-01'},
        ]

        employees = []
        for i, data in enumerate(employee_data):
            username = f"{self._translit(data['last']).lower()}_{self._translit(data['first'][0]).lower()}{self._translit(data['middle'][0]).lower()}"
            user = User.objects.create_user(
                username=username,
                password='employee123',
                first_name=data['first'],
                last_name=data['last']
            )
            UserProfile.objects.create(user=user, is_employee=True)

            emp = Employee.objects.create(
                user=user,
                position=positions[data['pos']],
                work_schedule=schedules[data['sched']],
                last_name=data['last'],
                first_name=data['first'],
                middle_name=data['middle'],
                birth_date=data['birth'],
                passport_number=data['passport'],
                phone=f'+7 (900) 000-00{i+2:02d}',
                email=f'{username}@mail.ru',
                contract_number=data['contract'],
                hire_date=data['hire'],
                status='hired'
            )
            employees.append(emp)

        all_employees = [director_emp] + employees
        self.stdout.write('  Сотрудники созданы (10 + директор)')

        # ============================================================
        # 6. СПРАВОЧНИКИ
        # ============================================================
        # Компетенции
        competences = [
            Competence.objects.create(name='Сварщик', coefficient=0.10),
            Competence.objects.create(name='Оператор ЧПУ', coefficient=0.07),
            Competence.objects.create(name='Эрозионист', coefficient=0.07),
            Competence.objects.create(name='Системный администратор', coefficient=0.05),
            Competence.objects.create(name='Стропальщик', coefficient=0.05),
            Competence.objects.create(name='Наладчик', coefficient=0.06),
            Competence.objects.create(name='Контролёр ОТК', coefficient=0.04),
            Competence.objects.create(name='Электрик', coefficient=0.06),
            Competence.objects.create(name='Термист', coefficient=0.07),
            Competence.objects.create(name='Заточник', coefficient=0.04),
        ]

        # Категории работ
        work_categories = [
            WorkCategory.objects.create(name='3D-моделирование'),
            WorkCategory.objects.create(name='Подготовка управляющей программы'),
            WorkCategory.objects.create(name='Фрезерная обработка'),
            WorkCategory.objects.create(name='Токарная обработка'),
            WorkCategory.objects.create(name='Электроэрозионная обработка'),
            WorkCategory.objects.create(name='Слесарная обработка'),
            WorkCategory.objects.create(name='Термическая обработка'),
            WorkCategory.objects.create(name='Сварочные работы'),
            WorkCategory.objects.create(name='Контроль качества'),
            WorkCategory.objects.create(name='Уборка рабочего места'),
        ]

        # Оборудование
        equipment_list = [
            Equipment.objects.create(name='Фрезерный станок Haas VF-2', processing_type='milling', purchase_cost=3500000, purchase_date='2020-03-15', power_rating=15.00),
            Equipment.objects.create(name='Фрезерный станок Haas VF-3', processing_type='milling', purchase_cost=4200000, purchase_date='2021-06-10', power_rating=18.00),
            Equipment.objects.create(name='Токарный станок 16К20', processing_type='turning', purchase_cost=1500000, purchase_date='2019-03-15', power_rating=7.50),
            Equipment.objects.create(name='Токарный станок 16К25', processing_type='turning', purchase_cost=1800000, purchase_date='2020-09-01', power_rating=10.00),
            Equipment.objects.create(name='Электроэрозионный станок Sodick', processing_type='erosion', purchase_cost=5000000, purchase_date='2021-09-20', power_rating=10.00),
            Equipment.objects.create(name='Электроэрозионный станок AGIE', processing_type='erosion', purchase_cost=3800000, purchase_date='2019-06-15', power_rating=8.00),
            Equipment.objects.create(name='Сверлильный станок 2Н135', processing_type='drilling', purchase_cost=600000, purchase_date='2018-05-10', power_rating=4.00),
            Equipment.objects.create(name='Шлифовальный станок 3Л722', processing_type='grinding', purchase_cost=950000, purchase_date='2020-11-20', power_rating=5.50),
            Equipment.objects.create(name='Сварочный аппарат Kemppi', processing_type='welding', purchase_cost=350000, purchase_date='2022-01-15', power_rating=8.00),
            Equipment.objects.create(name='Печь термическая', processing_type='welding', purchase_cost=800000, purchase_date='2018-11-05', power_rating=20.00),
        ]

        # Типы операций
        operation_types = [
            OperationType.objects.create(name='обработка'),
            OperationType.objects.create(name='техобслуживание'),
            OperationType.objects.create(name='уборка'),
            OperationType.objects.create(name='замена инструмента'),
            OperationType.objects.create(name='наладка'),
        ]

        # Категории расходов
        expense_categories = [
            ExpenseCategory.objects.create(name='Закупка материалов'),
            ExpenseCategory.objects.create(name='Заработная плата'),
            ExpenseCategory.objects.create(name='Аренда помещения'),
            ExpenseCategory.objects.create(name='Коммунальные услуги'),
            ExpenseCategory.objects.create(name='Ремонт и обслуживание оборудования'),
            ExpenseCategory.objects.create(name='Налоги и сборы'),
            ExpenseCategory.objects.create(name='Транспортные расходы'),
            ExpenseCategory.objects.create(name='Реклама и маркетинг'),
            ExpenseCategory.objects.create(name='Охрана труда'),
            ExpenseCategory.objects.create(name='Канцелярские расходы'),
        ]

        # Изделия
        products = [
            Product.objects.create(name='Фреза дробилки D150-08', description='Сталь 40Х, термообработка HRC 48-52'),
            Product.objects.create(name='Вал привода 60х300', description='Сталь 45, допуск +-0.05 мм'),
            Product.objects.create(name='Кронштейн крепления K-01', description='Сталь 3, сварная конструкция'),
            Product.objects.create(name='Втулка распорная 25х40', description='Бронза БРаЖ-7'),
            Product.objects.create(name='Плита опорная 200х300х20', description='Сталь 45, фрезеровка'),
            Product.objects.create(name='Шестерня зубчатая Z-32', description='Сталь 40Х, зубофрезерная обработка'),
            Product.objects.create(name='Корпус подшипника D120', description='Чугун СЧ20'),
            Product.objects.create(name='Вал-шестерня 45х200', description='Сталь 18ХГТ, цементация'),
            Product.objects.create(name='Фланец переходной D80-D50', description='Сталь 09Г2С'),
            Product.objects.create(name='Направляющая 30х40х500', description='Сталь 40Х, закалка'),
            Product.objects.create(name='Прижимная планка 20х60х100', description='Сталь 45'),
            Product.objects.create(name='Шпонка 10х8х40', description='Сталь 45'),
        ]

        # Материалы
        materials = [
            Material.objects.create(name='Сталь-45 лист 1500х600х10', material_type='raw', material_kind='Сталь-45', stock_form='лист 1500х600х10', unit_price=1200),
            Material.objects.create(name='Сталь-40Х пруток 30х1000', material_type='raw', material_kind='Сталь-40Х', stock_form='пруток 30х1000', unit_price=800),
            Material.objects.create(name='Сталь-40Х пруток 50х1000', material_type='raw', material_kind='Сталь-40Х', stock_form='пруток 50х1000', unit_price=1500),
            Material.objects.create(name='Сталь-3 лист 1500х600х5', material_type='raw', material_kind='Сталь-3', stock_form='лист 1500х600х5', unit_price=600),
            Material.objects.create(name='БРаЖ-7 пруток 25х1000', material_type='raw', material_kind='БРаЖ-7', stock_form='пруток 25х1000', unit_price=3500),
            Material.objects.create(name='Чугун СЧ20 отливка', material_type='raw', material_kind='Чугун СЧ20', stock_form='отливка', unit_price=400),
            Material.objects.create(name='Сталь 18ХГТ пруток 45х1000', material_type='raw', material_kind='Сталь 18ХГТ', stock_form='пруток 45х1000', unit_price=2000),
            Material.objects.create(name='Сталь 09Г2С лист 1500х600х8', material_type='raw', material_kind='Сталь 09Г2С', stock_form='лист 1500х600х8', unit_price=950),
            Material.objects.create(name='СОЖ концентрат', material_type='consumable', unit_price=500),
            Material.objects.create(name='Перчатки порезостойкие', material_type='consumable', unit_price=150),
            Material.objects.create(name='Очки защитные', material_type='consumable', unit_price=200),
            Material.objects.create(name='Масло индустриальное И-40', material_type='consumable', unit_price=350),
            Material.objects.create(name='Электроды сварочные УОНИ 13/55', material_type='consumable', unit_price=250),
            Material.objects.create(name='Круги отрезные 125х1.6', material_type='consumable', unit_price=80),
            Material.objects.create(name='Сверло спиральное D10', material_type='consumable', unit_price=300),
        ]
        self.stdout.write('  Справочники созданы')

        # ============================================================
        # 7. КОМПЕТЕНЦИИ СОТРУДНИКОВ
        # ============================================================
        # Директор
        EmployeeCompetence.objects.create(employee=director_emp, competence=competences[3])  # Сисадмин

        # Половина сотрудников (5 человек) с компетенциями от 1 до 3
        competence_assignments = [
            (employees[0], [competences[1], competences[5]]),  # Антонов: ЧПУ, Наладчик
            (employees[1], [competences[1], competences[7]]),  # Борисов: ЧПУ, Электрик
            (employees[3], [competences[0], competences[8]]),  # Гусев: Сварщик, Термист
            (employees[5], [competences[4], competences[6], competences[9]]),  # Ежов: Стропальщик, Контролёр, Заточник
            (employees[6], [competences[2]]),  # Жаров: Эрозионист
        ]
        for emp, comp_list in competence_assignments:
            for comp in comp_list:
                EmployeeCompetence.objects.create(employee=emp, competence=comp)
        self.stdout.write('  Компетенции сотрудников созданы')

        # ============================================================
        # 8. КЛИЕНТЫ
        # ============================================================
        # 5 клиентов НЕ сотрудников
        client_users = []
        client_names = [
            ('ООО "Судоремонт"', 'ship@mail.ru', '+7 (900) 100-00-01', 'partner_company'),
            ('ООО "АгроТех"', 'agro@mail.ru', '+7 (900) 100-00-02', 'farpost'),
            ('ИП "Металлообработка"', 'metal@mail.ru', '+7 (900) 100-00-03', 'avito'),
            ('ООО "ДетальСервис"', 'detail@mail.ru', '+7 (900) 100-00-04', 'company_website'),
            ('ООО "СтройМаш"', 'stroymash@mail.ru', '+7 (900) 100-00-05', 'personal_referral'),
        ]
        clients = []
        for i, (name, email, phone, source) in enumerate(client_names):
            username = f'client{i+1}'
            user = User.objects.create_user(username=username, password='client123', email=email)
            UserProfile.objects.create(user=user)
            cust = Customer.objects.create(
                user=user,
                name=name,
                phone=phone,
                email=email,
                source=source
            )
            clients.append(cust)
            client_users.append(user)

        # 3 клиента из сотрудников
        emp_clients = []
        for emp in employees[:3]:  # Первые три сотрудника
            cust = Customer.objects.create(
                user=emp.user,
                name=emp.full_name,
                phone=emp.phone,
                email=emp.email,
                source='personal_referral'
            )
            emp_clients.append(cust)

        all_clients = clients + emp_clients
        self.stdout.write('  Клиенты созданы (5 внешних + 3 сотрудника)')

        # ============================================================
        # 9. ЗАЯВКИ
        # ============================================================
        request_descriptions = [
            {'desc': 'Изготовить фрезу дробилки D150-08, 10 шт. Чертежи прилагаются.', 'product': 'Фреза дробилки D150-08', 'qty': 10, 'deadline': '2026-05-20', 'status': 'approved'},
            {'desc': 'Изготовить вал привода 60х300, 2 шт.', 'product': 'Вал привода 60х300', 'qty': 2, 'deadline': '2026-05-25', 'status': 'approved'},
            {'desc': 'Кронштейны крепления K-01, 20 шт.', 'product': 'Кронштейн крепления K-01', 'qty': 20, 'deadline': '2026-06-01', 'status': 'approved'},
            {'desc': 'Втулки распорные 25х40, 50 шт.', 'product': 'Втулка распорная 25х40', 'qty': 50, 'deadline': '2026-06-10', 'status': 'approved'},
            {'desc': 'Плита опорная 200х300х20, 5 шт.', 'product': 'Плита опорная 200х300х20', 'qty': 5, 'deadline': '2026-05-30', 'status': 'approved'},
            {'desc': 'Шестерня зубчатая Z-32, 3 шт.', 'product': 'Шестерня зубчатая Z-32', 'qty': 3, 'deadline': '2026-06-05', 'status': 'approved'},
            {'desc': 'Корпус подшипника D120, 2 шт.', 'product': 'Корпус подшипника D120', 'qty': 2, 'deadline': '2026-06-15', 'status': 'in_review'},
            {'desc': 'Вал-шестерня 45х200, 4 шт.', 'product': 'Вал-шестерня 45х200', 'qty': 4, 'deadline': '2026-05-28', 'status': 'approved'},
            {'desc': 'Фланец переходной D80-D50, 10 шт.', 'product': 'Фланец переходной D80-D50', 'qty': 10, 'deadline': '2026-06-08', 'status': 'new'},
            {'desc': 'Направляющая 30х40х500, 6 шт.', 'product': 'Направляющая 30х40х500', 'qty': 6, 'deadline': '2026-06-12', 'status': 'approved'},
            {'desc': 'Прижимная планка 20х60х100, 15 шт.', 'product': 'Прижимная планка 20х60х100', 'qty': 15, 'deadline': '2026-05-22', 'status': 'rejected'},
            {'desc': 'Шпонка 10х8х40, 100 шт.', 'product': 'Шпонка 10х8х40', 'qty': 100, 'deadline': '2026-05-18', 'status': 'approved'},
            {'desc': 'Комплект деталей по чертежам заказчика (спецификация прилагается)', 'product': 'Шестеренка m5 z13', 'qty': 3, 'deadline': '2026-06-20', 'status': 'new'},
            {'desc': 'Доработка фрезы D150-08 (усиленная конструкция)', 'product': 'Фреза дробилки D150-08', 'qty': 5, 'deadline': '2026-06-18', 'status': 'in_review'},
            {'desc': 'Срочное изготовление вала привода 60х300 по образцу', 'product': 'Вал привода 60х300', 'qty': 1, 'deadline': '2026-05-15', 'status': 'approved'},
        ]

        requests = []
        request_ct = ContentType.objects.get_for_model(Request)
        for i, client in enumerate(all_clients):
            num_requests = random.randint(1, 3)
            for j in range(num_requests):
                idx = (i * 3 + j) % len(request_descriptions)
                rd = request_descriptions[idx]
                req = Request.objects.create(
                    customer=client,
                    description=rd['desc'],
                    product_name=rd['product'],
                    quantity=rd['qty'],
                    desired_deadline=rd['deadline'],
                    status=rd['status']
                )
                requests.append(req)

        self.stdout.write(f'  Заявки созданы ({len(requests)})')

        # Прикрепляем файлы к половине заявок
        file_texts = [
            ('техзадание_фреза.txt', 'Техническое задание на изготовление фрезы дробилки D150-08.\nМатериал: Сталь 40Х.\nТермообработка: закалка HRC 48-52.\nДопуски: +-0.05 мм.\nКоличество: 10 шт.'),
            ('техзадание_вал.txt', 'Техническое задание на изготовление вала привода 60х300.\nМатериал: Сталь 45.\nДлина: 300 мм, диаметр: 60 мм.\nДопуск радиального биения: 0.02 мм.'),
            ('спецификация.txt', 'Спецификация к заказу:\n1. Плита опорная 200х300х20 — 5 шт.\n2. Кронштейн крепления K-01 — 20 шт.\nМатериал: Сталь 3.\nСварные швы по ГОСТ 5264-80.'),
        ]
        half = len(requests) // 2
        for req in requests[:half]:
            num_files = random.randint(1, 3)
            for k in range(num_files):
                ft = file_texts[k % len(file_texts)]
                File.objects.create(
                    content_type=request_ct,
                    object_id=req.id,
                    file=ContentFile(ft[1].encode('utf-8'), name=ft[0]),
                    original_name=ft[0],
                    file_category='drawing' if 'техзадание' in ft[0] else 'other',
                    uploaded_by=req.customer.user if req.customer.user else director_user
                )
        self.stdout.write('  Файлы заявок прикреплены')

        # ============================================================
        # 10. ЗАКАЗЫ
        # ============================================================
        orders = []

        # Заказы, связанные с заявками (10-15 шт)
        approved_requests = [r for r in requests if r.status == 'approved']
        for i, req in enumerate(approved_requests[:12]):
            product = products[i % len(products)]
            order = Order.objects.create(
                request=req,
                customer=req.customer,
                product=product,
                quantity=req.quantity or 1,
                price_per_unit=random.choice([800, 1500, 3500, 5000, 12000, 25000]),
                material_source=random.choice(['customer', 'purchase', 'waste']),
                accepted_date=date(2026, 4, random.randint(1, 30)),
                planned_completion_date=date(2026, 5, random.randint(10, 31)),
                launch_date=date(2026, 4, random.randint(15, 30)) if random.random() > 0.3 else None,
                completion_date=None,
                status=random.choice(['pending', 'in_progress', 'completed', 'closed'])
            )
            orders.append(order)

        # 3 заявки разделяем на 2-3 заказа каждую
        split_requests = approved_requests[12:15] if len(approved_requests) > 12 else approved_requests[:3]
        for req in split_requests:
            for _ in range(random.randint(2, 3)):
                product = products[random.randint(0, len(products) - 1)]
                order = Order.objects.create(
                    request=req,
                    customer=req.customer,
                    product=product,
                    quantity=random.randint(1, 20),
                    price_per_unit=random.choice([800, 1500, 3500, 5000, 12000]),
                    material_source=random.choice(['purchase', 'customer']),
                    accepted_date=date(2026, 4, random.randint(1, 30)),
                    planned_completion_date=date(2026, 5, random.randint(10, 31)),
                    launch_date=date(2026, 4, random.randint(15, 30)),
                    status=random.choice(['in_progress', 'completed']),
                )
                orders.append(order)

        # 5 заказов без связи с заявками
        for i in range(5):
            client = all_clients[i % len(all_clients)]
            product = products[random.randint(0, len(products) - 1)]
            order = Order.objects.create(
                request=None,
                customer=client,
                product=product,
                quantity=random.randint(1, 30),
                price_per_unit=random.choice([800, 1500, 3500, 5000, 12000, 25000]),
                material_source=random.choice(['purchase', 'customer', 'waste']),
                accepted_date=date(2026, 4, random.randint(1, 30)),
                planned_completion_date=date(2026, 5, random.randint(10, 31)),
                launch_date=date(2026, 5, random.randint(1, 10)) if random.random() > 0.5 else None,
                status=random.choice(['pending', 'in_progress', 'completed']),
            )
            orders.append(order)

        self.stdout.write(f'  Заказы созданы ({len(orders)})')

        # ============================================================
        # 11. СКЛАДСКОЙ УЧЁТ
        # ============================================================
        for order in orders:
            # Поступление материалов
            for _ in range(random.randint(1, 2)):
                material = materials[random.randint(0, len(materials) - 1)]
                InventoryRecord.objects.create(
                    material=material,
                    movement_type='receipt',
                    quantity=random.randint(1, 30),
                    unit_price=material.unit_price,
                    date=date(2026, 4, random.randint(1, 30))
                )
            # Выдачи (1-5)
            for _ in range(random.randint(1, 5)):
                material = materials[random.randint(0, len(materials) - 1)]
                InventoryRecord.objects.create(
                    material=material,
                    order=order,
                    movement_type='issue',
                    quantity=random.randint(1, 10),
                    unit_price=material.unit_price,
                    date=date(2026, random.randint(4, 5), random.randint(1, 30))
                )
        self.stdout.write('  Складской учёт заполнен')

        # ============================================================
        # 12-13. ТАБЕЛЬ И РАБОТЫ
        # ============================================================
        # Генерируем смены для каждого месяца (апрель и май)
        for month in [4, 5]:
            num_shifts = random.randint(5, 15)
            _, max_day = monthrange(2026, month)
            shift_days = random.sample(range(1, max_day + 1), min(num_shifts, max_day))
            for day in shift_days:
                shift_date = date(2026, month, day)
                work_log = WorkLog.objects.create(
                    employee=emp,
                    shift_date=shift_date,
                    efficiency_score=round(random.uniform(-0.05, 0.05), 2),
                    comment='' if random.random() > 0.3 else 'Смена отработана'
                )
                # 3 работы в смену
                for _ in range(3):
                    order_choice = random.choice(orders) if orders and random.random() > 0.3 else None
                    wc = random.choice(work_categories)
                    start_hour = random.randint(8, 10)
                    start_time = datetime(2026, month, day, start_hour, 0)
                    end_time = start_time + timedelta(hours=random.randint(1, 4))
                    WorkEntry.objects.create(
                        work_log=work_log,
                        order=order_choice,
                        work_category=wc,
                        start_time=start_time,
                        end_time=end_time
                    )

        # ============================================================
        # 14. ОПЕРАЦИИ
        # ============================================================
        for eq in equipment_list:
            num_ops = random.randint(0, 30)
            for _ in range(num_ops):
                emp = random.choice(all_employees)
                order_choice = random.choice(orders) if orders and random.random() > 0.3 else None
                op_type = random.choice(operation_types)
                op_date = date(2026, random.randint(4, 5), random.randint(1, 30))
                start_hour = random.randint(8, 16)
                start_time = datetime(op_date.year, op_date.month, op_date.day, start_hour, 0)
                end_time = start_time + timedelta(hours=random.randint(1, 6))
                Operation.objects.create(
                    equipment=eq,
                    order=order_choice,
                    employee=emp,
                    operation_type=op_type,
                    start_time=start_time,
                    end_time=end_time,
                    meter_reading=round(random.uniform(0, 500), 2) if random.random() > 0.5 else None
                )
        self.stdout.write('  Операции заполнены')

        # ============================================================
        # 15. ДОХОДЫ И РАСХОДЫ
        # ============================================================
        for order in orders:
            total = order.total_price
            # Доходы
            if order.status in ['completed', 'closed']:
                # Оплачен полностью
                Income.objects.create(order=order, amount=total * random.uniform(0.3, 0.5), payment_type='prepayment', date=order.accepted_date + timedelta(days=random.randint(1, 5)))
                Income.objects.create(order=order, amount=total - total * 0.4, payment_type='final_payment', date=date(2026, 5, random.randint(10, 31)))
            elif order.status == 'in_progress':
                # Частичная оплата (0-50%)
                if random.random() > 0.3:
                    Income.objects.create(order=order, amount=total * random.uniform(0.1, 0.5), payment_type='prepayment', date=order.accepted_date + timedelta(days=random.randint(1, 5)))
            elif order.status == 'pending' and random.random() > 0.5:
                Income.objects.create(order=order, amount=total * random.uniform(0.1, 0.3), payment_type='prepayment', date=order.accepted_date + timedelta(days=2))

        # Расходы
        for _ in range(30):
            cat = random.choice(expense_categories)
            Expense.objects.create(
                expense_category=cat,
                amount=round(random.uniform(500, 50000), 2),
                date=date(2026, random.randint(4, 5), random.randint(1, 30)),
                description=f'Расход по статье "{cat.name}"'
            )
        self.stdout.write('  Финансы заполнены')

        # ============================================================
        # 16. ДОПОЛНИТЕЛЬНЫЕ ФАЙЛЫ
        # ============================================================
        file_data = [
            (Employee, all_employees[1], 'трудовой_договор.txt', 'Трудовой договор №00000002\nСотрудник: Антонов Сергей Петрович\nДолжность: Фрезеровщик\nДата приёма: 01.02.2020', 'hr'),
            (Employee, all_employees[3], 'трудовой_договор.txt', 'Трудовой договор №00000004\nСотрудник: Волков Дмитрий Сергеевич\nДолжность: Токарь\nДата приёма: 01.09.2019', 'hr'),
            (Equipment, equipment_list[0], 'паспорт_станка.txt', 'Паспорт станка Haas VF-2\nЗаводской номер: HF2-2020-0342\nДата выпуска: 2020 г.\nМощность: 15 кВт', 'equipment'),
            (Equipment, equipment_list[4], 'паспорт_станка.txt', 'Паспорт станка Sodick\nЗаводской номер: SDK-2019-1128\nТип: электроэрозионный\nМощность: 10 кВт', 'equipment'),
            (Income, Income.objects.first(), 'платёжное_поручение.txt', 'Платёжное поручение № 42\nСумма: 35 000 руб.\nНазначение: предоплата по заказу\nОт: 15.04.2026', 'payment'),
            (Expense, Expense.objects.first(), 'счёт_фактура.txt', 'Счёт-фактура № 87\nПоставщик: ООО "Металлоторг"\nМатериал: Сталь-45 лист\nСумма: 12 000 руб.', 'payment'),
            (Order, orders[0], 'договор_подряда.txt', 'Договор подряда № ДП-2026-001\nИсполнитель: ООО "Экструзионное оборудование"\nЗаказчик: согласно заказу\nСроки: согласно спецификации', 'contract'),
            (Order, orders[-1], 'договор_подряда.txt', 'Договор подряда № ДП-2026-015\nИсполнитель: ООО "Экструзионное оборудование"\nСроки выполнения: май 2026 г.', 'contract'),
        ]

        for model_class, obj, filename, content, category in file_data:
            ct = ContentType.objects.get_for_model(model_class)
            File.objects.create(
                content_type=ct,
                object_id=obj.id,
                file=ContentFile(content.encode('utf-8'), name=filename),
                original_name=filename,
                file_category=category,
                uploaded_by=director_user
            )

        self.stdout.write('  Дополнительные файлы прикреплены')
        self.stdout.write(self.style.SUCCESS(f'\nБаза данных успешно заполнена!'))
        self.stdout.write(f'  Пользователей: {User.objects.count()}')
        self.stdout.write(f'  Сотрудников: {Employee.objects.count()}')
        self.stdout.write(f'  Клиентов: {Customer.objects.count()}')
        self.stdout.write(f'  Заявок: {Request.objects.count()}')
        self.stdout.write(f'  Заказов: {Order.objects.count()}')
        self.stdout.write(f'  Записей табеля: {WorkLog.objects.count()}')
        self.stdout.write(f'  Работ: {WorkEntry.objects.count()}')
        self.stdout.write(f'  Операций: {Operation.objects.count()}')
        self.stdout.write(f'  Складских записей: {InventoryRecord.objects.count()}')
        self.stdout.write(f'  Доходов: {Income.objects.count()}')
        self.stdout.write(f'  Расходов: {Expense.objects.count()}')
        self.stdout.write(f'  Файлов: {File.objects.count()}')

    @staticmethod
    def _translit(text):
        mapping = {
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
            'Ы': 'Y', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ы': 'y', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        }
        return ''.join(mapping.get(c, c) for c in text)