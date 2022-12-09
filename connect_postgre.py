import psycopg2


def drop_tables():
    conn = psycopg2.connect("""
        host=rc1a-b1vaxoaauogz0wkd.mdb.yandexcloud.net
        port=6432
        sslmode=verify-full
        dbname=xxeve_logistic
        user=iisakov
        password=xxeve_iisakov
        target_session_attrs=read-write
    """)

    q = conn.cursor()
    with open('recreat_table.txt', 'r', encoding='utf-8') as query_file:
        reader = query_file.readlines()
        query_list = []
        for row in reader:
            query_list.append(row[:-1])
    q.execute('\n'.join(query_list))

    conn.commit()
    conn.close()
    print('Дропнули и создали таблицы заново')



def reload_data():
    conn = psycopg2.connect("""
        host=rc1a-b1vaxoaauogz0wkd.mdb.yandexcloud.net
        port=6432
        sslmode=verify-full
        dbname=xxeve_logistic
        user=iisakov
        password=xxeve_iisakov
        target_session_attrs=read-write
    """)

    q = conn.cursor()

    with open('load_script.script') as load_script_file:
        reader = load_script_file.readlines()
        for row in reader:
            name_table = row.split('(')[0].split(' ')[1]
            q.copy_expert(row, open(f'/mnt/c/DataScience/Projects/eve_artisаn_sole_trader/table_info/csv/{name_table}_prepared.csv', 'r', encoding='utf-8'))
            print(f'{name_table} Залили.')
    conn.commit()
    conn.close()
