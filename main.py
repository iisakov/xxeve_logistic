import os.path
import sys

import connect_postgre
from datetime import datetime
from time import sleep


import requests

import config
import scripts

import SQL_tools


def main(arg):

    FLAG = True

    if '-r' not in arg:
        hubs_first = ['Jita', 'Perimeter', 'Amarr', 'Rens', 'Dodixie', 'Hek']
        hubs_empire = ['Oursulaert', 'Tash-Murkon Prime', 'Agil', 'Sakht', 'Tuomuta', 'Esescama', 'Dresi', 'Ordion',
                       'Zinkon', 'Berta', 'Motsu', 'Nourvukaiken', 'Sobaseki', 'Torrinos', 'Oursulaert',
                       'Arnon', 'Halle', 'Orvolle', 'Stacmon', 'Boystin', 'Sarline', 'Clellinon', 'Sortet',
                       'Apanake', 'Agil', 'Lustrevik', 'Pator', 'Teonusude']
        hubs_nullsec = ['XX9-WV', 'G-0Q86', '1-SMEB', 'BWF-ZZ', 'E02-IK', '4C-B7X', 'LGK-VP', 'TG-Z23', 'PC9-AY', 'VSIG-K',
                        'X-M2LR', 'N5Y-4N']

        extreme_points_list = []

        for i, hub in enumerate(hubs_first):
            for j, hub_to in enumerate(hubs_first):
                if i < j:
                    extreme_points_list.append([{'field': 'name', 'value': hub}, {'field': 'name', 'value': hub_to}])

        for hub in hubs_first:
            for hub_to in hubs_empire:
                if hub != hub_to:
                    extreme_points_list.append([{'field': 'name', 'value': hub}, {'field': 'name', 'value': hub_to}])

        for hub in hubs_first:
            for hub_to in hubs_nullsec:
                if hub != hub_to:
                    extreme_points_list.append([{'field': 'name', 'value': hub}, {'field': 'name', 'value': hub_to}])
    else:
        extreme_points_list = [[{'field': 'name', 'value': arg[arg.index('-r')+1]}, {'field': 'name', 'value': arg[arg.index('-r')+2]}]]

    while FLAG:
        FLAG = False if '-i' not in arg else True

        for extreme_points in extreme_points_list:
            SQL_tools.print_route_waypoints_name(extreme_points_list)
            system_from_dict = extreme_points[0]
            system_to_dict = extreme_points[1]

            scripts.load_info_in_table_script.load_route_info(system_from_dict, system_to_dict)

            if '-s' in arg:
                scripts.load_info_in_table_script.load_stats()

        name_tables_list = ['alliances', 'alliances_corporations', 'attackers', 'characters', 'corporations',
                            'entity_list', 'killmails', 'regions', 'snap_statistic_systems', 'systems', 'types',
                            'victims', 'categories', 'constellations', 'groups', 'market_groups']

        path_to_file_script = 'load_script.script'
        connect_postgre.drop_tables()
        for table_name in name_tables_list:
            path_to = 'table_info/csv/'
            path_to_file_table = f'{path_to}{table_name}.csv'

            if not os.path.isfile(path_to_file_script):
                file_script = open(path_to_file_script, 'w', encoding='utf-8')
                file_script.close()

            SQL_tools.table_to_cvs(table_name, SQL_tools.select_all_in_table('xxeve_logistic.db', table_name))
            if table_name != 'systems':
                if table_name == 'types':
                    scripts.refactor_info_script.refactor_mass_division_in_csv(path_to_file_table, table_name)
                if table_name == 'characters':
                    scripts.refactor_info_script.refactor_description_in_csv(path_to_file_table, table_name)
                scripts.refactor_info_script.refactor_create_timestamp_in_csv(path_to_file_table, table_name)
            else:
                os.rename(f'{path_to}{table_name}.csv', f'{path_to}{table_name}_prepared.csv')
                print(f'переименовали файл {table_name}.csv')
            SQL_tools.append_script_file(path_to_file_script, table_name, 'xxeve_logistic.db')
            print(f'Выбрали все записи из таблицы {table_name}, записали в csv')
        connect_postgre.reload_data()

        open(path_to_file_script, 'w', encoding='utf-8')
        SQL_tools.print_route_waypoints_name(extreme_points_list)


if __name__ == "__main__":
    main(sys.argv)
