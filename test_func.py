import SQL_tools

for snap in SQL_tools.get_kills_and_jumps():
    if snap['ship_kills'] > 0:
        print(snap)

