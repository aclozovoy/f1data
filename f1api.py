import pandas as pd
import requests

lapstring = str('1:32.187')
lapstring = str('null')

#TIME FUNCTION
def time_convert(lapstring):
    try:
        # MS
        ms = int(lapstring[-3:])

        # SEC
        s = lapstring.split(':')[1]
        sec = int(s[0:2])

        # MIN
        min = int(lapstring.split(':')[0])

        time = 60000 * min + 1000 * sec + ms

    except:
        time = None

    return time


flag = 0

year = 2022
round_list = range(1,17)
round_list = range(1,2)
driver_list = range(20)


# LOOP OVER ROUNDS (RACES)
for round in round_list:

    # BUILD API URL
    base = 'http://ergast.com/api/f1'
    year_str = '/' + str(year)
    round_str = '/' + str(round)
    session = '/qualifying'
    json = '.json'
    url = base + year_str + round_str + session + json
    print(url)

    # API CALL
    resp = requests.get(url=url)
    data = resp.json()

    for cur_driver in driver_list:
        print(round,'   ',cur_driver)
        sub_data = (data['MRData']['RaceTable']['Races'][0]['QualifyingResults'][cur_driver])
        new = pd.json_normalize(sub_data)

        new['year'] = year
        new['round'] = round

        # CREATE DF ON FIRST ITERATION. CONCAT ON FOLLOWING ITERATIONS.
        if flag == 0:
            df = new
            flag = 1
        else:
            df = pd.concat([df,new], ignore_index=True)

print(df.dtypes)

print (df.applymap(type))


df['Q1_ms'] = df['Q1'].apply(time_convert)
df['Q2_ms'] = df['Q2'].apply(time_convert)
df['Q3_ms'] = df['Q3'].apply(time_convert)

print('LOOP STARTS HERE______________________________')

for index, row in df.iterrows():
    if row.loc['Q3_ms'] == row.loc['Q3_ms']:
        df.at[index,'Qlast'] = row.loc['Q3_ms']
    elif row.loc['Q2_ms'] == row.loc['Q2_ms']:
        df.at[index,'Qlast'] = row.loc['Q2_ms']
    else:
        df.at[index,'Qlast'] = row.loc['Q1_ms']


print(df)


team_colors = {'Team': ['Red Bull', 'Ferrari', 'Alpine F1 Team', 'Mercedes', 'Alfa Romeo', 'AlphaTauri', 'Haas F1 Team', 'McLaren', 'Aston Martin', 'Williams','Renault','Racing Point','Toro Rosso','Force India','Sauber'],
        'Color': ['#0600ef','#dc0000','#0090ff','#00d2be','#900000','#2b4562','#808080','#ff8700','#006f62','#005aff','#fff500','#f596c8','#469bff','#ff80c7','#006eff']
        }
color_df = pd.DataFrame(team_colors)


