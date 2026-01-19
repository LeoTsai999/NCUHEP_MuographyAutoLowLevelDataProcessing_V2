import numpy as np
import pandas as pd
import uproot
import sys
from array import array
import time
from tqdm import trange, tqdm
import datetime
from numba import njit, prange
import awkward as ak 

@njit
def FromPwidth_to_Voltage(pwidth):
    A, n = 17.00001535417237, 15.383171736562412 # 僅適用於閾值65mV
    
    voltage = (np.exp(pwidth/A) / n) * 1000  # 單位轉換成 mV

    return voltage

def TempDataPreProcessing(file_name):
    new_file_name = file_name.removesuffix("_Mu")

    df = pd.read_csv(f'/data9/YangMingShanExperiments/YangMingHotspotResort/RawData/HK/{new_file_name}_HK.txt', sep='\t')
    # 抓出大板上的4個溫度感測器資料
    tmp100_temp0 = df.iloc[:, 9].to_numpy()
    tmp100_temp1 = df.iloc[:, 10].to_numpy()
    tmp100_temp2 = df.iloc[:, 11].to_numpy()
    tmp100_temp3 = df.iloc[:, 12].to_numpy()
    PCNT = df.iloc[:, 3].to_numpy()
    BoardID = df.iloc[:, 1].to_numpy()


    tmp100_avg = (tmp100_temp0 + tmp100_temp1 + tmp100_temp2 + tmp100_temp3) / 4.0


    for i in range(len(PCNT)-1):     
        if PCNT[i] > PCNT[i+1] and PCNT[i] - PCNT[i+1] >= 2**15:             # 如果事件i的PCNT比事件i+1的PCNT大，且兩者的差異大於2**19，表示PCNT溢位重置了
            PCNT[i+1] = PCNT[i]                                              # 則把事件i+1的PCNT修正成跟事件i一樣
            print(f'在{PCNT[i]}有發生PCNT溢位重置的情況!!!!!!!!!!')
        elif PCNT[i] > PCNT[i+1] and PCNT[i] - PCNT[i+1] < 2**15:
            PCNT[i+1] = PCNT[i] + 1                                          # 否則就是PCNT不知道為什麼沒加到，故+1補回來

    temp_data = {'BoardID': BoardID.astype(int), 'PCNT': PCNT.astype(int), 'Temp': tmp100_avg}
    return temp_data



def GetTempAtThisPCNTandThisBoard(temp_data, pcnt_keys,  PCNT_target, BoardID):

    idx = np.searchsorted(pcnt_keys, PCNT_target, side='right') - 1 # 找到小於等於 PCNT_target 的最大 pcnt_keys 索引值

    mask = (temp_data['BoardID'] == BoardID) & (temp_data['PCNT'] == pcnt_keys[idx])

    temp_values = temp_data['Temp'][mask]
    
    temp = np.average(temp_values) if len(temp_values) > 0 else 999 # 把999當成無效值

    return temp

    

def GiveGlobalID():
    """計算每個 Hit 的 GlobalID"""
    BoardIDs = sorted_hits['BoardID']
    ChannelIDs = sorted_hits['ChannelID']
    GlobalIDs = (BoardIDs - 1) * 16 + ChannelIDs

    sorted_hits['GlobalID'] = GlobalIDs


