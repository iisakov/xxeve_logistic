import csv
import os
from time import sleep

import requests as r
import sqlite3

from pprint import pprint
from datetime import datetime

import config

debug = False
# debug = True


def get_entity_list(entity: str) -> list:
    end_point = 'markets' if 'market' in entity else 'universe'
    entity = entity.split('_')[1] if 'market' in entity else entity
    response = []
    page = 1
    while page:
        response += r.get(f'https://esi.evetech.net/latest/{end_point}/{entity}/?datasource=tranquility&page={page}').json()
        page = page + 1 if len(response) % 100 == 0 else False
    return response


def get_corporations_list():
    request_str = f'https://esi.evetech.net/latest/corporations/npccorps/?datasource=tranquility'
    response = r.get(request_str)
    if debug: print('get_corporations_list ------------------------------------------------', request_str)
    if debug: print('get_corporations_list ------------------------------------------------', response)
    response = response.json()
    return response


def get_entity(entity: str, entity_id: int, language: str = 'ru') -> list:
    request_str = f'https://esi.evetech.net/latest/universe/{entity}/{entity_id}/?datasource=tranquility&language={language}'
    response = r.get(request_str)
    if debug: print('get_entity ------------------------------------------------', request_str)
    if debug: print('get_entity ------------------------------------------------', response)
    response = response.json()

    return response


def get_kills_and_jumps() -> list:
    response_kills = r.get('https://esi.evetech.net/latest/universe/system_kills/?datasource=tranquility').json()
    response_jumps = r.get('https://esi.evetech.net/latest/universe/system_jumps/?datasource=tranquility').json()
    systems_stats = {stat['system_id']: {'npc_kills': 0,
                                         'pod_kills': 0,
                                         'ship_kills': 0,
                                         'system_id': stat['system_id'],
                                         'snap_id': datetime.now().strftime("%Y%m%d%H"),
                                         'ship_jumps': stat['ship_jumps']} for stat in response_jumps}

    for kill in response_kills:
        if kill['system_id'] in systems_stats.keys():
            # try:
            #     systems_stats[kill['system_id']] = systems_stats[kill['system_id']] | kill
            # except:
                for kill_k, kill_v in kill.items():
                    systems_stats[kill['system_id']][kill_k] = kill_v
        else:
            # try:
            #     systems_stats[kill['system_id']] = kill | {'ship_jumps': 0, 'snap_id': datetime.now().strftime("%Y%m%d%H")}
            # except:
                for jump_k, jump_v in {'ship_jumps': 0, 'snap_id': datetime.now().strftime("%Y%m%d%H")}.items():
                    kill[jump_k] = jump_v
                systems_stats[kill['system_id']] = kill
    return list(systems_stats.values())


def get_killmail(killmail_id, killmail_hash) -> dict:
    if debug: print('get_killmail ------------------------------------------------')
    request_str = f'https://esi.evetech.net/latest/killmails/{killmail_id}/{killmail_hash}'
    if debug: print('get_killmail: request_str', request_str)
    response = r.get(request_str)
    while response.status_code != 200:
        if debug: print('get_killmail ------------------------------------------------', response.status_code, response.text)
        sleep(2)
        response = r.get(request_str)
    if debug: print('get_killmail ------------------------------------------------', request_str)
    if debug: print('get_killmail ------------------------------------------------', response)
    response = response.json()
    return response


def get_alliance(alliance_id) -> dict:
    request_str = f'https://esi.evetech.net/latest/alliances/{alliance_id}/?datasource=tranquility'
    response = r.get(request_str)
    if response.status_code == 404:
        return {key: 0 for key in config.alliances_fields.keys()}
    while response.status_code != 200:
        if debug: print('get_alliance ------------------------------------------------', response.status_code, response.text)
        sleep(2)
        response = r.get(request_str)
    if debug: print('get_alliance ------------------------------------------------', request_str)
    if debug: print('get_alliance ------------------------------------------------', response)

    response = response.json()
    return response


def get_alliance_killmails(alliance_id, wright: bool = None):
    if wright:
        killmails_list = get_zkb_mails('xxeve_logistic.db', 'alliances', alliance_id, all_mails=True)
        if len(killmails_list) > 0:
            wright_killmails_to_db(killmails_list)


