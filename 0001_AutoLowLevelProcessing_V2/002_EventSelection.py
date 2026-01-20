import numpy as np
import pandas as pd
# from tqdm import trange, tqdm
from array import array
import uproot
import json
import awkward as ak
import sys

# def EventsToSheetLikeDict(events):

#     keys = events[0].keys() # 用第一個event來抓key(反正大家都一樣)

#     local_sheet_like_dict = {key: [] for key in keys} # 創一個字典, 每個key對應一個空list
    
#     for event in events:
#         for key in keys:
#             if key in event:
#                 local_sheet_like_dict[key].extend(event[key])

#     return local_sheet_like_dict

# def SheetLikeDictToEvents(sheet_like_dict):
#     # sheet_like_dict: 每個key對應一個list, list中包含所有事件的hits資訊
#     local_events = []
#     unique_ids, start_indices, counts = np.unique(sheet_like_dict["EventID"], return_index=True, return_counts=True)
#     for start, count in zip(start_indices, counts):
#         event = {key: sheet_like_dict[key][start:start+count] for key in sheet_like_dict.keys()}
#         local_events.append(event)
#     return local_events

def NotSingleHitSelection(events):
    """
    :param events: events字典。
    """
    # 移除只有一個hit的event。
    print('\nRemove single hit events')
    # axis=0 是計算有多少個 Event (列數)
    # axis=1 是計算每個 Event 裡面有多少個 Hit (行數/內層長度)
    num_hits = ak.num(events['BoardID'], axis=1)
    mask = num_hits > 1
    filtered_events = events[mask]

    # 打印通過率
    original_len = len(events)
    passed_len = len(filtered_events)
    print(f'通過 NotSingleHitSelection 的事件數量： {passed_len}, 通過率 {100*(passed_len/original_len):.5f}%')

    return filtered_events


def NotShowerSelection(events):
    num_hits = ak.num(events['BoardID'], axis=1)
    mask = num_hits <= 8
    events_less_than_8hits = events[mask]

    L1_hits = ak.sum(events_less_than_8hits['LayerID'] == 1, axis=1)
    L2_hits = ak.sum(events_less_than_8hits['LayerID'] == 2, axis=1)
    L3_hits = ak.sum(events_less_than_8hits['LayerID'] == 3, axis=1)
    L4_hits = ak.sum(events_less_than_8hits['LayerID'] == 4, axis=1)

    mask_final = (L1_hits <= 3) & (L2_hits <= 3) & (L3_hits <= 3) & (L4_hits <= 2)
    NotShowerEvents = events_less_than_8hits[mask_final]

    print(f'通過 NotShowerSelection 的事件數量： {len(NotShowerEvents)}, 通過率{100*(len(NotShowerEvents)/len(events)):.5f}%')
    return NotShowerEvents


def FourLayerHitSelection(events):
    print('\n--> Four Layer Hit Selection (Awkward Version)...')
    
    # 只要該層的 Hit 數 > 0，就代表該層有被觸發
    # axis=1 代表檢查每個 Event 內部
    has_L1 = ak.any(events['LayerID'] == 1, axis=1)
    has_L2 = ak.any(events['LayerID'] == 2, axis=1)
    has_L3 = ak.any(events['LayerID'] == 3, axis=1)
    has_L4 = ak.any(events['LayerID'] == 4, axis=1)

    # 四層都要有 (AND)
    mask = has_L1 & has_L2 & has_L3 & has_L4
    
    filtered_events = events[mask]
    
    print(f'通過 FourLayerHitSelection 的事件數量： {len(filtered_events)}')
    return filtered_events


def TOTSelection(events):
    print('\n--> TOT Selection (Awkward Version)...')

    num_hits = ak.num(events['BoardID'], axis=1)
    mask = num_hits <= 8
    events_less_than_8hits = events[mask]

    L1_hits = ak.sum(events_less_than_8hits['LayerID'] == 1, axis=1)
    L2_hits = ak.sum(events_less_than_8hits['LayerID'] == 2, axis=1)
    L3_hits = ak.sum(events_less_than_8hits['LayerID'] == 3, axis=1)
    L4_hits = ak.sum(events_less_than_8hits['LayerID'] == 4, axis=1)

    mask_NotShower = (L1_hits <= 3) & (L2_hits <= 3) & (L3_hits <= 3) & (L4_hits <= 3)
    NotShowerEvents = events_less_than_8hits[mask_NotShower]

    has_L1 = ak.any(NotShowerEvents['LayerID'] == 1, axis=1)
    has_L2 = ak.any(NotShowerEvents['LayerID'] == 2, axis=1)
    has_L3 = ak.any(NotShowerEvents['LayerID'] == 3, axis=1)
    has_L4 = ak.any(NotShowerEvents['LayerID'] == 4, axis=1)

    mask_TOT = (has_L1 & has_L2) | (has_L2 & has_L3) | (has_L3 & has_L4)
    TOTEvents = NotShowerEvents[mask_TOT]

    print(f'通過 TOTSelection 的事件數量： {len(TOTEvents)}, 通過率{100*(len(TOTEvents)/len(events)):.5f}%')
    return TOTEvents




"""
輸入參數
"""

path        = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/'  # 001_HitsProcessing處理後的ROOT檔案儲存路徑
output_path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/'  # 這個檔案處理後的ROOT檔案儲存路徑

# 檢查是否有輸入參數
if len(sys.argv) < 2:
    print("錯誤: 請輸入檔案名稱")
    sys.exit(1)

file_name = sys.argv[1]  # <--- 讀取第一個參數

if __name__ == "__main__":

    file = uproot.open(f"{path}{file_name}_Processed.root")  
    tree = file["DataTree"]                          

    ak_array = tree.arrays(library="ak")
    event_dict = {field: ak_array[field] for field in ak_array.fields}
    print(type(event_dict))



    # # 把字典前幾個打印出來看看
    # for i in range(100):
    #     print(f'\nEvent {i}:')
    #     for key in event_dict.keys():
    #         print(f'  {key}: {event_dict[key][i]}')

    
    print('--> TOT Selection ...')
    TOTEvents = TOTSelection(ak_array)
    # 轉成字典格式並存檔
    TOTEvents_dict = {field: TOTEvents[field] for field in TOTEvents.fields}

    with uproot.recreate(f"{output_path}{file_name}_AfterTOTSelection.root") as file:
        file.mktree("DataTree", TOTEvents_dict)  # 建立一個新的 TTree，名稱為 "HitsTree" 並寫入資料
    

    print('--> Not Single Hit Selection...')
    events = NotSingleHitSelection(ak_array) # 跟FourLayerHitSelection有重複效果，但後面兩個執行速度較長快，故先執行這個以減少事件數量

    print('--> Not Shower Selection...')
    events = NotShowerSelection(events)

    print('--> Four Layer Hit Selection...')
    events = FourLayerHitSelection(events)
    
    print(f'最終通過事件數量： {len(events)}') 


    final_Events_dict = {field: events[field] for field in events.fields}

    with uproot.recreate(f"{output_path}{file_name}_AfterSelection.root") as file:
        file.mktree("DataTree", final_Events_dict) # 建立一個新的 TTree

