import yaml
import SQL_tools
import config
import os


def load_info():
    for entity in ['regions', 'constellations', 'systems', 'categories', 'groups', 'market_groups']:
        response = [{'entity_code': entity, 'entity_id': entity_id} for entity_id in SQL_tools.get_entity_list(entity)]
        for row in response:
            SQL_tools.wright_to_db('xxeve_logistic.db', 'entity_list', SQL_tools.preparing_values(row, config.entity_list_fields))

    for corporation_id in SQL_tools.get_corporations_list():
        corporation_info = SQL_tools.get_corporation(corporation_id)
        corporation_info['corporation_id'] = corporation_id
        SQL_tools.wright_to_db('xxeve_logistic.db', 'corporations', SQL_tools.preparing_values(corporation_info, config.corporations_fields))

    for region in SQL_tools.get_entity_list('regions'):
        if not SQL_tools.check_entity_in_table('xxeve_logistic.db', 'regions', 'region_id', region):
            region_info = SQL_tools.preparing_values(SQL_tools.get_entity('regions', region), config.regions_fields)
            print(region_info)
            SQL_tools.wright_to_db('../xxeve_logistic.db', 'regions', region_info)
        else:
            print(f'Запись с {region} существует.')

    for constellation in SQL_tools.get_entity_list('constellations'):
        if not SQL_tools.check_entity_in_table('../xxeve_logistic.db', 'constellations', 'constellation_id', constellation):
            constellation_info = SQL_tools.preparing_values(SQL_tools.convert_position(SQL_tools.get_entity('constellations', constellation)), config.constellations_fields)
            SQL_tools.wright_to_db('xxeve_logistic.db', 'constellations', constellation_info)
        else:
            print(f'Запись с {constellation} существует.')

    categories = yaml.safe_load(open('../sde/sde/fsd/categoryIDs.yaml', encoding='utf-8'))
    for category_k, category_v in categories.items():
        category_v['category_id'] = category_k
        category_v['icon_id'] = category_v['iconID'] if 'iconID' in category_v else 'null'

        if 'name' in category_v.keys():
            category_v['name'] = category_v['name']['ru']
        if not SQL_tools.check_entity_in_table('xxeve_logistic.db', 'categories', 'category_id', category_k):
            SQL_tools.wright_to_db('xxeve_logistic.db', 'categories', SQL_tools.preparing_values(category_v, config.categories_fields))

    groups = yaml.safe_load(open('../sde/sde/fsd/groupIDs.yaml', encoding='utf-8'))
    for group_k, group_v in groups.items():
        group_v['group_id'] = group_k
        group_v['category_id'] = group_v['categoryID']
        group_v['icon_id'] = group_v['iconID'] if 'iconID' in group_v else 'null'

        if 'name' in group_v.keys():
            group_v['name'] = group_v['name']['ru']
        if not SQL_tools.check_entity_in_table('xxeve_logistic.db', 'groups', 'group_id', group_k):
            SQL_tools.wright_to_db('xxeve_logistic.db', 'groups', SQL_tools.preparing_values(group_v, config.groups_fields))

    market_groups = yaml.safe_load(open('../sde/sde/fsd/marketGroups.yaml', encoding='utf-8'))
    for market_group_k, market_group_v in market_groups.items():
        market_group_v['market_group_id'] = market_group_k
        market_group_v['icon_id'] = market_group_v['iconID'] if 'iconID' in market_group_v else 'null'
        market_group_v['parent_group_id'] = market_group_v['parentGroupID'] if 'parentGroupID' in market_group_v else 'null'

        if 'nameID' in market_group_v.keys():
            market_group_v['name'] = market_group_v['nameID']['ru'] if 'ru' in market_group_v['nameID'] else market_group_v['nameID']['en']
        if 'descriptionID' in market_group_v.keys():
            market_group_v['description'] = market_group_v['descriptionID']['ru'] if 'ru' in market_group_v['descriptionID'] else market_group_v['descriptionID']['en']

        if not SQL_tools.check_entity_in_table('xxeve_logistic.db', 'market_groups', 'market_group_id', market_group_k):
            SQL_tools.wright_to_db('xxeve_logistic.db', 'market_groups', SQL_tools.preparing_values(market_group_v, config.market_groups_fields))

    types = yaml.safe_load(open('../sde/sde/fsd/typeIDs.yaml', encoding='utf-8'))
    for type_k, type_v in types.items():

        type_v['type_id'] = type_k
        type_v['race_id'] = type_v['raceID'] if 'raceID' in type_v else 'null'
        type_v['group_id'] = type_v['groupID'] if 'groupID' in type_v else 'null'
        type_v['variation_parent_type_id'] = type_v['variationParentTypeID'] if 'variationParentTypeID' in type_v else 'null'
        type_v['meta_group_id'] = type_v['metaGroupID'] if 'metaGroupID' in type_v else 'null'
        type_v['base_price'] = type_v['basePrice'] if 'basePrice' in type_v else 'null'
        type_v['sof_faction_name'] = type_v['sofFactionName'] if 'sofFactionName' in type_v else 'null'
        type_v['graphic_id'] = type_v['graphicID'] if 'graphicID' in type_v else 'null'
        type_v['icon_id'] = type_v['iconID'] if 'iconID' in type_v else 'null'
        type_v['sound_id'] = type_v['soundID'] if 'soundID' in type_v else 'null'
        type_v['faction_id'] = type_v['factionID'] if 'factionID' in type_v else 'null'
        type_v['market_group_id'] = type_v['marketGroupID'] if 'marketGroupID' in type_v else 'null'
        type_v['portion_size'] = type_v['portionSize'] if 'portionSize' in type_v else 'null'
        type_v['sof_material_set_id'] = type_v['sofMaterialSetID'] if 'sofMaterialSetID' in type_v else 'null'

        if 'name' in type_v.keys():
            type_v['name'] = type_v['name']['ru'] if 'ru' in type_v['name'] else type_v['name']['en']
        if 'description' in type_v.keys():
            type_v['description'] = type_v['description']['ru'] if 'ru' in type_v['description'] else type_v['description']['en']

        if not SQL_tools.check_entity_in_table('xxeve_logistic.db', 'types', 'type_id', type_k):
            SQL_tools.wright_to_db('xxeve_logistic.db', 'types', SQL_tools.preparing_values(type_v, config.types_fields))

    url = '../sde/sde/fsd/universe/eve/'
    for region in os.listdir(url):
        if 'staticdata' in region:
            continue
        print("region:", region)
        for constellation in os.listdir(url + region + '/'):
            if 'staticdata' in constellation:
                continue
            print("region:", region, 'constellation:', constellation)
            for system in os.listdir(url + region + '/' + constellation + '/'):
                if 'staticdata' in system:
                    continue
                system_info = yaml.safe_load(
                    open(url + region + '/' + constellation + '/' + system + '/solarsystem.staticdata',
                         encoding='utf-8'))
                system_info['wormhole_class_id'] = system_info[
                    'wormholeClassID'] if 'wormholeClassID' in system_info else 'null'
                system_info['name'] = system
                system_info['sun_type_id'] = system_info['sunTypeID'] if 'sunTypeID' in system_info else 'null'
                system_info['stargates_number'] = len(system_info['stargates']) if 'stargates' in system_info else 0
                system_info['solar_system_name_id'] = system_info[
                    'solarSystemNameID'] if 'solarSystemNameID' in system_info else 'null'
                system_info['system_id'] = system_info[
                    'solarSystemID'] if 'solarSystemID' in system_info else 'null'
                system_info['security_class'] = system_info[
                    'securityClass'] if 'securityClass' in system_info else 'null'
                system_info['security_status'] = system_info['security'] if 'security' in system_info else 'null'
                system_info['planets_number'] = len(system_info['planets']) if 'planets' in system_info else 0
                system_info['position_x'] = system_info['center'][0] if 'center' in system_info else 'null'
                system_info['position_y'] = system_info['center'][1] if 'center' in system_info else 'null'
                system_info['position_z'] = system_info['center'][2] if 'center' in system_info else 'null'
                system_info['constellation_id'] = yaml.safe_load(
                    open(url + region + '/' + constellation + '/constellation.staticdata', encoding='utf-8'))[
                    'constellationID']

                if not SQL_tools.check_entity_in_table('xxeve_logistic.db', 'systems', 'system_id',
                                                       system_info['system_id']):
                    SQL_tools.wright_to_db('xxeve_logistic.db', 'systems',
                                           SQL_tools.preparing_values(system_info, config.systems_fields))


