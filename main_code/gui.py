import datetime
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QShortcut, QVBoxLayout, QComboBox, QDesktopWidget, QMessageBox, QTableView, QAbstractItemView, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QMimeData
from load_data import LoadingData
from analytics import Analyze
from main_parser import GameDataScraper
import pandas as pd

class CustomSortFilterProxyModel(QSortFilterProxyModel):
    def lessThan(self, left_index, right_index):
        source_model = self.sourceModel()
        column_date = "Дата" 
        column_point = "Всего баллов"
        column_place = "Место"
        column_round = "Последний раунд"
        column_all_games = "Всего игр"
        column_played_games = "Сыграно игр"
        column_top5 = "Топ 5"
        column_top1 = "Топ 1"

        # Получить индекс столбца по имени
        column_index = source_model.columnCount()
        for col in range(source_model.columnCount()):
            if source_model.headerData(col, Qt.Horizontal) == column_date:
                column_index = col
            elif source_model.headerData(col, Qt.Horizontal) == column_date:
                column_index = col

        if left_index.column() == column_index and right_index.column() == column_index:
            left_date_str = left_index.data()
            right_date_str = right_index.data()

            # Check if date strings are not None
            if left_date_str is None or right_date_str is None:
                return False

            # Split date strings into day, month, and year components
            left_day, left_month, left_year = map(int, left_date_str.split('.'))
            right_day, right_month, right_year = map(int, right_date_str.split('.'))

            # Compare the year, month, and day components
            if left_year != right_year:
                return left_year < right_year
            elif left_month != right_month:
                return left_month < right_month
            else:
                return left_day < right_day
        
        if left_index.isValid() and right_index.isValid():
            left_data = left_index.data()
            right_data = right_index.data()

            # Check if data is not None
            if left_data is not None and right_data is not None:
                # Attempt to convert data to float for comparison
                try:
                    left_float = float(left_data)
                    right_float = float(right_data)
                    return left_float < right_float
                except ValueError:
                    # If conversion fails, compare as strings
                    return left_data < right_data

            # If either data is None, handle gracefully
            return left_data is None and right_data is not None

        return super().lessThan(left_index, right_index)

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Квиз, плиз! Статистика")
        self.setFixedSize(1400, 800)  # Устанавливаем фиксированный размер окна
        self.center()  # Центрируем окно по центру экрана
        self.init_ui()

    def center(self):
        frame_geometry = self.frameGeometry()
        desktop_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(desktop_center)
        self.move(frame_geometry.topLeft())

    def init_ui(self):
        self.update_label = QLabel("Хотите обновить данные?")
        self.update_button_yes = QPushButton("Да")
        self.update_button_yes.setFixedSize(480, 100)
        self.update_button_no = QPushButton("Нет")
        self.update_button_no.setFixedSize(480, 100)
        self.update_label.setFont(QFont("Arial", 22))
        self.update_label.setStyleSheet("font-weight: bold")

        self.update_button_yes.clicked.connect(self.update_data)
        self.update_button_no.clicked.connect(self.choose_data)

        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.update_label)
        self.layout1.addWidget(self.update_button_yes)
        self.layout1.addWidget(self.update_button_no)
        self.layout1.setAlignment(Qt.AlignCenter)

        self.setLayout(self.layout1)

    def update_data(self):
        self.update_button_yes.setEnabled(False)
        self.update_button_no.setEnabled(False)
        self.update_label.setText("Обновление данных...")
        parser = GameDataScraper('kim', 'main_data/data_kim.xlsx','main_data/data_kim.xlsx')
        parser.scrape_data(parser.kim_url, 'kim')

        parser = GameDataScraper('thematic_kim', 'main_data/data_thematic_kim.xlsx','main_data/data_thematic_kim.xlsx')
        parser.scrape_data(parser.kim_thematic_url, 'thematic_kim')

        parser = GameDataScraper('classic', 'main_data/data_classic.xlsx','main_data/data_classic.xlsx')
        parser.scrape_data(parser.classic_url, 'classic')

        parser = GameDataScraper('thematic_classic', 'main_data/data_thematic_classic.xlsx','main_data/data_thematic_classic.xlsx')
        parser.scrape_data(parser.classic_thematic_url, 'thematic_classic')

        self.choose_data()

    def choose_data(self):
        self.clear_layout()
        self.layout1.setAlignment(Qt.AlignAbsolute)

        self.team_name_label = QLabel("Выберите данные по играм")
        self.team_name_label.setFont(QFont("Arial", 14))
        self.team_name_label.setStyleSheet("font-weight: bold")
        self.team_name_label.setAlignment(Qt.AlignCenter)

        self.classic_data = QLabel('<a href="classic">Посмотреть данные по классическим играм</a>')
        self.classic_data.setAlignment(Qt.AlignCenter)
        self.classic_data.setFont(QFont("Arial", 12))
        self.classic_data.linkActivated.connect(lambda: self.another_function(1))

        self.kim_data = QLabel('<a href="kim">Посмотреть данные по КиМ</a>')
        self.kim_data.setAlignment(Qt.AlignCenter)
        self.kim_data.setFont(QFont("Arial", 12))
        self.kim_data.linkActivated.connect(lambda: self.another_function(2))

        self.thematic_kim_data = QLabel('<a href="thematic_kim">Посмотреть данные по тематическому КиМ</a>')
        self.thematic_kim_data.setAlignment(Qt.AlignCenter)
        self.thematic_kim_data.setFont(QFont("Arial", 12))
        self.thematic_kim_data.linkActivated.connect(lambda: self.another_function(3))

        self.thematic_classic_data = QLabel('<a href="thematic_classic">Посмотреть данные по тематическим классическим играм</a>')
        self.thematic_classic_data.setAlignment(Qt.AlignCenter)
        self.thematic_classic_data.setFont(QFont("Arial", 12))
        self.thematic_classic_data.linkActivated.connect(lambda: self.another_function(4))

        self.all_classic_data = QLabel('<a href="all_classic">Посмотреть данные по всем классическим играм</a>')
        self.all_classic_data.setAlignment(Qt.AlignCenter)
        self.all_classic_data.setFont(QFont("Arial", 12))
        self.all_classic_data.linkActivated.connect(lambda: self.another_function(5))

        self.all_kim_data = QLabel('<a href="all_kim">Посмотреть данные по всему КиМ</a>')
        self.all_kim_data.setAlignment(Qt.AlignCenter)
        self.all_kim_data.setFont(QFont("Arial", 12))
        self.all_kim_data.linkActivated.connect(lambda: self.another_function(6))

        self.all_data = QLabel('<a href="all">Посмотреть данные по всем играм</a>')
        self.all_data.setAlignment(Qt.AlignCenter)
        self.all_data.setFont(QFont("Arial", 12))
        self.all_data.linkActivated.connect(lambda: self.another_function(7))

        self.layout1.addWidget(self.team_name_label)
        self.layout1.addWidget(self.classic_data)
        self.layout1.addWidget(self.kim_data)
        self.layout1.addWidget(self.thematic_classic_data)
        self.layout1.addWidget(self.thematic_kim_data)
        self.layout1.addWidget(self.all_classic_data)
        self.layout1.addWidget(self.all_kim_data)
        self.layout1.addWidget(self.all_data)

    def copy_data_to_clipboard(self):
        selection_model = self.table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if selected_indexes:
            data = ""
            rows = set(index.row() for index in selected_indexes)
            columns = set(index.column() for index in selected_indexes)

            for row in sorted(rows):
                for column in sorted(columns):
                    index = self.proxy_model.mapToSource(self.proxy_model.index(row, column))
                    data += str(index.data(Qt.DisplayRole))
                    if column < max(columns):
                        data += "\t"  # Separate columns with tabs
                data += "\n"  # Separate rows with newlines

            mime_data = QMimeData()
            mime_data.setData("text/plain", data.encode('utf-8'))

            clipboard = QApplication.clipboard()
            clipboard.setMimeData(mime_data)

    def another_function(self, category):
        self.clear_layout()

        loading = LoadingData()
        if category == 1:
            loading.load_data('main_data/data_classic.xlsx')
            self.team_name_label = QLabel("Данные по классическим играм")
        elif category == 2:
            loading.load_data('main_data/data_kim.xlsx')
            self.team_name_label = QLabel("Данные по КиМ")
        elif category == 3:
            loading.load_data('main_data/data_thematic_kim.xlsx')
            self.team_name_label = QLabel("Данные по тематическому КиМ")
        elif category == 4:
            loading.load_data('main_data/data_thematic_classic.xlsx')
            self.team_name_label = QLabel("Данные по тематической классике")
        elif category == 5:
            loading.load_data('main_data/data_classic.xlsx', 'main_data/data_thematic_classic.xlsx')
            self.team_name_label = QLabel("Данные по классическим и тематическим играм")
        elif category == 6:
            loading.load_data('main_data/data_kim.xlsx', 'main_data/data_thematic_kim.xlsx')
            self.team_name_label = QLabel("Данные по КиМ и тематическому КиМ")
        elif category == 7:
            loading.load_data('main_data/data_classic.xlsx', 'main_data/data_thematic_classic.xlsx', 
                              'main_data/data_kim.xlsx', 'main_data/data_thematic_kim.xlsx')
            self.team_name_label = QLabel("Данные по всем играм")

        self.team_name_label.setFont(QFont("Arial", 12))
        self.team_name_label.setStyleSheet("font-weight: bold")
        self.team_name_label.setAlignment(Qt.AlignCenter)

        self.analize_block = Analyze(loading.data)
        self.analize_block.prepairing(category)

        self.chose_team = QComboBox()
        self.chose_team.addItems(self.analize_block.team_data.keys())
        self.chose_team.setEditable(True)

        year_seasons_dict = {'2024': ['Лето', 'Весна'],
                            '2023': ['Зима', 'Осень', 'Лето', 'Весна'],
                            '2022': ['Зима', 'Осень', 'Лето', 'Весна'],
                            '2021': ['Зима', 'Осень', 'Лето', 'Весна'],
                            '2020': ['Зима', 'Осень', 'Весна'],
                            '2019': ['Зима', 'Осень']}

        self.chose_season = QComboBox()
        self.chose_season.addItem('Всё время')
        if (category == 1) or (category == 4) or (category == 5):
            self.game_type = 1
            for year, seasons in  year_seasons_dict.items():
                for season in seasons:
                    item_text = f"{season}: {year}"
                    self.chose_season.addItem(item_text)
        elif (category == 2) or (category == 3) or (category == 6):
            self.game_type = 2
            self.chose_season.addItems(['Весна: 2024', 'Осень: 2023', 'Весна: 2023', 'Осень: 2022', 'Весна: 2022', 'Осень: 2021', 'Весна: 2020'])

        self.chose_team.currentIndexChanged.connect(lambda: self.update_table_view(1))
        self.chose_season.currentIndexChanged.connect(lambda: self.update_table_view(1))

        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.proxy_model = CustomSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.setSortingEnabled(True)  
        
        self.copy_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self.table_view)
        self.copy_shortcut.activated.connect(self.copy_data_to_clipboard)
  
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table_view)

        self.stat_label = QLabel("Статистика по:")

        self.button1 = QPushButton("Номер пакета")
        self.button1.clicked.connect(lambda: self.update_table_view(self.button1.text()))

        self.button2 = QPushButton("День недели")
        self.button2.clicked.connect(lambda: self.update_table_view(self.button2.text()))
            
        self.button3 = QPushButton("Ресторан")
        self.button3.clicked.connect(lambda: self.update_table_view(self.button3.text()))

        self.button4 = QPushButton("Сравнить с другими командами")
        self.button4.clicked.connect(lambda: self.update_table_view(2))


        self.mean_points_label = QLabel("Средний балл: ")
        self.mean_place_label = QLabel("Среднее место: ")

            # Создание макета для кнопок
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.stat_label)
        buttons_layout.addWidget(self.button1)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button3)
        buttons_layout.addWidget(self.button4)  
        buttons_layout.addWidget(self.mean_points_label)
        buttons_layout.addWidget(self.mean_place_label)
        buttons_layout.setAlignment(Qt.AlignCenter)
        

        buttons_container = QWidget()
        buttons_container.setLayout(buttons_layout)

            # Создание QLabel и QComboBox
        self.label_test = QLabel("Введите название команды (выберите)")
        self.label_season = QLabel("Выберите сезон")
        self.spacing = QLabel(" "*100)

            # Создание макета для QLabel и QComboBox с выравниванием сверху
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.label_season, Qt.AlignLeft)
        top_layout.addWidget(self.chose_season, Qt.AlignLeft)
        top_layout.addWidget(self.spacing)
        top_layout.addWidget(self.label_test, Qt.AlignRight)
        top_layout.addWidget(self.chose_team, Qt.AlignRight)
        #top_layout.setAlignment(Qt.AlignRight)

            # Создание главного макета и добавление в него остальных макетов
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(table_layout)

            # Размещение кнопок справа
        main_container = QWidget()
        main_container.setLayout(main_layout)

            # Создание главного макета окна
        main_window_layout = QHBoxLayout()
        main_window_layout.addWidget(main_container)
        main_window_layout.addWidget(buttons_container)

        self.back_button = QPushButton("Вернуться к выбору данных")
        self.back_button.clicked.connect(lambda: self.choose_data())

            # Установка главного макета для окна
        central_widget = QWidget()
        central_widget.setLayout(main_window_layout)
        self.layout1.addWidget(self.team_name_label)
        self.layout1.addWidget(central_widget)
        self.layout1.addWidget(self.back_button)


    def update_table_view(self, info):
        selected_team = self.chose_team.currentText()

        if selected_team in self.analize_block.team_data.keys():
            team_data = self.analize_block.team_data[selected_team].reset_index(drop=True)
            self.model.clear()
            current_df = None
            current_season = self.chose_season.currentText()
            if current_season != 'Всё время':
                team_data['Дата'] = pd.to_datetime(team_data['Дата'], format='%d.%m.%Y')
                current_df = self.analize_block.df
                current_df['Дата'] = pd.to_datetime(current_df['Дата'], format='%d.%m.%Y')
                kim_dates = ['22.09.2022', '16.03.2023', '21.09.2023', '21.03.2024']
                kim_dates = ['21.03.2024', '21.09.2023', '16.03.2023', '22.09.2022', '11.03.2022', '15.09.2021', '13.02.2020']
                classic_dates = ['30.05.2024', '29.02.2024', '30.11.2023', '07.09.2023', 
                                 '01.06.2023', '02.03.2023', '01.12.2022', '01.09.2022',
                                 '02.06.2022', '03.03.2022', '01.12.2021', '31.08.2021', 
                                 '02.06.2021', '03.03.2021', '02.12.2020', '06.09.2020', 
                                 '05.03.2020', '03.12.2019', '30.08.2019']
                classic_dates.insert(0, datetime.datetime.now().date().strftime('%d.%m.%Y'))
                kim_dates.insert(0, datetime.datetime.now().date().strftime('%d.%m.%Y'))

                current_index_season = self.chose_season.currentIndex()
                if self.game_type == 1:
                    start_date = pd.to_datetime(classic_dates[current_index_season], format='%d.%m.%Y')
                    end_date = pd.to_datetime(classic_dates[current_index_season-1], format='%d.%m.%Y')
                elif self.game_type == 2:
                    start_date = pd.to_datetime(kim_dates[current_index_season], format='%d.%m.%Y')
                    end_date = pd.to_datetime(kim_dates[current_index_season-1], format='%d.%m.%Y')
                team_data = team_data[(team_data['Дата'] >= start_date) & (team_data['Дата'] < end_date)]
                team_data['Дата'] = team_data['Дата'].dt.strftime('%d.%m.%Y')
                current_df = current_df[(current_df['Дата'] >= start_date) & 
                                            (current_df['Дата'] < end_date)]
                current_df['Дата'] = current_df['Дата'].dt.strftime('%d.%m.%Y')
                team_data.reset_index(drop=True)

            self.mean_points_label.setText(f"Средний балл: {round(team_data['Всего баллов'].mean(),2)}")
            self.mean_place_label.setText(f"Среднее место: {round(team_data['Место'].mean(),2)}")

            self.model.setRowCount(team_data.shape[0])
            self.model.setColumnCount(team_data.shape[1])

            if info != 1 and info != 2:
                team_data = self.analize_block.get_table_info(team_data, info, current_df)
                self.model.setRowCount(team_data.shape[0])
                self.model.setColumnCount(team_data.shape[1]+1)
            elif info == 2:
                team_data = self.analize_block.compare_teams(selected_team, current_df).reset_index(drop=True)
                self.model.setRowCount(team_data.shape[0])
                self.model.setColumnCount(team_data.shape[1])
            
            column_names = team_data.columns.tolist()

            # Проверка, является ли индекс мультииндексом
            if isinstance(team_data.columns, pd.MultiIndex):
                # Использование мультииндекса в качестве названий столбцов
                header_labels = [str(col) for col in team_data.columns.get_level_values(1)]
            else:
                header_labels = column_names

            if isinstance(team_data.index, pd.MultiIndex):
                # Получение последнего уровня мультииндекса
                index_values = [str(index[-1]) for index in team_data.index]
            else:
                index_values = team_data.index.astype(str)

            index_names = team_data.index.names
            if index_names:
                index_names_str = ' '.join(str(name) for name in index_names if name is not None)
            else:
                index_names_str = "Unnamed"

            if info != 1 and info != 2:
                self.model.setHeaderData(0, Qt.Horizontal, index_names_str)
                # Установка значений индексов в первом столбце
                for row_idx, index_value in enumerate(index_values):
                    self.model.setItem(row_idx, 0, QStandardItem(index_value))

                for col_idx, name in enumerate(header_labels):
                    self.model.setHeaderData(col_idx+1, Qt.Horizontal, name)

                for row_idx, row in enumerate(team_data.iterrows()):
                    for col_idx, item in enumerate(row[1]):
                        self.model.setItem(row_idx, col_idx+1, QStandardItem(str(item)))
            elif info == 1:
                for col_idx, name in enumerate(header_labels):
                    self.model.setHeaderData(col_idx, Qt.Horizontal, name)

                for row_idx, row in enumerate(reversed(team_data.values.tolist())):
                    for col_idx, item in enumerate(row):
                        self.model.setItem(row_idx, col_idx, QStandardItem(str(item)))
            else:
                for col_idx, name in enumerate(header_labels):
                    self.model.setHeaderData(col_idx, Qt.Horizontal, name)

                for row_idx, row in team_data.iterrows():
                    for col_idx, item in enumerate(row):
                        self.model.setItem(row_idx, col_idx, QStandardItem(str(item)))
            self.table_view.resizeColumnsToContents()
        else:
            QMessageBox.information(self, "Ошибка", "Нет команды с таким названием! ЧЕ, ДУМАЛИ Я НЕ ПРЕДУСМОТРЕЛ? ))))")

    def update_table_view_compare(self, info):
        selected_team = self.chose_team.currentText()
        compare_team = self.compare_box.currentText()

        if selected_team and compare_team:
            team_data = self.analize_block.team_data[selected_team].reset_index(drop=True)
            self.model.clear()
            current_df = None
            current_season = self.chose_season.currentText()
            if current_season != 'Всё время':
                team_data['Дата'] = pd.to_datetime(team_data['Дата'], format='%d.%m.%Y')
                current_df = self.analize_block.df
                current_df['Дата'] = pd.to_datetime(current_df['Дата'], format='%d.%m.%Y')
                kim_dates = ['22.09.2022', '16.03.2023', '21.09.2023', '21.03.2024']
                kim_dates = ['21.03.2024', '21.09.2023', '16.03.2023', '22.09.2022', '11.03.2022', '15.09.2021', '13.02.2020']
                classic_dates = ['30.05.2024', '29.02.2024', '30.11.2023', '07.09.2023', 
                                 '01.06.2023', '02.03.2023', '01.12.2022', '01.09.2022',
                                 '02.06.2022', '03.03.2022', '01.12.2021', '31.08.2021', 
                                 '02.06.2021', '03.03.2021', '02.12.2020', '06.09.2020', 
                                 '05.03.2020', '03.12.2019', '30.08.2019']
                classic_dates.insert(0, datetime.datetime.now().date().strftime('%d.%m.%Y'))
                kim_dates.insert(0, datetime.datetime.now().date().strftime('%d.%m.%Y'))

                current_index_season = self.chose_season.currentIndex()
                if self.game_type == 1:
                    start_date = pd.to_datetime(classic_dates[current_index_season], format='%d.%m.%Y')
                    end_date = pd.to_datetime(classic_dates[current_index_season-1], format='%d.%m.%Y')
                elif self.game_type == 2:
                    start_date = pd.to_datetime(kim_dates[current_index_season], format='%d.%m.%Y')
                    end_date = pd.to_datetime(kim_dates[current_index_season-1], format='%d.%m.%Y')
                team_data = team_data[(team_data['Дата'] >= start_date) & (team_data['Дата'] < end_date)]
                team_data['Дата'] = team_data['Дата'].dt.strftime('%d.%m.%Y')
                current_df = current_df[(current_df['Дата'] >= start_date) & 
                                            (current_df['Дата'] < end_date)]
                current_df['Дата'] = current_df['Дата'].dt.strftime('%d.%m.%Y')
                team_data.reset_index(drop=True)

            self.model.setRowCount(team_data.shape[0])
            self.model.setColumnCount(team_data.shape[1])
            
            if info != 1:
                team_data = self.analize_block.get_table_info(selected_team, info)
                self.model.setRowCount(team_data.shape[0])
                self.model.setColumnCount(team_data.shape[1]+1)
            
            column_names = self.analize_block.team_data[selected_team].columns.tolist()

            # Проверка, является ли индекс мультииндексом
            if isinstance(team_data.columns, pd.MultiIndex):
                # Использование мультииндекса в качестве названий столбцов
                header_labels = [str(col) for col in team_data.columns.get_level_values(1)]
            else:
                header_labels = column_names

            if isinstance(team_data.index, pd.MultiIndex):
                # Получение последнего уровня мультииндекса
                index_values = [str(index[-1]) for index in team_data.index]
            else:
                index_values = team_data.index.astype(str)

            index_names = team_data.index.names
            if index_names:
                index_names_str = ' '.join(str(name) for name in index_names if name is not None)
            else:
                index_names_str = "Unnamed"

            if info != 1:
                self.model.setHeaderData(0, Qt.Horizontal, index_names_str)
                # Установка значений индексов в первом столбце
                for row_idx, index_value in enumerate(index_values):
                    self.model.setItem(row_idx, 0, QStandardItem(index_value))

                for col_idx, name in enumerate(header_labels):
                    self.model.setHeaderData(col_idx+1, Qt.Horizontal, name)

                for row_idx, row in enumerate(team_data.iterrows()):
                    for col_idx, item in enumerate(row[1]):
                        self.model.setItem(row_idx, col_idx+1, QStandardItem(str(item)))
            else:
                for col_idx, name in enumerate(header_labels):
                    self.model.setHeaderData(col_idx, Qt.Horizontal, name)

                for row_idx, row in team_data.iterrows():
                    for col_idx, item in enumerate(row):
                        self.model.setItem(row_idx, col_idx, QStandardItem(str(item)))

    def filter_items(self, text):
        text = text.lower()
        for index in range(self.chose_team.count()):
            item_text = self.chose_team.itemText(index).lower()
            if text in item_text:
                self.chose_team.model().item(index).setEnabled(True)
            else:
                self.chose_team.model().item(index).setEnabled(False)

    def clear_layout(self):
        for i in reversed(range(self.layout1.count())):
            widget = self.layout1.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('assets/logo.ico'))
    window = GUI()
    window.setWindowIcon(QIcon('assets/logo.ico'))
    window.show()
    sys.exit(app.exec_())