def get_corporation(corporation_id) -> dict:
    request_str = f'https://esi.evetech.net/latest/corporations/{corporation_id}/?datasource=tranquility'
    response = r.get(request_str)
    if response.status_code == 404:
        return {key: 0 for key in config.corporations_fields.keys()}
    while response.status_code != 200:
        if debug: print('get_corporation ------------------------------------------------', response.status_code, response.text)
        sleep(2)
        response = r.get(request_str)
    if debug: print('get_corporation ------------------------------------------------', request_str)
    if debug: print('get_corporation ------------------------------------------------', response)
    response = response.json()

    return response


def get_corporation_killmails(corporation_id, wright: bool = None):
    if wright:
        killmails_list = get_zkb_mails('xxeve_logistic.db', 'corporations', corporation_id, all_mails=True)
        if len(killmails_list) > 0:
            wright_killmails_to_db(killmails_list)


def get_characters(character_id, wright: bool = None):
    request_str = f'https://esi.evetech.net/latest/characters/{character_id}/?datasource=tranquility'
    name_db = 'xxeve_logistic.db'
    response = r.get(request_str)
    if debug: print('get_characters ------------------------------------------------', request_str)
    if debug: print('get_characters ------------------------------------------------', response)
    if response.status_code == 404:
        return None
    while response.status_code != 200:
        if debug: print('get_characters ------------------------------------------------', response.status_code, response.text)
        sleep(2)
        response = r.get(request_str)
    response = response.json()
    response['character_id'] = character_id
    response['description'] = response['description'].replace(',', ' ')
    if 'corporation_id' in response:
        if len(select_entity(name_db, 'corporations', 'corporation_id', response['corporation_id'], limit='one')) != 0:
            print(select_entity(name_db, 'corporations', 'corporation_id', response['corporation_id'], limit='one'))
        else:
            corporation_info = get_corporation(response['corporation_id'])
            corporation_info['corporation_id'] = response['corporation_id']
            response['corporation_name'] = corporation_info['name']
            if wright:
                wright_to_db(name_db, 'corporations', preparing_values(corporation_info, config.corporations_fields))
                get_corporation_killmails(corporation_info['corporation_id'])
            if 'alliance_id' in response:
                if len(select_entity(name_db, 'alliances', 'alliance_id', response['alliance_id'], limit='one')) != 0:
                    print(select_entity(name_db, 'alliances', 'alliance_id', response['alliance_id'], limit='one'))
                else:
                    alliance_info = get_alliance(response['alliance_id'])
                    alliance_info['alliance_id'] = response['alliance_id']
                    response['alliance_name'] = alliance_info['name']
                    if wright:
                        wright_to_db(name_db, 'alliances', preparing_values(alliance_info, config.alliances_fields))
                        get_alliance_killmails(alliance_info['alliance_id'])
                        alliances_corporations_info = {'alliance_id': alliance_info['alliance_id'], 'corporation_id': corporation_info['corporation_id']}
                        wright_to_db(name_db, 'alliances_corporations', preparing_values(alliances_corporations_info, config.alliances_corporations_fields))
    if wright:
        try:
            wright_to_db(name_db, 'characters', preparing_values(response, config.characters_fields))
        except:
            print(preparing_values(response, config.characters_fields))
    return response


def get_route(origin: int, destination: int, flag: str = 'shortest') -> list:
    request_str = f'https://esi.evetech.net/latest/route/{origin}/{destination}/?datasource=tranquility&flag={flag}'
    response = r.get(request_str)
    if debug: print('get_route ------------------------------------------------', request_str)
    if debug: print('get_route ------------------------------------------------', response)
    response = response.json()

    return response


