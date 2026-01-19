import uproot
import numpy as np
import ROOT
import sys
import awkward as ak
import pandas as pd

def FlattenEventsToHits(events):
    """
    將 Event-based 的 Awkward Array 轉換為 Hit-based 的 Dictionary (攤平)。
    自動處理 Jagged Array (如 LayerID) 和 Scalar Array (如 EventID) 的差異。
    """
    print('\n--> Flattening events to hits...')
    
    flat_dict = {}
    
    for field in events.fields:
        data = events[field]
        
        # 判斷是否為 Jagged Array (維度 > 1 代表裡面包了 List)
        # axis=1 的維度如果存在，代表它是 jagged
        if data.ndim > 1:
            # 這是 Hit 資訊 (例如 LayerID, ToT)，直接攤平
            flat_dict[field] = ak.flatten(data, axis=1).to_numpy()
        else:
            # 這是 Event 資訊 (例如 EventID, Timestamp)，每個 Event 只有一個值
            # 我們需要把它 "廣播" (複製) 到跟該 Event 的 Hits 數量一樣多
            # 例如 Event 0 有 3 個 hits，EventID 就要重複 3 次
            expanded_data = ak.broadcast_arrays(data, events['BoardID'])[0]
            flat_dict[field] = ak.flatten(expanded_data, axis=1).to_numpy()

    return flat_dict


# 設定靜默模式
ROOT.gROOT.SetBatch(True)

# 設定 ROOT 繪圖風格
ROOT.gStyle.SetOptStat(0) # 關閉統計框
ROOT.gStyle.SetPalette(ROOT.kCool) # 設定顏色主題 https://root.cern.ch/doc/v636/classTColor.html


path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/'  
plots_path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots/' 
plots_path_pdf = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots/PDF/'
# 讀取檔案
filename = sys.argv[1]  # <--- 讀取第一個參數

"""
Without Selection
"""

# 嘗試開啟檔案
try:
    file = uproot.open(f"{path}{filename}_Processed.root")
    tree = file["DataTree"]
    ak_array = tree.arrays(library="ak")
    event_dict = {field: ak_array[field] for field in ak_array.fields}

    # # 打印前100個事件看看
    # for i in range(100):
    #     print(f'\nEvent {i}:')
    #     for key in event_dict.keys():
    #         print(f'  {key}: {event_dict[key][i]}')


    hits_dict = FlattenEventsToHits(ak_array)

    # # 設定pandas顯示選項，避免列數過多被截斷
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # df = pd.DataFrame(hits_dict)
    # print(df.head(120))


except FileNotFoundError:
    print(f"Error: File {path}{filename}_Processed.root not found.")
    exit()


# ---------------------------------------------------------
# Part 1: 原有的個別 Board 繪圖 (保持不變)
# ---------------------------------------------------------
c1 = ROOT.TCanvas("c1", "Hit Maps Per Board", 800, 600)

c1.Print(f"{plots_path_pdf}{filename}_HitLevelPerBoard_NoSelection.pdf" + "[") 

print("Generating individual Board maps...")

# 預先計算每個 BID 的 counts 以便 Part 2 重複使用
bid_counts_cache = {}

for BID in range(1, 17):
    bid_mask = (hits_dict['BoardID'] == BID)
    channels_in_bid = hits_dict['ChannelID'][bid_mask]
    counts_for_this_BID = np.bincount(channels_in_bid, minlength=16)
    bid_counts_cache[BID] = counts_for_this_BID 

    # --- 繪圖邏輯 ---
    hist_name = f"h_BID_{BID}"
    hist_title = f"Hit Level - Board {BID};;"
    h_map = ROOT.TH2F(hist_name, hist_title, 4, 0, 4, 4, 0, 4)

    for CID in range(16):
        count = counts_for_this_BID[CID]
        bin_x = (CID % 4) + 1       
        bin_y = int(CID / 4) + 1    
        h_map.SetBinContent(bin_x, bin_y, count)

    max_count = np.max(counts_for_this_BID)
    h_map.SetMaximum(max_count * 1.2 if max_count > 0 else 1) 
    
    h_map.Draw("COLZ") 

    latex = ROOT.TLatex()
    latex.SetTextFont(42)
    latex.SetTextAlign(22)
    
    for CID in range(16):
        count = counts_for_this_BID[CID]
        x_center = (CID % 4) + 0.5
        y_center = int(CID / 4) + 0.5
        
        latex.SetTextSize(0.035)
        latex.SetTextColor(ROOT.kBlack)
        latex.DrawLatex(x_center, y_center + 0.15, f"CH {CID}")
        
        latex.SetTextSize(0.045)
        latex.DrawLatex(x_center, y_center - 0.15, f"{int(count)}")

    c1.Update()
    c1.Print(f"{plots_path_pdf}{filename}_HitLevelPerBoard_NoSelection.pdf") 

