import sqlite3
import config


def check_exist_table(name_db, name_table):
    connection_db = sqlite3.connect(name_db)
    request_str = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name_table}'"
    response = connection_db.execute(request_str).fetchall()
    return True if len(response) > 0 else False


def create_table(name_db, name_table, fields: dict) -> bool:
    if not check_exist_table(name_db, name_table):
        print(f'Создаём таблицу {name_db}.{name_table}.')
        connection_db = sqlite3.connect(name_db)
        fields_str = ', '.join([f'{x} {" ".join(fields[x])}' for x in fields])
        request_str = f'''CREATE TABLE {name_table}({fields_str})'''

        print(request_str)
        connection_db.cursor().execute(request_str)
        connection_db.close()
    else:
        print(f'Таблица {name_db}.{name_table} существует.')
    return True


create_table(name_db='xxeve_logistic.db', name_table='regions', fields=config.regions_fields)
create_table(name_db='xxeve_logistic.db', name_table='constellations', fields=config.constellations_fields)
create_table(name_db='xxeve_logistic.db', name_table='systems', fields=config.systems_fields)
create_table(name_db='xxeve_logistic.db', name_table='market_groups', fields=config.market_groups_fields)
create_table(name_db='xxeve_logistic.db', name_table='categories', fields=config.categories_fields)
create_table(name_db='xxeve_logistic.db', name_table='groups', fields=config.groups_fields)
create_table(name_db='xxeve_logistic.db', name_table='types', fields=config.types_fields)
create_table(name_db='xxeve_logistic.db', name_table='orders', fields=config.orders_fields)
create_table(name_db='xxeve_logistic.db', name_table='snap_statistic_systems', fields=config.snap_statistic_systems_fields)
create_table(name_db='xxeve_logistic.db', name_table='entity_list', fields=config.entity_list_fields)
create_table(name_db='xxeve_logistic.db', name_table='killmails', fields=config.killmails_fields)
create_table(name_db='xxeve_logistic.db', name_table='attackers', fields=config.attackers_fields)
create_table(name_db='xxeve_logistic.db', name_table='victims', fields=config.victims_fields)
create_table(name_db='xxeve_logistic.db', name_table='characters', fields=config.characters_fields)
create_table(name_db='xxeve_logistic.db', name_table='characters_killmails', fields=config.characters_killmails_fields)
create_table(name_db='xxeve_logistic.db', name_table='corporations', fields=config.corporations_fields)
create_table(name_db='xxeve_logistic.db', name_table='corporations_killmails', fields=config.corporations_killmails_fields)
create_table(name_db='xxeve_logistic.db', name_table='alliances', fields=config.alliances_fields)
create_table(name_db='xxeve_logistic.db', name_table='alliances_corporations', fields=config.alliances_corporations_fields)
