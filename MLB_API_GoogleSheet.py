import os
import time
import statsapi
import pandas as pd
from datetime import datetime

# --- 1. 初始化設定 ---
tic = time.time()
now = datetime.now()
current_year = now.year
season_str = str(current_year)
# 格式化今天的日期
execution_date = now.strftime('%Y/%m/%d')

# 檔案路徑設定 (根目錄，改為 .csv)
id_file = f"mlbPlayerID_Y26.txt"
field_csv = f"mlbField_{season_str}.csv"
pitch_csv = f"mlbPitch_{season_str}.csv"
hit_csv = f"mlbHit_{season_str}.csv"

# 30 支球隊 ID
teamList = [108,109,110,111,112,113,114,115,116,117,118,119,120,121,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,158]
updateData = ['field', 'pitch', 'hit']
updatePlayerIDFlag = True
updateDataFlag = True

# --- 2. 輔助函式 ---

def getMlbPlayerID():
    """獲取目前所有球隊名單中的球員 ID"""
    mlbPlayerID = []
    unique_names = set()
    for team in teamList:
        try:
            roster = statsapi.roster(team)
            lines = roster.split('\n')
            for line in lines:
                if not line.strip(): continue
                parts = line.split()
                # 濾除背號與位置縮寫
                name = " ".join([p for p in parts if not p.isdigit() and p not in ['TWP', 'P', 'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'DH']])
                if name and name not in unique_names:
                    unique_names.add(name)
                    players = statsapi.lookup_player(name)
                    for p in players:
                        mlbPlayerID.append(p['id'])
        except:
            continue
    return list(set(mlbPlayerID))

def getMlbPlayerData(player_id, updateData):
    """抓取單一球員的各項統計數據"""
    field, pitch, hit = [], [], []
    try:
        player_data = statsapi.player_stat_data(player_id)
        if not player_data.get('stats'): return field, pitch, hit
        
        info = {
            'active': player_data.get('active'),
            'team': player_data.get('current_team'),
            'name': f"{player_data.get('first_name')} {player_data.get('last_name')}"
        }

        for s in player_data['stats']:
            stats = s['stats']
            group = s['group']
            
            if group == 'hitting' and 'hit' in updateData:
                hit.append([info['active'], info['team'], info['name'], stats.get('airOuts'), stats.get('atBats'), stats.get('atBatsPerHomeRun'), stats.get('avg'), stats.get('babip'), stats.get('baseOnBalls'), stats.get('catchersInterference'), stats.get('caughtStealing'), stats.get('doubles'), stats.get('gamesPlayed'), stats.get('groundIntoDoublePlay'), stats.get('groundOuts'), stats.get('groundOutsToAirouts'), stats.get('hitByPitch'), stats.get('hits'), stats.get('homeRuns'), stats.get('intentionalWalks'), stats.get('leftOnBase'), stats.get('numberOfPitches'), stats.get('obp'), stats.get('ops'), stats.get('plateAppearances'), stats.get('rbi'), stats.get('runs'), stats.get('sacBunts'), stats.get('sacFlies'), stats.get('slg'), stats.get('stolenBasePercentage'), stats.get('stolenBases'), stats.get('strikeOuts'), stats.get('totalBases'), stats.get('triples')])
            
            elif group == 'fielding' and 'field' in updateData:
                pos = stats.get('position', {})
                field.append([info['active'], info['team'], info['name'], pos.get('abbreviation'), pos.get('name'), stats.get('assists'), stats.get('chances'), stats.get('doublePlays'), stats.get('errors'), stats.get('fielding'), stats.get('games'), stats.get('gamesPlayed'), stats.get('gamesStarted'), stats.get('innings'), stats.get('putOuts'), stats.get('rangeFactorPer9Inn'), stats.get('rangeFactorPerGame'), stats.get('throwingErrors'), stats.get('triplePlays')])
            
            elif group == 'pitching' and 'pitch' in updateData:
                pitch.append([info['active'], info['team'], info['name'], stats.get('airOuts'), stats.get('atBats'), stats.get('avg'), stats.get('balks'), stats.get('baseOnBalls'), stats.get('battersFaced'), stats.get('blownSaves'), stats.get('catchersInterference'), stats.get('caughtStealing'), stats.get('completeGames'), stats.get('doubles'), stats.get('earnedRuns'), stats.get('era'), stats.get('gamesFinished'), stats.get('gamesPitched'), stats.get('gamesPlayed'), stats.get('gamesStarted'), stats.get('groundIntoDoublePlay'), stats.get('groundOuts'), stats.get('groundOutsToAirouts'), stats.get('hitBatsmen'), stats.get('hitByPitch'), stats.get('hits'), stats.get('hitsPer9Inn'), stats.get('holds'), stats.get('homeRuns'), stats.get('homeRunsPer9'), stats.get('inheritedRunners'), stats.get('inheritedRunnersScored'), stats.get('inningsPitched'), stats.get('intentionalWalks'), stats.get('losses'), stats.get('numberOfPitches'), stats.get('obp'), stats.get('ops'), stats.get('outs'), stats.get('pickoffs'), stats.get('pitchesPerInning'), stats.get('runs'), stats.get('runsScoredPer9'), stats.get('sacBunts'), stats.get('sacFlies'), stats.get('saveOpportunities'), stats.get('saves'), stats.get('shutouts'), stats.get('slg'), stats.get('stolenBasePercentage'), stats.get('stolenBases'), stats.get('strikeOuts'), stats.get('strikePercentage'), stats.get('strikeoutWalkRatio'), stats.get('strikes'), stats.get('totalBases'), stats.get('triples'), stats.get('walksPer9Inn'), stats.get('whip'), stats.get('wildPitches'), stats.get('winPercentage'), stats.get('wins')])
    except:
        pass
    return field, pitch, hit

# --- 3. 執行球員 ID 更新 ---
mlbPlayerID_hist = []
if os.path.exists(id_file):
    with open(id_file, 'r') as f:
        mlbPlayerID_hist = [int(i) for i in f.read().splitlines() if i]

if updatePlayerIDFlag:
    current_ids = getMlbPlayerID()
    final_list = list(set(current_ids) | set(mlbPlayerID_hist))
    if len(final_list) > len(mlbPlayerID_hist):
        print(f"🆕 發現新球員，更新 ID 列表...")
        with open(id_file, 'w') as f:
            for pid in final_list:
                f.write(f"{pid}\n")
    mlbPlayerID = final_list
else:
    mlbPlayerID = mlbPlayerID_hist

# --- 4. 抓取數據並轉為 DataFrame ---
all_field, all_pitch, all_hit = [], [], []

if updateDataFlag:
    print(f"🚀 開始抓取 {len(mlbPlayerID)} 位球員的數據...")
    for pid in mlbPlayerID:
        f, p, h = getMlbPlayerData(pid, updateData)
        all_field.extend(f)
        all_pitch.extend(p)
        all_hit.extend(h)

# 定義欄位名稱
cols_field = ['active','team','name','abb','position','assists','chances','doublePlays','errors','fielding','games','gamesPlayed','gamesStarted','innings','putOuts','rangeFactorPer9Inn','rangeFactorPerGame','throwingErrors','triplePlays']
cols_pitch = ['active','team','name','airOuts','atBats','avg','balks','baseOnBalls','battersFaced','blownSaves','catchersInterference','caughtStealing','completeGames','doubles','earnedRuns','era','gamesFinished','gamesPitched','gamesPlayed','gamesStarted','groundIntoDoublePlay','groundOuts','groundOutsToAirouts','hitBatsmen','hitByPitch','hits','hitsPer9Inn','holds','homeRuns','homeRunsPer9','inheritedRunners','inheritedRunnersScored','inningsPitched','intentionalWalks','losses','numberOfPitches','obp','ops','outs','pickoffs','pitchesPerInning','runs','runsScoredPer9','sacBunts','sacFlies','saveOpportunities','saves','shutouts','slg','stolenBasePercentage','stolenBases','strikeOuts','strikePercentage','strikeoutWalkRatio','strikes','totalBases','triples','walksPer9Inn','whip','wildPitches','winPercentage','wins']
cols_hit = ['active','team','name','airOuts','atBats','atBatsPerHomeRun','avg','babip','baseOnBalls','catchersInterference','caughtStealing','doubles','gamesPlayed','groundIntoDoublePlay','groundOuts','groundOutsToAirouts','hitByPitch','hits','homeRuns','intentionalWalks','leftOnBase','numberOfPitches','obp','ops','plateAppearances','rbi','runs','sacBunts','sacFlies','slg','stolenBasePercentage','stolenBases','strikeOuts','totalBases','triples']

df_field = pd.DataFrame(all_field, columns=cols_field)
df_pitch = pd.DataFrame(all_pitch, columns=cols_pitch)
df_hit = pd.DataFrame(all_hit, columns=cols_hit)

# 插入執行日期
df_field.insert(0, 'EXECUTION_DATE', execution_date)
df_pitch.insert(0, 'EXECUTION_DATE', execution_date)
df_hit.insert(0, 'EXECUTION_DATE', execution_date)

# --- 5. 儲存檔案 (CSV Append 模式) ---
files_to_save = [
    (df_field, field_csv),
    (df_pitch, pitch_csv),
    (df_hit, hit_csv)
]

for df, filename in files_to_save:
    if not df.empty:
        if not os.path.exists(filename):
            # 檔案不存在：寫入標題
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"🆕 建立新 CSV: {filename}")
        else:
            # 檔案已存在：附加數據，不寫標題
            df.to_csv(filename, mode='a', index=False, header=False, encoding='utf-8-sig')
            print(f"📝 附加數據至: {filename}")
    else:
        print(f"⚠️ 跳過空白數據。")

print(f"✅ 處理完成！耗時: {time.time() - tic:.2f}s")