c1.Print(f"{plots_path_pdf}{filename}_HitLevelPerBoard_NoSelection.pdf" + "]")
print(f"Part 1 Done. Saved to {f'{plots_path_pdf}{filename}_HitLevelPerBoard_NoSelection.pdf'}")

# ==========================================
#          計算全域 Colorbar 範圍
# ==========================================
# 1. 收集所有 Board (1~16) 的 counts 數據
all_global_counts = []
for counts in bid_counts_cache.values():
    all_global_counts.extend(counts)

# 轉為 numpy array 以便計算
all_global_counts = np.array(all_global_counts)

# 2. 計算 5百分位數 (min) 和 10百分位數 (max)
# 注意：將最大值設為 10百分位數會導致前 90% 的高計數區域顏色飽和（變成最高色），
# 這通常用於觀察低計數區域的雜訊或特徵。
z_min = np.min(all_global_counts)  
z_max = np.percentile(all_global_counts, 95)

# 防呆：如果 max <= min (例如數據全是0)，給予一個微小區間避免錯誤
if z_max <= z_min:
    z_max = z_min + 1.0

# ---------------------------------------------------------
# Part 2: 組合繪圖 (4 Boards per Layer) - 包含 PDF 與 PNG 匯總圖
# ---------------------------------------------------------
# 建立 PDF 用的 Canvas (單頁單層)
c2 = ROOT.TCanvas("c2", "Layer Maps", 800, 800)
c2.SetRightMargin(0.18)

c2.Print(f"{plots_path_pdf}{filename}_HitLevelCombined4Layers_NoSelection.pdf" + "[")

# 新增：建立 PNG 匯總用的 Canvas (2x2 Grid)
c_summary = ROOT.TCanvas("c_summary", "All Layers Summary", 3200, 3200)
c_summary.Divide(2, 2) # 切割成 2x2，左上是1，右上是2，左下3，右下4

print("Generating combined Layer maps...")

