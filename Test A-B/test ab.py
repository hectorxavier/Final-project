import pandas as pd
import numpy as np
from scipy import stats
from scipy import stats as st
import matplotlib.pyplot as plt
import math as mth

mkt_events = pd.read_csv('Test A-B/files/ab_project_marketing_events_us.csv')
new_users = pd.read_csv('Test A-B/files/final_ab_new_users_upd_us.csv')
events = pd.read_csv('Test A-B/files/final_ab_events_upd_us.csv')
participants = pd.read_csv('Test A-B/files/final_ab_participants_upd_us.csv')

mkt_events.info()
display(mkt_events)
new_users.info()
display(new_users)
events.info()
display(events)
participants.info()
display(participants)

## Es necesario transformar los campos que contienen fecha a tipo Datetime
mkt_events['start_dt'] = pd.to_datetime(mkt_events['start_dt'])
mkt_events['finish_dt'] = pd.to_datetime(mkt_events['finish_dt'])
new_users['first_date'] = pd.to_datetime(new_users['first_date'])
events['event_dt'] = pd.to_datetime(events['event_dt'])

## Existen campos que pueden transformarse en categorias
print(new_users['device'].unique())
new_users['device'] = new_users['device'].astype('category')

## Valores duplicados. Se verifica si existe duplicados en los dataset con el metodo duplicated.
print(new_users[new_users['user_id'].duplicated()]) #No debían existir usuarios duplicados si el dataset corresponde a nuevos registros.
print(events[events.duplicated()])
print(participants[participants.duplicated()])

print(participants['ab_test'].unique())
print(events['event_name'].unique())

## Embudo. login --> product_page --> product_cart --> purchase
data = events.pivot_table(
    index='user_id',
    columns='event_name',
    values='event_dt',
    aggfunc='min'
)

print(data)
## Secuencia para desarrollar el embudo.
step_1 = ~data['product_page'].isna()
step_2 = step_1 & (data['product_cart'] > data['product_page'])
step_3 = step_2 & (data['purchase'] > data['product_cart'])

n_product_page = data[step_1].shape[0]
n_product_cart = data[step_2].shape[0]
n_purchase = data[step_3].shape[0]

print('Ve un producto:', n_product_page)
print('Agrega un producto:', n_product_cart)
print('Realiza la compra:', n_purchase)

# Número de usuarios
participants_group = participants.groupby('group')['user_id'].count().reset_index()
print(participants_group) ## La muestra puedes estar mejor distribuida, pero la diferencia no se considera significativa
print(new_users['first_date'].min())
print(new_users['first_date'].max()) # Indican que los nuevos usuarios se registraron hasta el 2020-12-21, sin embargo existe registro luego de esa fecha.

# Usuarios en ambas muestras.

group_a = participants[participants['group'] == 'A']['user_id']
print(group_a.head())
print(participants[participants['user_id'].isin(group_a) & (participants['group'] == 'B')]['user_id'].nunique()) # existen usuarios en ambas muestras.

print(participants['user_id'].nunique())

# Eventos por días
print(events['event_dt'].min()) #Prueba de la fecha mínima de los registros
print(events['event_dt'].max()) #Prueba de la fecha máxima de los registros
events['day'] = events['event_dt'].dt.weekday
events['date'] = events['event_dt'].dt.date
print(events.head())

event_day_group = events.groupby('date').count().reset_index()
print(event_day_group.head)
event_day_group.plot.line(x = 'date', y = 'user_id')
plt.close()

print(participants[(participants['group'] == 'A') & (participants['ab_test'] == 'recommender_system_test')])
print(participants[(participants['group'] == 'B') & (participants['ab_test'] == 'recommender_system_test')])
## Se revisa los nombre de la pruebas, genera dudas que en el grupo A, considerado como de control tambien cuente con el test de 'recommender_system_test', igual sucede con el grupo B, por lo que se consdera conveniente filtrar la información de los dos grupos aunque esto signifique tener menos datos para la prueba.