def get_zkb_mails(name_db, entity: str, entity_id: int, past_seconds: int = None, all_mails: bool = False, limit=50):
    entity_dict = {'systems':       'solarSystemID',
                   'regions':       'regionID',
                   'characters':    'characterID',
                   'corporations':  'corporationID',
                   'alliances':     'allianceID'}

    if debug: print('get_zkb_mails ------------------------------------------------', entity_id)

    entity = entity_dict[entity]

    if all_mails:
        response = []
        page = 1
        while page and page < 3:
            request_str = f'https://zkillboard.com/api/kills/{entity}/{entity_id}/page/{page}/'
            response_piece = r.get(request_str)
            while response_piece.status_code != 200:
                if debug: print('get_zkb_mails ------------------------------------------------', response_piece.status_code, response_piece.text)
                sleep(2)
                response_piece = r.get(request_str)
            response += response_piece.json()
            page = page + 1 if len(response) % 100 == 0 else False
    else:
        request_str = f'https://zkillboard.com/api/kills/{entity}/{entity_id}/pastSeconds/{past_seconds}/' if past_seconds != 0 else f'https://zkillboard.com/api/kills/{entity}/{entity_id}/'
        response = r.get(request_str)

        while response.status_code != 200:
            if debug: print('get_zkb_mails ------------------------------------------------', response.status_code, response.text)
            sleep(2)
            response = r.get(request_str)

        if debug: print('get_zkb_mails ------------------------------------------------', request_str)
        if debug: print('get_zkb_mails ------------------------------------------------', response)
        response = response.json()
    response = response[:limit] if limit is not None else response
    past_seconds = 'всё время' if past_seconds is None else round(past_seconds/60)
    print(f'За последние {past_seconds} минут, найдено', len(response), 'killmail`а')
    if None in response:
        response = []
    if len(response) == 0:
        return None
    result = {}

    for i, killmail in enumerate(response):
        print(f'Осталось {len(response) - i}')
        if len(select_entity(name_db, 'killmails', 'killmail_id', killmail['killmail_id'], limit='one')) != 0:
            print(select_entity(name_db, 'killmails', 'killmail_id', killmail['killmail_id'], limit='one'))
            continue

        result[killmail['killmail_id']] = {'attackers': {}}
        print('killmail_id:', killmail['killmail_id'])
        killmail_info = get_killmail(killmail['killmail_id'], killmail['zkb']['hash'])

        result[killmail['killmail_id']]['killmail_id'] = killmail['killmail_id']
        result[killmail['killmail_id']]['location_id'] = killmail['zkb']['locationID'] if 'locationID' in killmail['zkb'] else -1
        result[killmail['killmail_id']]['fitted_value'] = killmail['zkb']['fittedValue']
        result[killmail['killmail_id']]['dropped_value'] = killmail['zkb']['droppedValue'] if 'droppedValue' in killmail['zkb'] else 0
        result[killmail['killmail_id']]['destroyed_value'] = killmail['zkb']['destroyedValue'] if 'destroyedValue' in killmail['zkb'] else 0
        result[killmail['killmail_id']]['destroyed_value'] = killmail['zkb']['destroyedValue'] if 'destroyedValue' in killmail['zkb'] else 0
        result[killmail['killmail_id']]['total_value'] = killmail['zkb']['totalValue']
        result[killmail['killmail_id']]['points'] = killmail['zkb']['points']
        result[killmail['killmail_id']]['npc'] = killmail['zkb']['npc']
        result[killmail['killmail_id']]['solo'] = killmail['zkb']['solo']
        result[killmail['killmail_id']]['awox'] = killmail['zkb']['awox']
        result[killmail['killmail_id']]['killmail_time'] = killmail_info['killmail_time']
        result[killmail['killmail_id']]['system_id'] = killmail_info['solar_system_id']

        if not check_entity_in_table(name_db, 'systems', 'system_id', killmail_info['solar_system_id']):
            system_info = get_entity('systems', killmail_info['solar_system_id'])
            system_info = convert_position(system_info)
            wright_to_db(name_db, 'systems', preparing_values(system_info, config.systems_fields))
        result[killmail['killmail_id']]['system_name'] = select_entity(name_db, 'systems', 'system_id', killmail_info['solar_system_id'])['name']

        for attacker in range(len(killmail_info['attackers'])):
            result[killmail['killmail_id']]['attackers'][attacker] = {}

            if debug: print('----------------------------------------------------------------------', killmail_info['attackers'])
            if 'alliance_id' in killmail_info['attackers'][attacker]:
                if len(select_entity(name_db, 'alliances', 'alliance_id', killmail_info['attackers'][attacker]['alliance_id'], limit='one')) != 0:
                    print(select_entity(name_db, 'alliances', 'alliance_id', killmail_info['attackers'][attacker]['alliance_id'], limit='one'))
                else:
                    result[killmail['killmail_id']]['attackers'][attacker]['attacker_alliance_id'] = killmail_info['attackers'][attacker]['alliance_id']
                    result[killmail['killmail_id']]['attackers'][attacker]['attacker_alliance_name'] = get_alliance(killmail_info['attackers'][attacker]['alliance_id'])['name']

            if 'corporation_id' in killmail_info['attackers'][attacker]:
                if len(select_entity(name_db, 'corporations', 'corporation_id', killmail_info['attackers'][attacker]['corporation_id'], limit='one')) != 0:
                    print(select_entity(name_db, 'corporations', 'corporation_id', killmail_info['attackers'][attacker]['corporation_id'], limit='one'))
                else:
                    result[killmail['killmail_id']]['attackers'][attacker]['attacker_corporation_id'] = killmail_info['attackers'][attacker]['corporation_id']
                    result[killmail['killmail_id']]['attackers'][attacker]['attacker_corporation_name'] = get_corporation(killmail_info['attackers'][attacker]['corporation_id'])['name']

            if 'weapon_type_id' in killmail_info['attackers'][attacker]:
                result[killmail['killmail_id']]['attackers'][attacker]['attacker_weapon_type_id'] = killmail_info['attackers'][attacker]['weapon_type_id']
                result[killmail['killmail_id']]['attackers'][attacker]['attacker_weapon_name'] = select_entity(name_db, 'types', 'type_id', killmail_info['attackers'][attacker]['weapon_type_id'])['name']

            if 'ship_type_id' in killmail_info['attackers'][attacker]:
                result[killmail['killmail_id']]['attackers'][attacker]['attacker_ship_name'] = select_entity(name_db, 'types', 'type_id', killmail_info['attackers'][attacker]['ship_type_id'])['name']
                result[killmail['killmail_id']]['attackers'][attacker]['attacker_ship_id'] = killmail_info['attackers'][attacker]['ship_type_id']

            result[killmail['killmail_id']]['attackers'][attacker]['killmail_id'] = killmail['killmail_id']
            result[killmail['killmail_id']]['attackers'][attacker]['attacker_id'] = attacker
            result[killmail['killmail_id']]['attackers'][attacker]['attacker_damage_done'] = killmail_info['attackers'][attacker]['damage_done']
            result[killmail['killmail_id']]['attackers'][attacker]['attacker_final_blow'] = killmail_info['attackers'][attacker]['final_blow']
            result[killmail['killmail_id']]['attackers'][attacker]['attacker_security_status'] = killmail_info['attackers'][attacker]['security_status']
            result[killmail['killmail_id']]['attackers'][attacker]['attacker_character_id'] = killmail_info['attackers'][attacker]['character_id'] if 'character_id' in killmail_info['attackers'][attacker] else "NULL"

        if 'alliance_id' in killmail_info['victim']:
            if len(select_entity(name_db, 'alliances', 'alliance_id', killmail_info['victim']['alliance_id'], limit='one')) != 0:
                print(select_entity(name_db, 'alliances', 'alliance_id', killmail_info['victim']['alliance_id'], limit='one'))
            else:
                result[killmail['killmail_id']]['victim_alliance_id'] = killmail_info['victim']['alliance_id']
                result[killmail['killmail_id']]['victim_alliance_name'] = get_alliance(killmail_info['victim']['alliance_id'])['name']

        if 'corporation_id' in killmail_info['victim']:
            if len(select_entity(name_db, 'corporations', 'corporation_id', killmail_info['victim']['corporation_id'], limit='one')) != 0:
                print(select_entity(name_db, 'corporations', 'corporation_id', killmail_info['victim']['corporation_id'], limit='one'))
            else:
                result[killmail['killmail_id']]['victim_corporation_id'] = killmail_info['victim']['corporation_id']
                result[killmail['killmail_id']]['victim_corporation_name'] = get_corporation(killmail_info['victim']['corporation_id'])['name']

        if 'ship_type_id' in killmail_info['victim']:
            result[killmail['killmail_id']]['victim_ship_name'] = select_entity(name_db, 'types', 'type_id', killmail_info['victim']['ship_type_id'])['name']
            result[killmail['killmail_id']]['victim_ship_id'] = killmail_info['victim']['ship_type_id']

        result[killmail['killmail_id']]['victim_character_id'] = killmail_info['victim']['character_id'] if 'character_id' in killmail_info['victim'] else "NULL"
        result[killmail['killmail_id']]['victim_id'] = killmail['killmail_id']
        result[killmail['killmail_id']]['victim_damage_taken'] = killmail_info['victim']['damage_taken']
        result[killmail['killmail_id']]['victim_position_x'] = killmail_info['victim']['position']['x'] if 'position' in killmail_info['victim'] else 0
        result[killmail['killmail_id']]['victim_position_y'] = killmail_info['victim']['position']['y'] if 'position' in killmail_info['victim'] else 0
        result[killmail['killmail_id']]['victim_position_z'] = killmail_info['victim']['position']['z'] if 'position' in killmail_info['victim'] else 0
        wright_killmails_to_db({killmail['killmail_id']: result[killmail['killmail_id']]})
    return result


