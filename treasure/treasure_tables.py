import yaml

def load_item_tables():
    item_tables = {}
    with open('data/item_tables.yaml') as f:
        tables = yaml.load(f.read())
    for key, value in tables.items():
        item_tables[key] = {}
        item_tables[key]['items'] = [[x for x in i.values()][0] for i in value]
        item_tables[key]['chance'] = [[x for x in i.keys()][0] for i in value]
    return item_tables

def load_treasure_tables():
    treasure_tables = {}
    object_column_names = ['chance', 'object_die_n', 'object_die_sides', 'object_value', 'object_type', 'item_die_sides', 'item_table_name']
    coin_column_names = ['name', 'die_n', 'die_sides', 'multiplier']
    with open('data/treasure_tables.yaml') as f:
        tables = yaml.load(f.read())
    for key, values in tables.items():
        treasure_tables[key] = {'objects':[], 'coins':[]}
        for row in values['objects']:
            row = row.split(',')
            treasure_tables[key]['objects'].append({name: value for name, value in zip(object_column_names, row)})
        for row in values['coins']:
            row = row.split(',')
            treasure_tables[key]['coins'].append({name: value for name, value in zip(coin_column_names, row)})
    return treasure_tables

def load_individual_tables():
    individual_tables = {}
    coin_column_names = ['name', 'die_n', 'die_sides', 'multiplier']
    with open('data/coins.yaml') as f:
        tables = yaml.load(f.read())
    for level, table in tables.items():
        individual_tables[level] = {}
        for roll, coins in table.items():
            individual_tables[level][roll] = []
            for row in coins:
                row = row.split(',')
                individual_tables[level][roll].append({name: value for name, value in zip(coin_column_names, row)})
    return individual_tables

def load_npc_items():
    with open('data/npc_items.yaml') as f:
        npc_items = yaml.load(f.read())
    return npc_items


    
npc_items = load_npc_items()
item_tables = load_item_tables()
treasure_tables = load_treasure_tables()
individual_tables = load_individual_tables()