def GiveEasyAndPhysCoordX():
    """計算每個 Hit 的 EasyCoord"""
    BoardIDs = sorted_hits['BoardID']
    ChannelIDs = sorted_hits['ChannelID']

    # 建立全為 None 的陣列  
    EasyCoordX = np.full(len(BoardIDs),255, dtype=np.uint8)
    PhysCoordX = np.full(len(BoardIDs),255, dtype=np.float32)
    # BoardID 為 1, 5, 9, 13
    mask1 = np.isin(BoardIDs, [1, 5, 9, 13])
    mask_x_is_5 = (ChannelIDs % 4 == 3)
    mask_x_is_6 = (ChannelIDs % 4 == 2)
    mask_x_is_7 = (ChannelIDs % 4 == 1)
    mask_x_is_8 = (ChannelIDs % 4 == 0)

    EasyCoordX[mask1 & mask_x_is_5] = 5
    EasyCoordX[mask1 & mask_x_is_6] = 6
    EasyCoordX[mask1 & mask_x_is_7] = 7
    EasyCoordX[mask1 & mask_x_is_8] = 8

    PhysCoordX[mask1 & mask_x_is_5] = 223.15
    PhysCoordX[mask1 & mask_x_is_6] = 272.75
    PhysCoordX[mask1 & mask_x_is_7] = 322.35
    PhysCoordX[mask1 & mask_x_is_8] = 371.95
    
    del mask_x_is_5, mask_x_is_6, mask_x_is_7, mask_x_is_8

    # BoardID 為 2, 6, 10, 14
    mask2 = np.isin(BoardIDs, [2, 6, 10, 14])
    mask_x_is_1 = (ChannelIDs % 4 == 0)
    mask_x_is_2 = (ChannelIDs % 4 == 1)
    mask_x_is_3 = (ChannelIDs % 4 == 2)
    mask_x_is_4 = (ChannelIDs % 4 == 3)

    EasyCoordX[mask2 & mask_x_is_1] = 1
    EasyCoordX[mask2 & mask_x_is_2] = 2
    EasyCoordX[mask2 & mask_x_is_3] = 3
    EasyCoordX[mask2 & mask_x_is_4] = 4

    PhysCoordX[mask2 & mask_x_is_1] = 24.75
    PhysCoordX[mask2 & mask_x_is_2] = 74.35
    PhysCoordX[mask2 & mask_x_is_3] = 123.95
    PhysCoordX[mask2 & mask_x_is_4] = 173.55

    del mask_x_is_1, mask_x_is_2, mask_x_is_3, mask_x_is_4

    # BoardID 為 3, 7, 11, 15
    mask3 = np.isin(BoardIDs, [3, 7, 11, 15])
    mask_x_is_5 = (ChannelIDs % 4 == 0)
    mask_x_is_6 = (ChannelIDs % 4 == 1)
    mask_x_is_7 = (ChannelIDs % 4 == 2)
    mask_x_is_8 = (ChannelIDs % 4 == 3)

    EasyCoordX[mask3 & mask_x_is_5] = 5
    EasyCoordX[mask3 & mask_x_is_6] = 6
    EasyCoordX[mask3 & mask_x_is_7] = 7
    EasyCoordX[mask3 & mask_x_is_8] = 8

    PhysCoordX[mask3 & mask_x_is_5] = 223.15
    PhysCoordX[mask3 & mask_x_is_6] = 272.75
    PhysCoordX[mask3 & mask_x_is_7] = 322.35
    PhysCoordX[mask3 & mask_x_is_8] = 371.95

    del mask_x_is_5, mask_x_is_6, mask_x_is_7, mask_x_is_8

    # BoardID 為 4, 8, 12, 16
    mask4 = np.isin(BoardIDs, [4, 8, 12, 16])
    mask_x_is_1 = (ChannelIDs % 4 == 3)
    mask_x_is_2 = (ChannelIDs % 4 == 2)
    mask_x_is_3 = (ChannelIDs % 4 == 1)
    mask_x_is_4 = (ChannelIDs % 4 == 0)

    EasyCoordX[mask4 & mask_x_is_1] = 1
    EasyCoordX[mask4 & mask_x_is_2] = 2
    EasyCoordX[mask4 & mask_x_is_3] = 3
    EasyCoordX[mask4 & mask_x_is_4] = 4

    PhysCoordX[mask4 & mask_x_is_1] = 24.75
    PhysCoordX[mask4 & mask_x_is_2] = 74.35
    PhysCoordX[mask4 & mask_x_is_3] = 123.95
    PhysCoordX[mask4 & mask_x_is_4] = 173.55

    del mask_x_is_1, mask_x_is_2, mask_x_is_3, mask_x_is_4
    
    sorted_hits['EasyCoordX'] = EasyCoordX
    sorted_hits['PhysCoordX'] = PhysCoordX

   