def preparing_values(row, table_fields) -> dict:
    prepared_values = {'create_date':   f'"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"',
                       'create_by':     f'"system"'}
    for field, value in table_fields.items():
        if field in row:
            prepared_value = str(row[field]).replace('"', '')
            if 'TEXT' in table_fields[field]:
                prepared_values[field] = f'"{prepared_value}"'
            else:
                prepared_values[field] = prepared_value
    return prepared_values


def wright_to_db(name_db, name_table, row, bg=False) -> bool:
    if debug: print('-------------------------------------------------------------------------------------------wright_to_db')
    if debug: print('wright_to_db: row', row)
    check_row = {key: row[key] for key in row if key not in ['create_date', 'create_by']}
    if debug: print('wright_to_db: check_row', check_row)
    connection_db = sqlite3.connect(name_db)
    select_pks_str = f"select name from pragma_table_info('{name_table}') WHERE pk != 0"
    if debug: print('wright_to_db: select_pks_str', select_pks_str)
    pks = connection_db.cursor().execute(select_pks_str).fetchall()
    if debug: print('wright_to_db: pks', pks)
    if len(pks) > 1:
        pk_str = ' and '.join([f'{pk[0]} = {row[pk[0]]}' for pk in pks])
    else:
        pk_str = f'{pks[0][0]} = {row[pks[0][0]]}'
    if debug: print('wright_to_db: pk_str', pk_str)

    if check_row_in_table(name_db=name_db, name_table=name_table, row=check_row):
        if not bg: print(f'В таблице {name_table} существует запись.')
        return False

    elif check_entity_in_table(name_db=name_db, name_table=name_table, fv_str=pk_str):
        if not bg: print(f'В таблице {name_table} существует запись c {pk_str}.')
        update_values_str = ', '.join([f'{key} = {value}' for key, value in row.items()])
        request_str = f'''UPDATE {name_table} SET {update_values_str} WHERE {pk_str}'''
        if debug: print('check_entity_in_table: update_values_str', update_values_str)

    else:
        if not bg: print(f'Запись не существует.')
        fields_str = ', '.join(row)
        value_str = ', '.join([row[fields] for fields in row])
        request_str = f'''INSERT INTO {name_table} ({fields_str}) VALUES ({value_str})'''

    connection_db.cursor().execute(request_str)
    try:
        connection_db.commit()
    except:
        print('\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tне записали ):\n\n\n\n\n\n\n\n\n\n')
    connection_db.close()
    return True


