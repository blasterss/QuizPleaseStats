import pandas as pd

class LoadingData:
    def __init__(self):
        self.data = None
    
    def load_data(self, file_path1, file_path2=None, file_path3=None, file_path4=None):
        try:
            dfs = []
            dfs.append(pd.read_excel(file_path1))
            if file_path2:
                dfs.append(pd.read_excel(file_path2))
            if file_path3:
                dfs.append(pd.read_excel(file_path3))
            if file_path4:
                dfs.append(pd.read_excel(file_path4))
            self.data = pd.concat(dfs)
            print("Data loaded successfully!")
        except Exception as e:
            print("Error loading data:", str(e))