for layer_idx in range(4):
    L_num = layer_idx + 1
    
    # 計算這一層對應的 Board IDs
    start_bid = layer_idx * 4 + 1
    bid_tr = start_bid
    bid_tl = start_bid + 1
    bid_br = start_bid + 2
    bid_bl = start_bid + 3

    # 定義 8x8 Histogram
    hist_name_layer = f"h_Layer_{L_num}"
    hist_title_layer = f"Hit Level - Layer {L_num};;"
    h_layer = ROOT.TH2F(hist_name_layer, hist_title_layer, 8, 0, 8, 8, 0, 8)

    all_counts_in_layer = []
    text_to_draw = []

    layer_config = [
        (bid_tr, 4, 4, "TR"), 
        (bid_tl, 0, 4, "TL"), 
        (bid_br, 4, 0, "BR"), 
        (bid_bl, 0, 0, "BL")  
    ]

    # 填入 Histogram 資料
    for bid, off_x, off_y, pos_name in layer_config:
        counts = bid_counts_cache.get(bid, np.zeros(16))
        all_counts_in_layer.extend(counts)

        for CID in range(16):
            count = counts[CID]
            local_y = 4 - int(CID / 4)
            if pos_name == "TL" or pos_name == "BR":
                local_x = (CID % 4) + 1
            else:
                local_x = 4 - (CID % 4)
            
            global_bin_x = local_x + off_x
            global_bin_y = local_y + off_y
            
            h_layer.SetBinContent(global_bin_x, global_bin_y, count)
            
            text_x = (global_bin_x - 1) + 0.5 
            text_y = (global_bin_y - 1) + 0.5
            
            text_to_draw.append({
                "x": text_x,
                "y": text_y,
                "cid": CID,
                "count": count
            })

    # 動態設定 Z 軸範圍為全域範圍
    # max_count = np.max(all_counts_in_layer) if len(all_counts_in_layer) > 0 else 0
    # h_layer.SetMaximum(max_count * 1.2 if max_count > 0 else 1)
    h_layer.SetMinimum(z_min)
    h_layer.SetMaximum(z_max)

    # -----------------------------------------------------
    # 繪圖動作 1: 畫在 c2 (PDF)
    # -----------------------------------------------------
    c2.cd()
    h_layer.Draw("COLZ")
    
    # 畫線
    line = ROOT.TLine()
    line.SetLineColor(ROOT.kBlack)
    line.SetLineWidth(2)
    line.DrawLine(0, 4, 8, 4)
    line.DrawLine(4, 0, 4, 8)

    # 畫文字
    latex = ROOT.TLatex()
    latex.SetTextFont(42)
    latex.SetTextAlign(22)
    for item in text_to_draw:
        latex.SetTextSize(0.02) 
        latex.SetTextColor(ROOT.kBlack)
        latex.DrawLatex(item["x"], item["y"] + 0.2, f"CH {item['cid']}")
        latex.SetTextSize(0.025)
        latex.DrawLatex(item["x"], item["y"] - 0.2, f"{int(item['count'])}")

    # 畫 Label
    latex_label = ROOT.TLatex()
    latex_label.SetTextSize(0.04)
    latex_label.SetTextColor(ROOT.kRed)
    latex_label.SetTextAlign(22)
    latex_label.DrawLatex(6, 8.2, f"Board {bid_tr}")
    latex_label.DrawLatex(2, 8.2, f"Board {bid_tl}")
    latex_label.DrawLatex(6, -0.6, f"Board {bid_br}")
    latex_label.DrawLatex(2, -0.6, f"Board {bid_bl}")

    c2.Update()
    c2.Print(f"{plots_path_pdf}{filename}_HitLevelCombined4Layers_NoSelection.pdf")

    # -----------------------------------------------------
    # 繪圖動作 2: 畫在 c_summary (PNG Grid)
    # -----------------------------------------------------
    c_summary.cd(L_num) # 切換到對應的子圖 (1, 2, 3, 4)
    ROOT.gPad.SetRightMargin(0.2) # 子圖也要設定右邊界給色條
    
    # 使用 DrawCopy 因為 h_layer 在下一次迴圈會被重置
    h_layer.DrawCopy("COLZ") 

    
    # 注意：TLine 和 TLatex 是繪圖指令，需要再執行一次才會畫在當前的 Pad 上
    line.DrawLine(0, 4, 8, 4)
    line.DrawLine(4, 0, 4, 8)

    for item in text_to_draw:
        latex.SetTextSize(0.02) 
        latex.SetTextColor(ROOT.kBlack)
        latex.DrawLatex(item["x"], item["y"] + 0.2, f"CH {item['cid']}")
        latex.SetTextSize(0.025)
        latex.DrawLatex(item["x"], item["y"] - 0.2, f"{int(item['count'])}")

    latex_label.DrawLatex(6, 8.2, f"Board {bid_tr}")
    latex_label.DrawLatex(2, 8.2, f"Board {bid_tl}")
    latex_label.DrawLatex(6, -0.6, f"Board {bid_br}")
    latex_label.DrawLatex(2, -0.6, f"Board {bid_bl}")


# 儲存 PDF 結尾
c2.Print(f"{plots_path_pdf}{filename}_HitLevelCombined4Layers_NoSelection.pdf" + "]")
print(f"Part 2 Done. Saved PDF to {plots_path_pdf}{filename}_HitLevelCombined4Layers_NoSelection.pdf")

# 儲存 PNG 匯總圖
png_filename = f"{plots_path}{filename}_HitLevelCombined4Layers_NoSelection.png"
c_summary.SaveAs(png_filename)
print(f"Summary Image Saved to {png_filename}")


del c1, c2, c_summary, line, latex, latex_label, h_layer, h_map, tree, file, hits_dict, bid_counts_cache, all_global_counts, counts_for_this_BID

"""

With Selection

"""

# 嘗試開啟檔案
try:
    file = uproot.open(f"{path}{filename}_AfterSelection.root")
    tree = file["DataTree"]
    ak_array = tree.arrays(library="ak")
    event_dict = {field: ak_array[field] for field in ak_array.fields}

    # # 打印前100個事件看看
    # for i in range(100):
    #     print(f'\nEvent {i}:')
    #     for key in event_dict.keys():
    #         print(f'  {key}: {event_dict[key][i]}')


    hits_dict = FlattenEventsToHits(ak_array)

    # # 設定pandas顯示選項，避免列數過多被截斷
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # df = pd.DataFrame(hits_dict)
    # print(df.head(120))


except FileNotFoundError:
    print(f"Error: File {path}{filename}_Processed.root not found.")
    exit()

# ---------------------------------------------------------
# Part 1: 原有的個別 Board 繪圖 (保持不變)
# ---------------------------------------------------------
c1 = ROOT.TCanvas("c1", "Hit Maps Per Board", 800, 600)

c1.Print(f"{plots_path_pdf}{filename}_HitLevelPerBoard.pdf" + "[") 

print("Generating individual Board maps...")

