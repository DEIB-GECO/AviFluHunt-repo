import pandas

excel = pandas.read_excel("mutationsToMarker_tomodifywithpython.xlsx",
                          keep_default_na=False, na_values=['_'])


file = []
for row in excel.values:
    row = tuple(row)
    for mutation in row[1].split(","):
        file.append([f'H5N1:{mutation}', row[0]])

df = pandas.DataFrame(file, columns=['mutation_id', 'marker_id'])
df.to_excel('mutations_to_group.xlsx')
