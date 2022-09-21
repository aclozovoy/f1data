import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns


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

year = 2021
# round_list = range(1,17)
round_list = range(1,25)
# round_list = range(1,4)
driver_list = range(20)


# LOOP OVER ROUNDS (RACES)
for round in round_list:

    try:
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
            # print(round,'   ',cur_driver)
            sub_data = (data['MRData']['RaceTable']['Races'][0]['QualifyingResults'][cur_driver])
            new = pd.json_normalize(sub_data)

            new['year'] = year
            new['round'] = round
            new['racename'] = data['MRData']['RaceTable']['Races'][0]['raceName']

            # CREATE DF ON FIRST ITERATION. CONCAT ON FOLLOWING ITERATIONS.
            if flag == 0:
                df = new
                flag = 1
            else:
                df = pd.concat([df,new], ignore_index=True)
    except:
        print('There is no round '+str(round)+'.')

# CONVERT STRING TIME TO FLOAT
df['Q1_ms'] = df['Q1'].apply(time_convert)
df['Q2_ms'] = df['Q2'].apply(time_convert)
df['Q3_ms'] = df['Q3'].apply(time_convert)

# FIND TIME FROM LAST ROUND FOR EACH DRIVER
for index, row in df.iterrows():
    if row.loc['Q3_ms'] == row.loc['Q3_ms']:
        df.at[index,'Qlast'] = row.loc['Q3_ms']
    elif row.loc['Q2_ms'] == row.loc['Q2_ms']:
        df.at[index,'Qlast'] = row.loc['Q2_ms']
    else:
        df.at[index,'Qlast'] = row.loc['Q1_ms']


# LOOP OVER ROUNDS (RACES) TO FIND POLE TIMES AND TEAM AVERAGES
teams = df['Constructor.name'].unique()

for round in round_list:
    # POLE TIMES
    df_round = df[df['round'] == round]
    pole = df_round['Qlast'].min()
    for index, row in df.iterrows():
        if row.loc['round'] == round:
            df.at[index,'pole'] = pole

    # FIND TEAM AVERAGE
    for team in teams:
        df_round_team = df_round[df_round['Constructor.name'] == team]
        team_avg = df_round_team['Qlast'].mean()
        # if team_avg > 1.07*pole:
        #     team_avg = df_round_team['Qlast'].min()
        for index, row in df.iterrows():
            if row.loc['round'] == round:
                if row.loc['Constructor.name'] == team:
                    df.at[index,'Qteam'] = team_avg



# DRIVER TIME OFF POLE
df['driver time off pole'] = (df['Qlast'] - df['pole']) / 1000
df['driver percentage off pole'] = (df['Qlast'] / df['pole'])

# TEAM TIME OFF POLE
df['team avg time off pole'] = (df['Qteam'] - df['pole']) / 1000
df['team avg percentage off pole'] = (df['Qteam'] / df['pole'])


# REMOVE 'GRAND PRIX' FOR AXIS LABEL
df['country'] = df['racename'].str.replace(' Grand Prix','')


print(df)


team_colors = {'Red Bull':'#0600ef', 'Ferrari':'#dc0000', 'Alpine F1 Team':'#0090ff', 'Mercedes':'#00d2be', 'Alfa Romeo':'#900000', 'AlphaTauri':'#2b4562', 'Haas F1 Team':'#808080', 'McLaren':'#ff8700', 'Aston Martin':'#006f62', 'Williams':'#005aff','Renault':'#fff500','Racing Point':'#f596c8','Toro Rosso':'#469bff','Force India':'#ff80c7','Sauber':'#006eff','Caterham':'#005030', 'Lotus F1':'a28d00', 'Marussia':'#ed1b24'}

sns.set_style("dark")
sns.scatterplot(data=df, x="country", y="driver percentage off pole", hue="Constructor.name", palette=team_colors)
sns.lineplot(data=df, x="country", y="team avg percentage off pole", hue="Constructor.name", palette=team_colors, size = 0.5)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.ylim(0.995,1.1)
plt.xticks(rotation=90)
plt.title(str(year)+' Formula 1 Qualifying Times')
plt.show()