def wright_killmails_to_db(killmails_info):
    for killmail_k, killmail_v in killmails_info.items():
        killmail_row = preparing_values(killmail_v, config.killmails_fields)

        if not check_row_in_table(name_db='xxeve_logistic.db', name_table='killmails', row=killmail_row):
            print(f'В таблице killmails не существует запись. {killmail_k}')
            wright_to_db('xxeve_logistic.db', 'killmails', killmail_row)
        print(f'В таблице killmails существует запись. {killmail_k}')

        victims_row = preparing_values(killmail_v, config.victims_fields)
        if not check_row_in_table(name_db='xxeve_logistic.db', name_table='victims', row=victims_row):
            print(f'В таблице victims не существует запись. {killmail_k}')
            wright_to_db('xxeve_logistic.db', 'victims', victims_row)
        print(f'В таблице victims существует запись. {killmail_k} - victim_id: {victims_row["victim_id"]}')

        for attacker in killmail_v['attackers'].values():
            attackers_row = preparing_values(attacker, config.attackers_fields)
            if not check_row_in_table(name_db='xxeve_logistic.db', name_table='attackers', row=attackers_row):
                print(f'В таблице attackers не существует запись. {killmail_k}')
                wright_to_db('xxeve_logistic.db', 'attackers', attackers_row)
            print(f'В таблице attackers существует запись. {killmail_k} - attacker_character_id: {attackers_row["attacker_character_id"]}')