def load_stats(bg=False):
    for stat in SQL_tools.get_kills_and_jumps():
        row = SQL_tools.preparing_values(stat, config.snap_statistic_systems_fields)
        SQL_tools.wright_to_db('xxeve_logistic.db', 'snap_statistic_systems', row, bg)


def load_route_info(system_from: dict, system_to: dict):
    db_name = 'xxeve_logistic.db'
    route_list = SQL_tools.get_route(SQL_tools.select_entity(name_db=db_name,
                                                             name_table='systems',
                                                             entity_field=system_from['field'],
                                                             entity_value=f'"{system_from["value"]}"')['system_id'],
                                     SQL_tools.select_entity(name_db=db_name,
                                                             name_table='systems',
                                                             entity_field=system_to['field'],
                                                             entity_value=f'"{system_to["value"]}"')['system_id'])
    result = {}
    for i, system_id in enumerate(route_list):
        print(f'Всего в рейсе {system_from["value"]}-{system_to["value"]}: {len(route_list)} систем. Осталось {len(route_list) - i}')
        print(f'Проверяем {system_id} - {SQL_tools.select_entity(db_name, "systems", "system_id", system_id)["name"]}')
        result[system_id] = SQL_tools.get_zkb_mails(db_name, 'systems', system_id, all_mails=True)

    for killmails in result.values():
        if killmails is not None:
            for killmail in killmails.values():
                if len(SQL_tools.select_entity(db_name, 'characters', 'character_id', killmail['victim_character_id'], limit='one')) != 0:
                    print(SQL_tools.select_entity(db_name, 'characters', 'character_id', killmail['victim_character_id'], limit='one'))
                else:
                    SQL_tools.get_characters(killmail['victim_character_id'], wright=True)
                for attackers in killmail['attackers'].values():
                    if attackers['attacker_character_id'] != 'NULL':
                        if len(SQL_tools.select_entity(db_name, 'characters', 'character_id', attackers['attacker_character_id'], limit='one')) != 0:
                            print(SQL_tools.select_entity(db_name, 'characters', 'character_id', attackers['attacker_character_id'], limit='one'))
                        else:
                            SQL_tools.get_characters(attackers['attacker_character_id'], wright=True)
