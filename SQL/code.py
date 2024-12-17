# importar librerías
import pandas as pd
from sqlalchemy import create_engine


db_config = {'user': 'practicum_student',         # nombre de usuario
             'pwd': 's65BlTKV3faNIGhmvJVzOqhs', # contraseña
             'host': 'rc1b-wcoijxj3yxfsf3fs.mdb.yandexcloud.net',
             'port': 6432,              # puerto de conexión
             'db': 'data-analyst-final-project-db'}          # nombre de la base de datos

connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                                     db_config['pwd'],
                                                                       db_config['host'],
                                                                       db_config['port'],
                                                                       db_config['db'])

engine = create_engine(connection_string, connect_args={'sslmode':'require'})

# Encuentra el número de libros publicados después del 1 de enero de 2000.
# query

query = ''' SELECT COUNT(title) AS cnt
            FROM books
            WHERE publication_date::date > '2000-01-01'
        '''

published_books = pd.io.sql.read_sql(query, con = engine)
display(published_books)

# Encuentra el número de reseñas de usuarios y la calificación promedio para cada libro.
# query 
query = ''' SELECT AVG(rating) AS avg
            FROM ratings
            GROUP BY book_id
        '''

avg_rating = pd.io.sql.read_sql(query, con = engine)
display(avg_rating)

# Identifica la editorial que ha publicado el mayor número de libros con más de 50 páginas (esto te ayudará a excluir folletos y publicaciones similares de tu análisis).
# query 
query = ''' SELECT publisher_id, COUNT(DISTINCT book_id) AS books_pub
            FROM books
            WHERE num_pages > 50
            GROUP BY publisher_id
            ORDER BY books_pub DESC
            LIMIT 5
        '''

publisher = pd.io.sql.read_sql(query, con = engine)
display(publisher)

# Identifica al autor que tiene la más alta calificación promedio del libro: mira solo los libros con al menos 50 calificaciones.
# query 
query = ''' SELECT AVG(rating) AS avg, COUNT(title) AS books_ratings
            FROM ratings
              INNER JOIN books ON books.book_id = ratings.book_id
            WHERE books_ratings > 50
            GROUP BY book_id
            ORDER BY books_ratings DESC
            LIMIT 5
        '''

author_rat = pd.io.sql.read_sql(query, con = engine)
display(author_rat)