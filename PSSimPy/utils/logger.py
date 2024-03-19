import os
import csv
from typing import List, Tuple

class Logger:

    def __init__(self, file_path: str, headers: tuple):
        # append ".csv" if not included in file name
        if not file_path.endswith('.csv'):
            file_path = file_path + '.csv'
        self.file_path = file_path
        self.headers = headers

    def write(self, data: List[Tuple]):
        if not os.path.exists(self.file_path):
            data.insert(0, self.headers)
            mode = 'w'
        else:
            mode = 'a'
        with open(self.file_path, mode, newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)