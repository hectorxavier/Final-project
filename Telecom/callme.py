import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from scipy import stats as st

clients = pd.read_csv('Telecom/files/telecom_clients_us.csv')
clients.info()

data = pd.read_csv('Telecom/files/telecom_dataset_us.csv')
data.info()
display(data.head())
display(clients.head())

display(data[data['operator_id'].isnull()])
# Se procederá a eliminar los registros con valores nulos en la columna 'operator_id', pues al tratarse de la columna de interes no tiene razones para mantener información que no tenga datos en ese campo.
data.dropna(inplace = True)
# Se procederá a eliminar los registros con valores duplicados
print(data[data.duplicated()])
data.drop_duplicates(inplace=True)
print(data[data.duplicated()])
#Definir el número de usuarios que no tiene llamadas perdidas. El objetivo es limitar la muestra a los usuarios a los que tiene llamadas perdidas para no sesgar la media de estos valores, para el tiempo de espera se integrará la información.

user_missed_call = data[data['is_missed_call'] == True]['operator_id'].drop_duplicates()
print(user_missed_call.nunique())
user = data['operator_id'].drop_duplicates()
print(user.nunique())
print(user.nunique() - user_missed_call.nunique())

# Agrupación de llamadas perdidas por usuarios. 
data_group = data[data['operator_id'].isin(user_missed_call)].groupby(['operator_id', 'is_missed_call']).sum().reset_index()
print(data_group.head())
data_missed_call = data_group[data_group['is_missed_call'] == True][['user_id', 'calls_count']].reset_index(drop=True)
print(data_missed_call.head())
# Diagrama de caja y bigotes
plt.boxplot(data_missed_call['calls_count'])
plt.close()
data_missed_call['calls_count'].hist()
plt.close()

print(data_missed_call['calls_count'].mean())
### Revisar si se debe aplicar una prueba estadistica para definir como ineficientes a los operadores que estan en los extremos
# La metrica fundamental para el análisis se relaciona con las llamadas perdidas de los operadores, por lo que se 
# Percentiles, para definir el límite para los datos desde donde se considera ineficiente a un operador se tomará el percentil 95, todo valor que se ubique sobre este se considerará ineficiente.
print('El límite para llamadas perdidas será: '+ str(np.percentile(data_missed_call['calls_count'],95)))

### Tiempo de espera.
data['standby'] = data['total_call_duration'] - data['call_duration']
display(data.head())
print(data['standby'].mean())
print(data['standby'].max())
plt.boxplot(data['standby'])
plt.close()
data['standby'].hist()
plt.close()

print(np.percentile(data['standby'],90))
data_filtered = data[data['standby'] < np.percentile(data['standby'],90)]
data_filtered['standby'].hist()
plt.close()
plt.boxplot(data_filtered['standby'])
## Con el dataframe de información filtrada se mantiene varios valores que se pueden considerar extremos, se realizará un nuevo filtro.
## Si se excluye el 40% de las observaciones se nota que los valores están mejor distribuidos, si embargo, excluir esa cantidad de datos es muy alta. Aun así, se puede aplicarlo para establecer el limite en un valor más cercano a la media.
data_filtered_new = data[data['standby'] < np.percentile(data['standby'],60)]
data_filtered_new['standby'].hist()
plt.close()
plt.boxplot(data_filtered_new['standby'])

print('El valor medio del tiempo de espera es: ' + str(data_filtered_new['standby'].mean()))
print('El valor limite del tiempo de espera es: ' + str(data_filtered_new['standby'].max()))
## Filtro para listar los operadores ineficientes.
### Por llamadas perdidas.
operator = data_group[data_group['calls_count']>= np.percentile(data_missed_call['calls_count'],95)]['operator_id'].reset_index(drop = True)
print(operator)
### Por tiempo de espera
call_waiting = data[data['standby'] >= data_filtered_new['standby'].max()]['operator_id'].drop_duplicates().reset_index(drop = True)
print(call_waiting)
# Prueba de hipótesis sobre el tiempo de espera.
# H0 = Las medias de las datos originales es igual a la media del dataset de referencia.
results =  st.ttest_1samp(data['standby'], data_filtered_new['standby'].mean())
print('Valor p:', results.pvalue)
### El valor p resulta ser tan bajo que no hay manera de no rechazar la hipótesis nula.

### Según los resultados se puede conluir que existe un 40% de operadores que no es eficaz dentro de la empresa. Se validará el número llamadas que recibe cada uno, para confirmar que la pca eficacia se debe a los operadores a una mala distribución de las llamadas.
data_inef_operator = data[data['operator_id'].isin(operator)][['operator_id', 'calls_count']].groupby('operator_id').sum()
print(data_inef_operator.min())
print(data_inef_operator.max())
data_efic_operator = data[~(data['operator_id'].isin(operator))][['operator_id', 'calls_count']].groupby('operator_id').sum()
print(data_efic_operator.max())

