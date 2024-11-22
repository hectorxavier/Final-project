import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

clients = pd.read_csv('files/telecom_clients_us.csv')
clients.info()

data = pd.read_csv('files/telecom_dataset_us.csv')
data.info()
display(data.head())
display(clients.head())

display(data[data['operator_id'].isnull()])
# Se procederá a eliminar los registros con valores nulos en la columna 'operator_id', pues al tratarse de la columna de interes no tiene razones para mantener información que no tenga datos en ese campo.
data.dropna(inplace = True)

#Definir el número de usuarios que no tiene llamadas perdidas. El objetivo es limitar la muestra a los usuarios a los que tiene llamadas perdidas para no sesgar la media de estos valores, para el tiempo de espera se integrará la información.

user_missed_call = data[data['is_missed_call'] == True]['operator_id'].drop_duplicates()
print(user_missed_call.nunique())
user = data['operator_id'].drop_duplicates()
print(user.nunique())
print(user.nunique() - user_missed_call.nunique())

# Agrupación de llamadas perdidas por usuarios. 
data_group = data[data['operator_id'].isin(user_missed_call)].groupby(['operator_id', 'is_missed_call']).count().reset_index()
print(data_group.head())
data_missed_call = data_group[data_group['is_missed_call'] == True]['user_id'].reset_index(drop=True).to_frame()
print(data_missed_call.head())
# Diagrama de caja y bigotes
plt.boxplot(data_missed_call['user_id'])
plt.close()
data_missed_call['user_id'].hist()
plt.close()

print(data_missed_call['user_id'].mean())
### Revisar si se debe aplicar una prueba estadistica para definir como ineficientes a los operadores que estan en los extremos
# La metrica fundamental para el análisis se relaciona con las llamdas perdidas dde los operadores, por lo que se 
#data['is_missed_call'].hist()