# 預先計算每個 BID 的 counts 以便 Part 2 重複使用
bid_counts_cache = {}

for BID in range(1, 17):
    bid_mask = (hits_dict['BoardID'] == BID)
    channels_in_bid = hits_dict['ChannelID'][bid_mask]
    counts_for_this_BID = np.bincount(channels_in_bid, minlength=16)
    bid_counts_cache[BID] = counts_for_this_BID 

    # --- 繪圖邏輯 ---
    hist_name = f"h_BID_{BID}"
    hist_title = f"Hit Level - Board {BID};;"
    h_map = ROOT.TH2F(hist_name, hist_title, 4, 0, 4, 4, 0, 4)

    for CID in range(16):
        count = counts_for_this_BID[CID]
        bin_x = (CID % 4) + 1       
        bin_y = int(CID / 4) + 1    
        h_map.SetBinContent(bin_x, bin_y, count)

    max_count = np.max(counts_for_this_BID)
    h_map.SetMaximum(max_count * 1.2 if max_count > 0 else 1) 
    
    h_map.Draw("COLZ") 

    latex = ROOT.TLatex()
    latex.SetTextFont(42)
    latex.SetTextAlign(22)
    
    for CID in range(16):
        count = counts_for_this_BID[CID]
        x_center = (CID % 4) + 0.5
        y_center = int(CID / 4) + 0.5
        
        latex.SetTextSize(0.035)
        latex.SetTextColor(ROOT.kBlack)
        latex.DrawLatex(x_center, y_center + 0.15, f"CH {CID}")
        
        latex.SetTextSize(0.045)
        latex.DrawLatex(x_center, y_center - 0.15, f"{int(count)}")

    c1.Update()
    c1.Print(f"{plots_path_pdf}{filename}_HitLevelPerBoard.pdf") 

c1.Print(f"{plots_path_pdf}{filename}_HitLevelPerBoard.pdf" + "]")
print(f"Part 1 Done. Saved to {f'{plots_path_pdf}{filename}_HitLevelPerBoard.pdf'}")

# ==========================================
#          計算全域 Colorbar 範圍
# ==========================================
# 1. 收集所有 Board (1~16) 的 counts 數據
all_global_counts = []
for counts in bid_counts_cache.values():
    all_global_counts.extend(counts)

# 轉為 numpy array 以便計算
all_global_counts = np.array(all_global_counts)

# 2. 計算 5百分位數 (min) 和 10百分位數 (max)
# 注意：將最大值設為 10百分位數會導致前 90% 的高計數區域顏色飽和（變成最高色），
# 這通常用於觀察低計數區域的雜訊或特徵。
z_min = np.min(all_global_counts)  
z_max = np.percentile(all_global_counts, 95)

# 防呆：如果 max <= min (例如數據全是0)，給予一個微小區間避免錯誤
if z_max <= z_min:
    z_max = z_min + 1.0

# ---------------------------------------------------------
# Part 2: 組合繪圖 (4 Boards per Layer) - 包含 PDF 與 PNG 匯總圖
# ---------------------------------------------------------
# 建立 PDF 用的 Canvas (單頁單層)
c2 = ROOT.TCanvas("c2", "Layer Maps", 800, 800)
c2.SetRightMargin(0.18)

c2.Print(f"{plots_path_pdf}{filename}_HitLevelCombined4Layers.pdf" + "[")

# 新增：建立 PNG 匯總用的 Canvas (2x2 Grid)
c_summary = ROOT.TCanvas("c_summary", "All Layers Summary", 3200, 3200)
c_summary.Divide(2, 2) # 切割成 2x2，左上是1，右上是2，左下3，右下4

print("Generating combined Layer maps...")