def convert_position(row) -> dict:
    if debug: print('-------------------------------------------------------------------------------------------convert_position')
    position = row['position']
    result = row | {f'position_{key}': value for key, value in position.items()}
    return result


def check_row_in_table(name_db, name_table, row):
    if debug: print('-------------------------------------------------------------------------------------------check_row_in_table')
    connection_db = sqlite3.connect(name_db)
    values_check_str = ' and '.join([f'{key} = {value}' for key, value in row.items() if key not in ['create_date', 'create_by']])
    select_str = f'''SELECT * FROM {name_table} WHERE {values_check_str}'''
    if debug: print('check_row_in_table: select_str', select_str)
    response = connection_db.cursor().execute(select_str).fetchone()
    return True if response else False


def check_entity_in_table(name_db, name_table, entity_field=None, entity_value=None, fv_str=None):
    if debug: print('-------------------------------------------------------------------------------------------check_entity_in_table')
    connection_db = sqlite3.connect(name_db)
    if fv_str is None:
        select_str = f'''SELECT * FROM {name_table} WHERE {entity_field} = {entity_value}'''
    else:
        select_str = f'''SELECT * FROM {name_table} WHERE {fv_str}'''
    response = connection_db.execute(select_str).fetchone()
    return True if response is not None else False


def select_entity(name_db, name_table, entity_field, entity_value, limit='one') -> dict:
    if type(entity_value) is str:
        entity_value = entity_value.replace('"', '')
        entity_value = f'"{entity_value}"'
    connection_db = sqlite3.connect(name_db)
    select_str = f'''SELECT * FROM {name_table} WHERE {entity_field} = {entity_value}'''
    if debug: print('select_entity ------------------------------------------------', select_str)
    cursor = connection_db.execute(select_str)

    response = cursor.fetchall()
    result_list = []
    for entity_response in response:
        result_list.append({field[0]: entity_response[i] for i, field in enumerate(cursor.description)})
    if limit in ['all', 'one']:
        if limit == 'one':
            result = result_list[0] if len(result_list) > 0 else []
        else:
            result = result_list
    elif type(limit) == int and limit < len(result_list):
        result = result_list[:limit]
    else:
        result = False

    return result


def select_all_in_table(name_db, name_table):
    connection_db = sqlite3.connect(name_db)
    select_str = f'''SELECT * FROM {name_table}'''
    cursor = connection_db.execute(select_str)
    response = cursor.fetchall()
    result = []
    for entity_response in response:
        result.append({field[0]: entity_response[i] for i, field in enumerate(cursor.description)})
    return result


def append_script_file(path_to_script_file, name_table, name_db):
    connection_db = sqlite3.connect(name_db)
    select_str = f'''SELECT * FROM {name_table}'''
    cursor = connection_db.cursor().execute(select_str)
    header_table = ','.join([x[0] for x in cursor.description])
    with open(path_to_script_file, "a", encoding='utf-8') as script_file:
        script_file.write(f"copy {name_table}({header_table}) from STDIN DELIMITERS ',' CSV HEADER;\n")


