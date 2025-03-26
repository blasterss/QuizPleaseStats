import pandas as pd

class Analyze:
    def __init__(self, data):
        self.df = data
        self.team_data = {}
    
    def prepairing(self, category):
        
        if self.df is None:
            raise ValueError("DataFrame is not initialized.")
        # Получение уникальных названий 
        self.df.dropna(subset=['Название команды'], inplace=True)
        self.df['Название команды'] = self.df['Название команды'].astype(str)
        self.df['Название команды'] = self.df['Название команды'].str.lower()
        unique_teams = self.df['Название команды'].unique()

        #if category == 1:
            #self.df['Последний раунд'] = self.df['Последний раунд'].astype(str)# + '/18'
            #self.df['Всего баллов'] = self.df['Всего баллов'].astype(str)# + '/60'
        # Итерация по уникальным командам
        for team in unique_teams:
            # Фильтрация данных для текущей команды
            team_data = self.df[self.df['Название команды'] == team].copy()
            # Удаление столбца с названием команды, чтобы он не дублировался внутри каждого подфрейма
            team_data.drop(columns=['Название команды'], inplace=True)
            # Сохранение подфрейма в словаре, используя название команды в качестве ключа
            self.team_data[team] = team_data

    def get_table_info(self, selected_team, info, current_df=None):
        if current_df is None:
            unique_games_per_package = self.df.groupby(['Дата', 'Ресторан', 'День недели', 'Название игры', 'Номер пакета']).size().groupby(info).size()
        else:
            unique_games_per_package = current_df.groupby(['Дата', 'Ресторан', 'День недели', 'Название игры', 'Номер пакета']).size().groupby(info).size()
        
        df_unique_games_per_package = pd.DataFrame(unique_games_per_package, columns=pd.MultiIndex.from_tuples([(' ', 'Всего игр')]))
        df_team_package = selected_team.groupby(info).agg({'Место': [('Сыграно игр', lambda x: x.count()),
                                                                                      ('Топ 5', lambda x: (x <= 5).sum()),
                                                                                      ('Топ 1', lambda x: (x == 1).sum())]})
        
        self.current_table = pd.merge(df_unique_games_per_package, df_team_package, on=info, how='outer').fillna(0).astype(int)
        self.current_table = self.current_table.sort_values(by=[(' ', 'Всего игр')], ascending=False)

        return self.current_table

    
    def get_table_days(self, selected_team):
        self.current_table = self.team_data[selected_team].groupby('День недели').agg({'Место': [('Сыграно игр', lambda x: x.count()),
                                                        ('Топ 5', lambda x: (x <= 5).sum()),
                                                        ('Топ 1', lambda x: (x == 1).sum())]})
        return self.current_table
    
    def get_package_restaurants(self, selected_team):
        self.current_table = self.team_data[selected_team].groupby('Ресторан').agg({'Место': [('Сыграно игр', lambda x: x.count()),
                                                        ('Топ 5', lambda x: (x <= 5).sum()),
                                                        ('Топ 1', lambda x: (x == 1).sum())]})
        return self.current_table
    
    def compare_teams(self, selected_team, current_df=None):
        if current_df is None:
            current_team_games = self.df[self.df['Название команды']==selected_team][['Название игры', 'Номер пакета']]
            together_games = pd.merge(current_team_games, self.df, on=['Название игры','Номер пакета'], how='left')
        else:
            current_team_games = current_df[current_df['Название команды']==selected_team][['Название игры', 'Номер пакета']]
            together_games = pd.merge(current_team_games,  current_df, on=['Название игры','Номер пакета'], how='left')

        selected_team_ranks = together_games[together_games['Название команды'] == selected_team].groupby('Название игры')['Место'].min()
        together_games[f'Сколько раз заняла место выше, чем {selected_team}'] = together_games.apply(lambda row: row['Место'] < selected_team_ranks[row['Название игры']], axis=1).astype(int)
        connect_games = together_games['Название команды'].value_counts().reset_index()
        connect_games.columns = ['Название команды', f'Вместе сыгранных игр из {current_team_games.shape[0]}']
        hghr = together_games.groupby('Название команды').agg({f'Сколько раз заняла место выше, чем {selected_team}': 'sum'})
        connect_games = connect_games.merge(hghr, left_on='Название команды', right_index=True)
        self.current_table = connect_games.iloc[1:]
        #self.current_table = connect_games.rename({f'Сколько раз заняла место выше, чем {selected_team}': 'Сколько раз выше Funny cucumber'}, axis=1)
        return self.current_table