import glob
import os

import pandas as pd

for csvfile in glob.glob(os.path.join('', '*.csv')):
    read_file = pd.read_csv(f'{csvfile[:-4]}.csv')
    read_file.to_excel(f'{csvfile[:-4]}.xlsx', index=None, header=True)
