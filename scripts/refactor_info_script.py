import datetime

import pandas as pd


def refactor_data_time_in_csv(df_col, div=0):
    result = df_col.apply(lambda x: "".join(chr_ for chr_ in x if chr_.isdecimal()))

    def x(row):
        if len(row) < 14:
            row += "".join(['0']*(14-len(row)))
        row = datetime.datetime.strptime(row[:14], "%Y%m%d%H%M%S")
        row = datetime.datetime.strftime(row + datetime.timedelta(hours=div), "%Y-%m-%d %H:00:00")
        return row

    result = result.apply(x)
    return result


def refactor_mass_division_in_csv(path_to_fp, table_name):
    df = pd.read_csv(path_to_fp)
    if table_name == 'systems':
        df.set_index(df.columns[0]).to_csv(f'table_info/csv/{table_name}.csv')
    else:
        df.set_index(df.columns[0]).to_csv(f'table_info/csv/{table_name}_prepared.csv', float_format='%e')


def refactor_description_in_csv(path_to_fp, table_name):
    df = pd.read_csv(path_to_fp)
    # df['description'] = df['description'].fillna('нет описания')
    df['description'] = df['description'].apply(lambda x: 'нет описания')
    if table_name == 'systems':
        df.set_index(df.columns[0]).to_csv(f'table_info/csv/{table_name}.csv')
    else:
        df.set_index(df.columns[0]).to_csv(f'table_info/csv/{table_name}.csv', float_format='%.0f')


def refactor_create_timestamp_in_csv(path_to_fp, table_name):
    df = pd.read_csv(path_to_fp)
    df.create_date = refactor_data_time_in_csv(df.create_date)
    if 'killmail_time' in df.columns:
        df.killmail_time = refactor_data_time_in_csv(df.killmail_time, div=3)

    if table_name == 'systems':
        df.set_index(df.columns[0]).to_csv(f'table_info/csv/{table_name}.csv')
    else:
        df.set_index(df.columns[0]).to_csv(f'table_info/csv/{table_name}_prepared.csv', float_format='%.0f')