### EVALUACION TEST AB
group_a_filtered = participants[(participants['group'] == 'A') & (participants['ab_test'] == 'interface_eu_test')]
group_b_filtered = participants[(participants['group'] == 'B') & (participants['ab_test'] == 'recommender_system_test')]
duplicated_users = group_a_filtered[group_a_filtered['user_id'].isin(group_b_filtered['user_id'])]
display(duplicated_users['user_id'].nunique())
print(duplicated_users[duplicated_users['user_id'].isin(new_users['user_id'])]) #Los usuarios que se encuentran en ambos grupos son nuevos usuarios, por lo que se eliminarán los usuarios que se encuentran en el grupo A y se mantendrán los del grupo B

group_a_filtered = group_a_filtered[~group_a_filtered['user_id'].isin(group_b_filtered['user_id'])]
# Tabla pivot para elaborar el enbudo.
group_a_pivot = events[events['user_id'].isin(group_a_filtered['user_id'])].pivot_table(
    index='user_id',
    columns='event_name',
    values='event_dt',
    aggfunc='min'
)

group_b_pivot = events[events['user_id'].isin(group_b_filtered['user_id'])].pivot_table(
    index='user_id',
    columns='event_name',
    values='event_dt',
    aggfunc='min'
)

# Embudos
def funnel (group):
    step_1 = ~group['product_page'].isna()
    step_2 = step_1 & (group['product_cart'] > group['product_page'])
    step_3 = step_2 & (group['purchase'] > group['product_cart'])

    n_product_page = group[step_1].shape[0]
    n_product_cart = group[step_2].shape[0]
    n_purchase = group[step_3].shape[0]

    print('Ve un producto:', n_product_page)
    print('Agrega un producto:', n_product_cart)
    print('Realiza la compra:', n_purchase)
    print('/nConversión')
    print('Visita de pagina --> Agregar al carrito', (n_product_cart/n_product_page)*100)
    print('Agregar al carrito --> Realiza la compra:', (n_purchase/n_product_cart)*100)

funnel_a = funnel(group_a_pivot)
funnel_b = funnel(group_b_pivot)
# Se ve incremento en la conversión de la visitas a la página de los productos, agregar al carrito y realiza la compra.

def funnel2 (group):
    step_1 = ~group['product_page'].isna()
    step_2 = step_1 & (group['product_cart'] > group['product_page'])
    step_3 = step_2 & (group['purchase'] > group['product_cart'])

    n_product_page = group[step_1].shape[0]
    n_product_cart = group[step_2].shape[0]
    n_purchase = group[step_3].shape[0]
    return n_product_page, n_product_cart, n_purchase

n_product_page_a, n_product_cart_a, n_purchase_a = funnel2(group_a_pivot)
n_product_page_b, n_product_cart_b, n_purchase_b = funnel2(group_b_pivot)

# Prueba de hipótesis de proporciones.
alpha = 0.5

purchases = np.array([n_purchase_a, n_purchase_b])
cart = np.array([n_product_cart_a, n_product_cart_b])
visit = np.array([n_product_page_a, n_product_page_b])

# Prueba para proporciones product_card → purchase
p1 = purchases[0]/cart[0]

p2 = purchases[1]/cart[1]

p_combined = (purchases[0] + purchases[1]) / (cart[0] + cart[1])

difference = p1 - p2

z_value = difference / mth.sqrt(p_combined * (1 - p_combined) * (1/cart[0] + 1/cart[1]))
distr = st.norm(0, 1)

p_value = (1 - distr.cdf(abs(z_value))) * 2

print('p-value: ', p_value)

if (p_value < alpha):
    print("Rechazar la hipótesis nula: hay una diferencia significativa entre las proporciones")
else:
    print("No se pudo rechazar la hipótesis nula: no hay razón para pensar que las proporciones son diferentes")

# Prueba para proporciones product_page → product_card
p1 = cart[0]/visit[0]

p2 = cart[1]/visit[1]

p_combined = (cart[0] + cart[1]) / (visit[0] + visit[1])

difference = p1 - p2

z_value = difference / mth.sqrt(p_combined * (1 - p_combined) * (1/visit[0] + 1/visit[1]))
distr = st.norm(0, 1)

p_value = (1 - distr.cdf(abs(z_value))) * 2

print('p-value: ', p_value)

if (p_value < alpha):
    print("Rechazar la hipótesis nula: hay una diferencia significativa entre las proporciones")
else:
    print("No se pudo rechazar la hipótesis nula: no hay razón para pensar que las proporciones son diferentes")