for layer_idx in range(4):
    L_num = layer_idx + 1
    
    # 計算這一層對應的 Board IDs
    start_bid = layer_idx * 4 + 1
    bid_tr = start_bid
    bid_tl = start_bid + 1
    bid_br = start_bid + 2
    bid_bl = start_bid + 3

    # 定義 8x8 Histogram
    hist_name_layer = f"h_Layer_{L_num}"
    hist_title_layer = f"Hit Level - Layer {L_num};;"
    h_layer = ROOT.TH2F(hist_name_layer, hist_title_layer, 8, 0, 8, 8, 0, 8)

    all_counts_in_layer = []
    text_to_draw = []

    layer_config = [
        (bid_tr, 4, 4, "TR"), 
        (bid_tl, 0, 4, "TL"), 
        (bid_br, 4, 0, "BR"), 
        (bid_bl, 0, 0, "BL")  
    ]

    # 填入 Histogram 資料
    for bid, off_x, off_y, pos_name in layer_config:
        counts = bid_counts_cache.get(bid, np.zeros(16))
        all_counts_in_layer.extend(counts)

        for CID in range(16):
            count = counts[CID]
            local_y = 4 - int(CID / 4)
            if pos_name == "TL" or pos_name == "BR":
                local_x = (CID % 4) + 1
            else:
                local_x = 4 - (CID % 4)
            
            global_bin_x = local_x + off_x
            global_bin_y = local_y + off_y
            
            h_layer.SetBinContent(global_bin_x, global_bin_y, count)
            
            text_x = (global_bin_x - 1) + 0.5 
            text_y = (global_bin_y - 1) + 0.5
            
            text_to_draw.append({
                "x": text_x,
                "y": text_y,
                "cid": CID,
                "count": count
            })

    # 動態設定 Z 軸範圍為全域範圍
    # max_count = np.max(all_counts_in_layer) if len(all_counts_in_layer) > 0 else 0
    # h_layer.SetMaximum(max_count * 1.2 if max_count > 0 else 1)
    h_layer.SetMinimum(z_min)
    h_layer.SetMaximum(z_max)

    # -----------------------------------------------------
    # 繪圖動作 1: 畫在 c2 (PDF)
    # -----------------------------------------------------
    c2.cd()
    h_layer.Draw("COLZ")
    
    # 畫線
    line = ROOT.TLine()
    line.SetLineColor(ROOT.kBlack)
    line.SetLineWidth(2)
    line.DrawLine(0, 4, 8, 4)
    line.DrawLine(4, 0, 4, 8)

    # 畫文字
    latex = ROOT.TLatex()
    latex.SetTextFont(42)
    latex.SetTextAlign(22)
    for item in text_to_draw:
        latex.SetTextSize(0.02) 
        latex.SetTextColor(ROOT.kBlack)
        latex.DrawLatex(item["x"], item["y"] + 0.2, f"CH {item['cid']}")
        latex.SetTextSize(0.025)
        latex.DrawLatex(item["x"], item["y"] - 0.2, f"{int(item['count'])}")

    # 畫 Label
    latex_label = ROOT.TLatex()
    latex_label.SetTextSize(0.04)
    latex_label.SetTextColor(ROOT.kRed)
    latex_label.SetTextAlign(22)
    latex_label.DrawLatex(6, 8.2, f"Board {bid_tr}")
    latex_label.DrawLatex(2, 8.2, f"Board {bid_tl}")
    latex_label.DrawLatex(6, -0.6, f"Board {bid_br}")
    latex_label.DrawLatex(2, -0.6, f"Board {bid_bl}")

    c2.Update()
    c2.Print(f"{plots_path_pdf}{filename}_HitLevelCombined4Layers.pdf")

    # -----------------------------------------------------
    # 繪圖動作 2: 畫在 c_summary (PNG Grid)
    # -----------------------------------------------------
    c_summary.cd(L_num) # 切換到對應的子圖 (1, 2, 3, 4)
    ROOT.gPad.SetRightMargin(0.2) # 子圖也要設定右邊界給色條
    
    # 使用 DrawCopy 因為 h_layer 在下一次迴圈會被重置
    h_layer.DrawCopy("COLZ") 

    
    # 注意：TLine 和 TLatex 是繪圖指令，需要再執行一次才會畫在當前的 Pad 上
    line.DrawLine(0, 4, 8, 4)
    line.DrawLine(4, 0, 4, 8)

    for item in text_to_draw:
        latex.SetTextSize(0.02) 
        latex.SetTextColor(ROOT.kBlack)
        latex.DrawLatex(item["x"], item["y"] + 0.2, f"CH {item['cid']}")
        latex.SetTextSize(0.025)
        latex.DrawLatex(item["x"], item["y"] - 0.2, f"{int(item['count'])}")

    latex_label.DrawLatex(6, 8.2, f"Board {bid_tr}")
    latex_label.DrawLatex(2, 8.2, f"Board {bid_tl}")
    latex_label.DrawLatex(6, -0.6, f"Board {bid_br}")
    latex_label.DrawLatex(2, -0.6, f"Board {bid_bl}")


# 儲存 PDF 結尾
c2.Print(f"{plots_path_pdf}{filename}_HitLevelCombined4Layers.pdf" + "]")
print(f"Part 2 Done. Saved PDF to {plots_path_pdf}{filename}_HitLevelCombined4Layers.pdf")

# 儲存 PNG 匯總圖
png_filename = f"{plots_path}{filename}_HitLevelCombined4Layers.png"
c_summary.SaveAs(png_filename)
print(f"Summary Image Saved to {png_filename}")