def get_route_info(system_from, system_to):
    main_path = 'rote_info'
    result: dict = {'system_attackers_killmail_info':   [],
                    'system_victims_killmail_info':     []}

    route = get_route(select_entity(name_db='xxeve_logistic.db', name_table='systems', entity_field='name', entity_value=system_to)['system_id'],
                      select_entity(name_db='xxeve_logistic.db', name_table='systems', entity_field='name', entity_value=system_from)['system_id'])
    dir_path = f'{main_path}/{datetime.now().strftime("%Y-%m-%d-%H%M%S")}_{system_from}_{system_to}'
    os.makedirs(dir_path)
    for waypoint in route:
        result['system_info'] = select_entity(name_db='xxeve_logistic.db', name_table='systems', entity_field='system_id', entity_value=waypoint)
        result['system_snap_info'] = select_entity(name_db='xxeve_logistic.db', name_table='snap_statistic_systems', entity_field='system_id', entity_value=waypoint, limit='all')
        result['system_killmail_info'] = select_entity(name_db='xxeve_logistic.db', name_table='killmails', entity_field='system_id', entity_value=waypoint, limit='all')
        for killmail in result['system_killmail_info']:
            result['system_attackers_killmail_info'] += select_entity(name_db='xxeve_logistic.db', name_table='attackers', entity_field='killmail_id', entity_value=killmail['killmail_id'], limit='all')
            result['system_victims_killmail_info'] += select_entity(name_db='xxeve_logistic.db', name_table='victims', entity_field='killmail_id', entity_value=killmail['killmail_id'], limit='all')

        for table in result:
            file_path = f'{dir_path}/{waypoint}_{table}.csv'
            if type(result[table]) == list:
                if len(result[table]) > 0:
                    with open(f'{file_path}', 'w', newline='') as fp:
                        fieldnames = list(result[table][0].keys())
                        writer = csv.DictWriter(fp, fieldnames)
                        writer.writeheader()
                        writer.writerows(result[table])
                else:
                    continue
            else:
                with open(f'{file_path}', 'w', newline='') as fp:
                    fieldnames = list(result[table].keys())
                    writer = csv.DictWriter(fp, fieldnames)
                    writer.writeheader()
                    writer.writerow(result[table])

    for table in result:
        list_tab_file = [name for name in os.listdir(dir_path) if str(table) in name]
        if type(result[table]) == list:
            if len(result[table]) > 0:
                header = list(result[table][0].keys())
                with open(f'{dir_path}/{table}.csv', 'w', newline='') as fcsv:
                    writer = csv.writer(fcsv)
                    writer.writerow(header)
                    for file_from_name in list_tab_file:
                        reader = csv.reader(open(dir_path + '/' + file_from_name, 'r'))
                        for row in list(reader)[1:]:
                            writer.writerow(row)
        else:
            header = list(result[table].keys())
            with open(f'{dir_path}/{table}.csv', 'w', newline='') as fcsv:
                writer = csv.writer(fcsv)
                writer.writerow(header)
                for file_from_name in list_tab_file:
                    reader = csv.reader(open(dir_path + '/' + file_from_name, 'r'))
                    for row in list(reader)[1:]:
                        writer.writerow(row)


def table_to_cvs(name_table, info, name_folder='table_info'):
    if not os.path.isdir(name_folder):
        os.makedirs(name_folder)
        os.makedirs(name_folder+'/csv')
    dir_path = 'table_info/csv'

    file_path = f'{dir_path}/{name_table}.csv'
    with open(f'{file_path}', 'w', newline='', encoding="utf-8") as fp:
        fieldnames = list(info[0].keys())
        writer = csv.DictWriter(fp, fieldnames)
        writer.writeheader()
        writer.writerows(info)


def print_route_waypoints_name(extreme_points_list):
    system_name_list = []
    for system_id in get_route(select_entity(
            name_db='xxeve_logistic.db',
            name_table='systems',
            entity_field=extreme_points_list[0][0]['field'],
            entity_value=f'"{extreme_points_list[0][0]["value"]}"')['system_id'],
        select_entity(name_db='xxeve_logistic.db',
                      name_table='systems',
                      entity_field=extreme_points_list[0][1]['field'],
                      entity_value=f'"{extreme_points_list[0][1]["value"]}"')['system_id']):
        system_name_list.append(
            select_entity('xxeve_logistic.db', 'systems', entity_field='system_id', entity_value=system_id)['name'])

    print(system_name_list)
