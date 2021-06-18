import pandas as pd
import pandas_profiling

data = pd.read_csv('C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal X 8D 512G\\pandas.csv')
data.profile_report(title='long PD data analysis')
profile = data.profile_report(title='LPD')
profile.to_file(output_file='LPD.html')