def GiveEasyAndPhysCoordY():
    """計算每個 Hit 的 EasyCoordY"""
    BoardIDs = sorted_hits['BoardID']
    ChannelIDs = sorted_hits['ChannelID']

    
    EasyCoordY = np.full(len(BoardIDs), 255, dtype=np.uint8)
    PhysCoordY = np.full(len(BoardIDs), 255, dtype=np.float32)
    # BoardID 為 1,2,5,6,9,10,13,14
    mask1 = np.isin(BoardIDs, [1, 2, 5, 6, 9, 10, 13, 14])
    mask_y_is_8 = (ChannelIDs // 4 == 0)
    mask_y_is_7 = (ChannelIDs // 4 == 1)
    mask_y_is_6 = (ChannelIDs // 4 == 2)
    mask_y_is_5 = (ChannelIDs // 4 == 3)

    EasyCoordY[mask1 & mask_y_is_8] = 8
    EasyCoordY[mask1 & mask_y_is_7] = 7
    EasyCoordY[mask1 & mask_y_is_6] = 6
    EasyCoordY[mask1 & mask_y_is_5] = 5 

    PhysCoordY[mask1 & mask_y_is_8] = 371.95
    PhysCoordY[mask1 & mask_y_is_7] = 322.35
    PhysCoordY[mask1 & mask_y_is_6] = 272.75
    PhysCoordY[mask1 & mask_y_is_5] = 223.15

    # BoardID 為 3,4,7,8,11,12,15,16
    mask2 = np.isin(BoardIDs, [3, 4, 7, 8, 11, 12, 15, 16])
    mask_y_is_1 = (ChannelIDs // 4 == 3)
    mask_y_is_2 = (ChannelIDs // 4 == 2)
    mask_y_is_3 = (ChannelIDs // 4 == 1)
    mask_y_is_4 = (ChannelIDs // 4 == 0)

    EasyCoordY[mask2 & mask_y_is_1] = 1
    EasyCoordY[mask2 & mask_y_is_2] = 2
    EasyCoordY[mask2 & mask_y_is_3] = 3
    EasyCoordY[mask2 & mask_y_is_4] = 4 

    PhysCoordY[mask2 & mask_y_is_1] = 24.75
    PhysCoordY[mask2 & mask_y_is_2] = 74.35
    PhysCoordY[mask2 & mask_y_is_3] = 123.95
    PhysCoordY[mask2 & mask_y_is_4] = 173.55

    sorted_hits['EasyCoordY'] = EasyCoordY
    sorted_hits['PhysCoordY'] = PhysCoordY


def GiveEasyAndPhysCoordZ():
    """計算每個 Hit 的 EasyCoordZ"""
    BoardIDs = sorted_hits['BoardID']

    # 初始化陣列 (全為 None)
    EasyCoordZ = np.full(len(BoardIDs), 255, dtype=np.uint8)
    PhysCoordZ = np.full(len(BoardIDs), 255, dtype=np.float32)

    # Board 1,2,3,4 -> Z = 1
    mask1 = np.isin(BoardIDs, [1, 2, 3, 4])
    EasyCoordZ[mask1] = 1
    PhysCoordZ[mask1] = 0

    # Board 5,6,7,8 -> Z = 2
    mask2 = np.isin(BoardIDs, [5, 6, 7, 8])
    EasyCoordZ[mask2] = 2
    PhysCoordZ[mask2] = 500

    # Board 9,10,11,12 -> Z = 3
    mask3 = np.isin(BoardIDs, [9, 10, 11, 12])
    EasyCoordZ[mask3] = 3
    PhysCoordZ[mask3] = 1000

    # Board 13,14,15,16 -> Z = 4
    mask4 = np.isin(BoardIDs, [13, 14, 15, 16])
    EasyCoordZ[mask4] = 4
    PhysCoordZ[mask4] = 1500

    sorted_hits['EasyCoordZ'] = EasyCoordZ
    sorted_hits['PhysCoordZ'] = PhysCoordZ

"""
輸入參數
"""
path = '/data9/YangMingShanExperiments/YangMingHotspotResort/RawData/'                       # 數據絕對路徑
output_path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/'  # 處理後數據輸出絕對路徑

file_name = sys.argv[1]  # 讀取第一個參數(數據檔名)

# 顏色代碼
RED = "\033[31m"  # 紅色
GREEN = "\033[32m"  # 綠色
BLUE = "\033[34m"  # 藍色
RESET = "\033[0m"  # 重置顏色


"""

主程式開始，讀取資料

"""

events = [] # 用來儲存每個event的hits資訊。每個元素為一字典，包含一個event的所有hits資訊。
print(f'\n{RED}Processing file: {file_name}{RESET}')

print('\nReading data')
with open(path + file_name+'.txt', 'r') as f:
    lines = f.readlines()
print('\nComplete reading data, start slicing.')
lines = lines[1:int(len(lines))]
print('\nComplete slicing data')
"""

Remove # Fram .......... contents. After the remove, an np array will be saved to do analysis.

"""
hits = []
boardID = []
channelID = []
PCNT = []
TCNT = []
PWidth = []
strange_pwidth = []

for i in range(len(lines)):         # 逐行讀取資料。只有板號介於正常範圍（1~16）而且pwidth正常（小於100）的事件才會被記錄並作後續分析。不屬於正常範圍者，放入strange_pwidth紀錄。
    line = lines[i]
    if "#Frame" not in line:
        data = line.split()
        if 16 >= int(data[1]) >= 1 and int(data[7])<=100:
            boardID.append(data[1])
            channelID.append(data[2])
            PCNT.append(data[5])
            TCNT.append(data[6])
            PWidth.append(data[7])
        else:
            strange_pwidth.append([data[1], data[2], data[7]])

if len(strange_pwidth) != 0:
    print('Strange Signal: ')           # 把奇怪的hit打印出來
    for k in range(len(strange_pwidth)):
        print(strange_pwidth[k])
    print(f'共有 {len(strange_pwidth)} 個異常hit')

# 建立陣列儲存資料。資料型態分別以8或32位元儲存以節省空間。
boardID = np.array(boardID, dtype=np.uint8)
channelID = np.array(channelID, dtype=np.uint8)
PCNT = np.array(PCNT, dtype=np.uint64)
TCNT = np.array(TCNT, dtype=np.uint32)
PWidth = np.array(PWidth, dtype=np.uint8)

# 將前五行建立的陣列建立為字典已儲存資料。
hits = {'BoardID': boardID, 'ChannelID': channelID, 'PCNT': PCNT, 'TCNT': TCNT, 'PWidth': PWidth}

print('\nRemove # Fram: Complete remove # Frame......')
hits['BoardID']

"""
從pwidth轉換成voltage
"""
Amplitude = FromPwidth_to_Voltage(hits['PWidth'])
hits['Amplitude'] = Amplitude
"""

PCNT calibration

"""
for i in range(len(hits)-1):
    if hits['PCNT'][i] > hits['PCNT'][i+1] and hits['PCNT'][i] - hits['PCNT'][i+1] >= 2**15:   # 如果事件i的PCNT比事件i+1的PCNT大，且兩者的差異大於2**19，表示PCNT溢位重置了
        hits['PCNT'][i+1] = hits['PCNT'][i]                                                    # 則把事件i+1的PCNT修正成跟事件i一樣
        print(f'在{hits["PCNT"][i]}有發生PCNT溢位重置的情況!!!!!!!!!!')

    elif hits['PCNT'][i] > hits['PCNT'][i+1] and hits['PCNT'][i] - hits['PCNT'][i+1] < 2**15:
        hits['PCNT'][i+1] = hits['PCNT'][i] + 1                                                # 否則就是PCNT不知道為什麼沒加到，故+1補回來

print('\nhits complete PCNT calibration now. ')
print(f'After PCNT calibration: len(hits[PCNT]) = {len(hits["PCNT"])}')

"""

timestamp calibration

"""
timestamp = np.zeros_like(hits['PCNT'], dtype=np.uint64)          # 建立時間戳記，其由PCNT向左平移32位元後和TCNT組合而成
for i in range(len(hits['PCNT'])):
    timestamp[i] = (hits['PCNT'][i] << 32) + hits['TCNT'][i]    

hits['TimeStamp'] = timestamp                                     # 將時間戳記加入hits字典。

totlal_time_for_this_run = (np.max(hits['PCNT']) - np.min(hits['PCNT'])) # unit of PCNT is sec
print(f'\nTotal time for this run(By PCNT): {totlal_time_for_this_run/3600:.2f} hr')

print('\ntimestamp calibration : Finished')

sort_index = np.argsort(hits['TimeStamp'])                       
                                                                

hits = {key: hits[key][sort_index] for key in hits.keys()}        # 對於每一個key，將hits[key]按照sort_index排序。換言之，每一事件的所有資料都被按照時間順序重新排序。
print('\nsort by new timestamp: Finished')

"""
Event Determination: A event must less than 150 TCNT
"""
events_ID_list = []                                                       # 建立空陣列，用來儲存每個hit的event ID。

event_ID = np.uint32(0)                                                   # 定義第一個event的id為0。
first_hit_time_in_a_event= hits['TimeStamp'][0]                           # 抓出第一個hit的時間。第一個hit必定是第一個event的第一個hit。（也就是抓出Event 0 開始的時間）

for i in range(len(hits['TimeStamp'])):                                   # 每一個hit都會有兩種情況：
    if hits['TimeStamp'][i] - first_hit_time_in_a_event < 150:             # 情況1: 這個hit和前一個hit的時間差小於150個TCNT --> 那就屬於同一個Event
        events_ID_list.append(np.uint32(event_ID))                              # 因為是同一個Event，所以ID不用增加就直接給這個hit

    else:                                                                 # 情況2: 這個hit和前一個hit的時間差大於150個TCNT，表示這個hit是一個新的event的第一個hit --> 那就屬於一個新的Event
        event_ID += 1                                                     # 因此要把event_ID增加1。然後再給這個hit
        events_ID_list.append(np.uint32(event_ID))                                   
        first_hit_time_in_a_event = hits['TimeStamp'][i]                  # 並且把這個“Event開頭的hit”的時間給記錄下來，在for迴圈中繼續迭代

hits['EventID'] = np.array(events_ID_list)

# hits = {'BoardID': boardID, 'ChannelID': channelID, 'PCNT': PCNT, 'TCNT': TCNT, 'PWidth': PWidth, 'TimeStamp': timestamp, 'EventID': events_ID_list}

print('\nSucessfully add event ID to data')

"""

Add layer ID to hits, according to the board ID.

"""

hits['LayerID'] = np.zeros_like((hits['BoardID']), dtype=np.uint8)      # 建立一個陣列，用來儲存每個hit的layer ID。np.uint8的範圍是0~255。
for i in range(len(hits['LayerID'])):                                  # 利用迴圈遍歷每一個hit，並依據hit到哪一張板子，將hit的layer ID設定為1~4。其中layer4是頭，layer1是尾。
    if hits['BoardID'][i] <= 4:
        hits['LayerID'][i] = 1

    elif hits['BoardID'][i] <= 8:
        hits['LayerID'][i] = 2

    elif hits['BoardID'][i] <= 12:
        hits['LayerID'][i] = 3

    elif hits['BoardID'][i] <= 16:
        hits['LayerID'][i] = 4

    else:
        print('add layer ID fialed')
        print('hits[BoardID][i]: ', hits['BoardID'][i])
        quit()

print(f'length of hits[LayerID]: {len(hits["LayerID"])}')
print('\nSucessfully add layer ID to hits')

'''

增加溫度資料

'''
temp_data = TempDataPreProcessing(file_name)                     # 讀取溫度資料並進行前處理


df_temp = pd.DataFrame(temp_data)

df_temp = df_temp.groupby(['BoardID', 'PCNT'])['Temp'].mean().reset_index()

df_temp = df_temp.sort_values('PCNT')


df_hits = pd.DataFrame(hits)


df_hits['BoardID'] = df_hits['BoardID'].astype(int)
df_hits['PCNT'] = df_hits['PCNT'].astype(int)

df_hits['original_index'] = df_hits.index 

df_hits = df_hits.sort_values('PCNT')

df_merged = pd.merge_asof(
    df_hits, 
    df_temp, 
    on='PCNT', 
    by='BoardID', 
    direction='backward'
)

missing_mask = df_merged['Temp'].isna()
missing_rows = df_merged[missing_mask]

# if not missing_rows.empty:
#     print(f'\n{RED}有 {len(missing_rows)} 筆 Hits 找不到對應的溫度資料！{RESET}')
    
#     # # 前十筆
#     # print(missing_rows[['BoardID', 'PCNT', 'TimeStamp']].head(10).to_string(index=False))
    
    
#     # print('\n--- 各板子統計 ---')
#     # print(missing_rows['BoardID'].value_counts().to_string())
    
#     # 缺失 PCNT 範圍
#     print(f'\n缺失PCNT 範圍: {missing_rows["PCNT"].min()} ~ {missing_rows["PCNT"].max()}')
#     print(f'溫度資料 PCNT 範圍: {df_temp["PCNT"].min()} ~ {df_temp["PCNT"].max()}')
    
df_merged = df_merged.sort_values('original_index')

temp_list = df_merged['Temp'].fillna(999).to_numpy(dtype=np.float32)

hits['Temperature'] = temp_list


"""

Slice hits to events

"""
order = np.argsort(hits["EventID"])                           # 建立一個陣列，儲存按照EventID排序的索引值。
sorted_hits = {key: hits[key][order] for key in hits.keys()}  # 將hits按照EventID排序，變成 sorted_hits 

GiveGlobalID()
GiveEasyAndPhysCoordX()
GiveEasyAndPhysCoordY()
GiveEasyAndPhysCoordZ()


unique_id = np.unique(sorted_hits['EventID'])
# 建立類似TTree結構的字典

# 1. 計算每個 Event 有幾個 Hit (Counts)
#這會回傳每個 EventID 出現的次數，例如 [3, 2, 5...] 代表第0個事件有3個hit...
unique_ids, counts = np.unique(sorted_hits['EventID'], return_counts=True)

# 2. 直接建立 Jagged Array
print("Converting to Awkward Array...")
Tree = {}

for key in sorted_hits.keys():
    # ak.unflatten 根據 counts 把平坦的 numpy array 直接「揉」成鋸齒狀 array
    # 這是 zero-copy 操作，極快且不耗額外記憶體
    Tree[key] = ak.unflatten(sorted_hits[key], counts)

# 把EventID換成使用unique_ids
Tree["EventID"] = ak.Array(unique_ids)

with uproot.recreate(f'{output_path}{file_name}_Processed.root', compression=None) as f:
    f.mktree('DataTree', Tree)

# with uproot.open(f'{output_path}TEST{file_name}_Processed.root') as file:
#     tree = file['DataTree']
#     print("\n--- 驗證寫入內容 ---")
#     tree.show() # 顯示樹的結構

#     # 設定要打印檢查的 Event 數量
#     num_to_print = 5
#     print(f"\n{BLUE}--- 驗證寫入內容: 前 {num_to_print} 筆資料數值 (First {num_to_print} Events Values) ---{RESET}")

#     # 使用 library='ak' 讀取為 Awkward Array (Jagged Array)
#     # entry_start=0, entry_stop=num_to_print 確保只讀取前幾筆，避免讀取整個大檔案造成記憶體負擔
#     arrays = tree.arrays(entry_start=82, entry_stop=87, library='ak')
    
#     # 獲取所有欄位名稱 (Branch Names)
#     branch_names = arrays.fields

#     for i in range(len(arrays)):
#         print(f"\n{GREEN}=== Event {arrays['EventID'][i]} (Index {i}) ==={RESET}")
#         for branch in branch_names:

#             # 獲取該 Event 在該 Branch 的數值 (這通常是一個 List/Array)
#             value = arrays[branch][i]
            
#             # 格式化輸出：靠左對齊，讓數值排版整齊
#             print(f"  {branch:<15}: {value}")
    




""" 
array模組中對於資料型態的代號和ROOT的資料型態代碼對照表
=================== ROOT ===================: 
C : a character string terminated by the 0 character
B : an 8 bit signed integer                           (Char_t)
b : an 8 bit unsigned integer                         (UChar_t)
S : a 16 bit signed integer                           (Short_t)
s : a 16 bit unsigned integer                         (UShort_t)
I : a 32 bit signed integer                           (Int_t)
i : a 32 bit unsigned integer                         (UInt_t)
F : a 32 bit floating point                           (Float_t)
f : a 24 bit floating point with truncated mantissa   (Float16_t)
D : a 64 bit floating point                           (Double_t)
d : a 24 bit truncated floating point                 (Double32_t)
L : a 64 bit signed integer                           (Long64_t)
l : a 64 bit unsigned integer                         (ULong64_t)
G : a long signed integer, stored as 64 bit           (Long_t)
g : a long unsigned integer, stored as 64 bit         (ULong_t)
O : a boolean [the letter o, not a zero]              (Bool_t)

=================== array ===================: 

| Type code | C Type             | Python Type       |
|-----------|--------------------|-------------------|
| 'b'       | signed char        | int               |
| 'B'       | unsigned char      | int               |
| 'u'       | wchar_t            | Unicode character |
| 'w'       | Py_UCS4            | Unicode character |
| 'h'       | signed short       | int               |
| 'H'       | unsigned short     | int               |
| 'i'       | signed int         | int               |
| 'I'       | unsigned int       | int               |
| 'l'       | signed long        | int               |
| 'L'       | unsigned long      | int               |
| 'q'       | signed long long   | int               |
| 'Q'       | unsigned long long | int               |
| 'f'       | float              | float             |
| 'd'       | double             | float             |

"""



