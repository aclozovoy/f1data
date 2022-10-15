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

year = 2014
# round_list = range(1,17)
round_list = list(range(1,25))
# round_list.remove(9)
# round_list.remove(4)
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
        team_min = df_round_team['Qlast'].min()
        # if team_avg > 1.07*pole:
        #     team_avg = df_round_team['Qlast'].min()
        for index, row in df.iterrows():
            if row.loc['round'] == round:
                if row.loc['Constructor.name'] == team:
                    df.at[index,'Qteam_avg'] = team_avg
                    df.at[index,'Qteam_min'] = team_min


# DRIVER TIME OFF POLE
df['driver time off pole'] = (df['Qlast'] - df['pole']) / 1000
df['driver percentage off pole'] = (df['Qlast'] / df['pole'])

# TEAM AVG TIME OFF POLE
df['team avg time off pole'] = (df['Qteam_avg'] - df['pole']) / 1000
df['team avg percentage off pole'] = (df['Qteam_avg'] / df['pole'])

# TEAM AVG TIME OFF POLE
df['team min time off pole'] = (df['Qteam_min'] - df['pole']) / 1000
df['team min percentage off pole'] = (df['Qteam_min'] / df['pole'])

# REMOVE 'GRAND PRIX' FOR AXIS LABEL
df['country'] = df['racename'].str.replace(' Grand Prix','')


# IMPROVEMENT THROUGH SESSIONS
df['Q12delta'] = (df['Q2_ms'] - df['Q1_ms']) / 1000
df['Q23delta'] = (df['Q3_ms'] - df['Q2_ms']) / 1000
df_Q12delta = df.groupby(['Driver.code', 'Constructor.name'])['Q12delta'].agg('mean').reset_index()


# ASSIGN 107% TAG TO REMOVE OUTLIERS
# df['Under107'] = True
# df['driver percentage off pole clean'] = df['driver percentage off pole']
# for index, row in df.iterrows():
#     if row.loc['driver percentage off pole'] > 1.07:
#         df['Under107'] = False
#         df['driver percentage off pole clean'] = None


# df['driver percentage off pole'] = df['driver percentage off pole clean']


# STD DEV
df_agg = pd.DataFrame(columns=['std_dev', 'mean'])
df_agg['std_dev'] = df.groupby(['country'])['driver percentage off pole'].agg('std')
df_agg['mean'] = df.groupby(['country'])['driver percentage off pole'].agg('mean')
print(df_agg)

print(df)
# print(df_Q12delta)

team_colors = {'Red Bull':'#0600ef', 'Ferrari':'#dc0000', 'Alpine F1 Team':'#0090ff', 'Mercedes':'#00d2be', 'Alfa Romeo':'#900000', 'AlphaTauri':'#2b4562', 'Haas F1 Team':'#808080', 'McLaren':'#ff8700', 'Aston Martin':'#006f62', 'Williams':'#005aff','Renault':'#fff500','Racing Point':'#f596c8','Toro Rosso':'#469bff','Force India':'#ff80c7','Sauber':'#006eff','Caterham':'#005030', 'Lotus F1':'a28d00', 'Marussia':'#ed1b24'}

def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+.02, point['y'], str(point['val']))




plt.figure()
sns.set_style("dark")
sns.scatterplot(data=df, x="country", y="driver percentage off pole", hue="Constructor.name", palette=team_colors)
# sns.lineplot(data=df, x="country", y="team min percentage off pole", hue="Constructor.name", palette=team_colors, size = 0.5)

# label_point(df_agg, df.sepal_width, df_iris.species, plt.gca())
# for i in range(df.shape[0]):
    # plt.text(x=df.G[i]+0.3,y=df.GA[i]+0.3,s=df.Driver.code[i], fontdict=dict(color=’red’,size=10),bbox=dict(facecolor=’yellow’,alpha=0.5))
# plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.ylim(0.995,1.1)
plt.xticks(rotation=90)
plt.title(str(year)+' Formula 1 Qualifying Times')
plt.show()

plt.figure()
sns.scatterplot(data=df_agg, x="country", y="mean", color="b")
plt.show()

plt.figure()
sns.scatterplot(data=df_agg, x="country", y="std_dev", color="g")
plt.show()

# plt.figure()
# sns.barplot(data=df_Q12delta, x='Driver.code', y='Q12delta', hue="Constructor.name", palette=team_colors)#, width=0.8)
# plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
# plt.show()




