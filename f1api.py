import pandas as pd
import requests


flag = 0

year = 2022
round_list = range(1,17)
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
            df = pd.concat([df,new])

print(df)

# df_json = pd.read_json(url)
  
# Create empty dataframe
# df = pd.DataFrame(columns = ['Date', 'Views'])

# for index, row in df_json.iterrows():
#     df.at[index,'Date'] = row.loc['items']['timestamp']
#     df.at[index,'Views'] = row.loc['items']['views']

# df = df.dropna()
