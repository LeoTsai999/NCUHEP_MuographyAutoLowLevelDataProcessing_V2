# import uproot
# import numpy as np
# import ROOT
# from tqdm import tqdm, trange
# import sys
# import os
# from array import array


# """ ROOT 全域設定 """
# # 設定擬和結果展示
# ROOT.gStyle.SetOptFit(1111)
# # 關閉直方圖統計框
# ROOT.gStyle.SetOptStat(0)
#     # 設定寬度和高度
# ROOT.gStyle.SetStatW(0.15) # 寬度 
# ROOT.gStyle.SetStatH(0.1) # 高度 
#     # 設定位置 (X, Y是統計筐右上角)
# ROOT.gStyle.SetStatX(0.85) # 靠右
# ROOT.gStyle.SetStatY(0.85) # 靠上
# # 靜默模式
# ROOT.gROOT.SetBatch(True)
# ROOT.gStyle.SetPalette(ROOT.kCool) # 設定顏色主題 https://root.cern.ch/doc/v636/classTColor.html
# # 子圖邊距
# ROOT.gStyle.SetPadLeftMargin(0.20)
# ROOT.gStyle.SetPadRightMargin(0.10)
# ROOT.gStyle.SetPadTopMargin(0.125)
# ROOT.gStyle.SetPadBottomMargin(0.125)

# """ 設定 Minimizer """
# # 1. 設定 Minimizer(例如 "Minuit2", "Minuit", "GSLMultiMin")
# # 2. 設定演算法 ("Migrad", "Simplex", "Combined")
# ROOT.Math.MinimizerOptions.SetDefaultMinimizer("Minuit2", "Combined")

# # 其他設定
# ROOT.Math.MinimizerOptions.SetDefaultMaxFunctionCalls(1000000) # 增加最大迭代次數
# ROOT.Math.MinimizerOptions.SetDefaultTolerance(0.01)           # 設定收斂容許度
# ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(1)             # 設定輸出多少 (0=靜默, 1=正常, 2=詳細)

# """ 列印 Minimizer 設定參數 """
# ROOT.Math.MinimizerOptions.PrintDefault()


# """ 載入 langaus2.C  """
# macro_path = "/data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/langaus2.C"
# if os.path.exists(macro_path):
#     ROOT.gInterpreter.LoadMacro(f"{macro_path}")
# else:
#     print(f"Error: {macro_path} not found!")
#     exit()


# """ 路徑設定 """

# filename = sys.argv[1]  # <- 讀取第一個參數
# filename2 = sys.argv[2]  # <- 讀取第二個參數
# filename3 = sys.argv[3]  # <- 讀取第三個參數
# filename4 = sys.argv[4]  # <- 讀取第四個參數
# filename5 = sys.argv[5]  # <- 讀取第五個參數
# filename6 = sys.argv[6]  # <- 讀取第六個參數
# filename7 = sys.argv[7]  # <- 讀取第七個參數
# filename8 = sys.argv[8]  # <- 讀取第八個參數

# path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData'
# # 儲存圖片路徑
# output_path = f"/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots"
# output_pdf_name = f"{output_path}/TEST_{filename}_TOT.pdf"

# """ 讀取 ROOT file 為字典 """
# try:
#     file = uproot.open(f"{path}/{filename}_AfterToTSelection1.root")
#     tree = file["HitsTree"]
#     hits_dict = tree.arrays(library="np")
# except FileNotFoundError:
#     print(f"Error: File {path}/{filename}_AfterToTSelection1.root not found.")
#     exit()


# if __name__ == "__main__":

#     # 建立空的 histogram 字典
#     histograms = {'B1': [], 'B2': [],'B3': [], 'B4': [], 
#                   'B5': [], 'B6': [], 'B7': [], 'B8': [], 
#                   'B9': [], 'B10': [], 'B11': [], 'B12': [], 
#                   'B13': [], 'B14': [], 'B15': [], 'B16': []}

#     # 為每個 Board 和 Channel 建立 TH1F 物件
#     for board, bid in tqdm(zip(histograms.keys(), range(1, 17)), desc='Building Histograms', total=len(histograms)):
#         for channel in range(0, 16):
#             amplitudes = hits_dict['Amplitude'][(hits_dict['BoardID'] == bid) & (hits_dict['ChannelID'] == channel)]

#             edges = np.concatenate([
#                 np.arange(0, 500, 5),      # 0-500 之間5 為一格
#                 np.arange(500, 1000,15),   # 500-1000 之間 15 為一格
#                 # np.arange(1000, 1500, 40),  # 1000-1500 之間 40 為一格

#             ])
#             xbins = array('d', edges)       # 轉成 ROOT 吃的 double array
#             n_bins = len(xbins) - 1         # 計算 bin 數量

#             hist = ROOT.TH1F(f"{board}_Ch{channel}_Amps", 
#                  f"{board} Channel {channel} Amps Distribution;Amps;Counts", 
#                  n_bins, xbins)

#             hist.Sumw2()

#             hist.FillN(len(amplitudes), amplitudes.astype(np.float64), np.ones(len(amplitudes), dtype=np.float64))
#             hist.Scale(1.0, "width") # 除以binwidth
#             histograms[board].append(hist)



#     pythonic_Pad_mapping = [13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4]
#     dummy_canvas = ROOT.TCanvas("dummy_canvas", "Dummy Canvas", 4000, 4000 )
#     dummy_canvas.Print(output_pdf_name + "[")
#     dummy_canvas.Close()


#     """擬合與繪圖"""
#     TOT_all=[]
#     GSigma_all=[]
#     redchisq_all=[]
#     difference_all=[]
#     for board, hists in tqdm(histograms.items(), desc="Plotting Boards"):
#         canvas = ROOT.TCanvas(f"{board}_ToT", f"{board} ToT", 4000, 4000)
#         canvas.Divide(4, 4)  # 4x4 網格

#         for i, hist in enumerate(hists):       # hists 裡面有 16 個 histogram, 代表CH0~CH15。每個CH都是一個hist, 為TH1F物件
#             canvas.cd(pythonic_Pad_mapping[i]) # 切換到指定子圖 用pythonic mapping(ROOT左上角是1 右下角是16)
            
#             # 尋找0.4倍高寬點
#             left_half_max = None
#             right_half_max = None
#             max_bin_index = hist.GetMaximumBin()
#             max_content = hist.GetBinContent(max_bin_index)
#             half_max = max_content * 0.3
#             # 向左尋找
#             for bin_idx in range(max_bin_index, 0, -1):
#                 if hist.GetBinContent(bin_idx) <= half_max:
#                     left_half_max = hist.GetXaxis().GetBinCenter(bin_idx)
#                     break
#             # 向右尋找
#             for bin_idx in range(max_bin_index, hist.GetNbinsX() + 1):
#                 if hist.GetBinContent(bin_idx) <= half_max:
#                     right_half_max = hist.GetXaxis().GetBinCenter(bin_idx)
#                     break
#             if left_half_max is None or right_half_max is None:
#                 print(f"Warning: Could not find half max points for {board} Channel {i}. Skipping fit.")
#                 hist.Draw()
#                 continue
#             print(f'{board} Ch{i} Half Max Points: Left {left_half_max}, Right {right_half_max}, max content {max_content}')

#             # Fit Range
#             # fr = array('d', [left_half_max, right_half_max])
#             fr = array('d', [140, 650])
#             # Start Values (sv): Width, MP, Area, GSigma
#             # 找到最大值位置作為MP初始值
#             max_bin_index = hist.GetMaximumBin()
#             max_content = hist.GetBinContent(max_bin_index)
#             max_x_center = hist.GetXaxis().GetBinCenter(max_bin_index)

#             # 面積作為Area初始值
#             # area_guess = hist.Integral()
#             # 修改後的寫法 (正確)
#             area_guess = hist.Integral("width")


#             print(f'B{board} Ch{i} Fit Range: {left_half_max} to {right_half_max}, Max at {max_x_center} with Area {area_guess}')

#             # sv = array('d', [20.0, max_x_center, area_guess, 7.5]) # pwidth擬合參數初始值
#             sv = array('d', [30.0, max_x_center, area_guess, 20]) # amplitude擬合參數初始值
            
#             # Parameter Limits (pllo, plhi)
#             # Width, MP, Area, GSigma
#             '''pwidth擬合參數範圍'''
#             # pllo = array('d', [1.0, 15.0, 1.0, 1])
#             # plhi = array('d', [100.0, 25.0, 100000.0, 5.0])
#             '''amplitude擬合參數範圍'''
#             pllo = array('d', [15.0, max_x_center - 15.0, area_guess * 0.5, 15.0])
#             plhi = array('d', [30.0, max_x_center + 15.0, area_guess * 3.0, 50.0])
            
#             # 用於接收結果的 Array
#             fp = array('d', [0.0]*4)    # fit params
#             fpe = array('d', [0.0]*4)   # fit errors
#             chisqr = array('d', [0.0])  # chi square
#             ndf = array('i', [0])       # NDF

#             # 執行擬合
#             fit_func = ROOT.langaufit(hist, fr, sv, pllo, plhi, fp, fpe, chisqr, ndf)
#             TOT_all.append(fp[1])
#             GSigma_all.append(fp[3])
#             redchisq = chisqr[0] / ndf[0] if ndf[0] != 0 else 0
#             redchisq_all.append(redchisq)

#             hist.GetXaxis().SetLabelSize(0.06)
#             hist.GetXaxis().SetTitleSize(0.06)
#             hist.GetXaxis().SetTitle("PWidth(100ns)")
#             hist.GetXaxis().SetNdivisions(505) # 設定 X 軸刻度數量

#             hist.GetYaxis().SetLabelSize(0.06)
#             hist.GetYaxis().SetTitleSize(0.06)
#             hist.SetLineColor(ROOT.kBlack)
#             hist.Draw()
            
#             if redchisq > 5.0 :
#                 fit_func.SetLineColor(ROOT.kRed)
#             elif redchisq < 0.5:
#                 fit_func.SetLineColor(ROOT.kGreen)
#             else:
#                 fit_func.SetLineColor(ROOT.kBlue)

#             fit_func.SetLineWidth(1)
#             fit_func.Draw("lsame")
#             # 強制更新畫面
#             ROOT.gPad.Update()
            
#             # 抓取標題物件
#             pt = ROOT.gPad.GetPrimitive("title")
#             # 修改標題屬性
#             if pt:
#                 # === 設定對齊與大小 ===
#                 pt.SetTextSize(0.05)   
#                 pt.SetTextAlign(23)    
                
#                 pt.SetX1NDC(0.25)      # 左邊界
#                 pt.SetX2NDC(0.9)       # 右邊界
#                 pt.SetY1NDC(0.90)      # 方塊底部高度
#                 pt.SetY2NDC(0.98)      # 方塊頂部高度
                
#                 pt.SetBorderSize(0)    # 去除框黑線
#                 pt.SetFillColor(0)     # 背景透明
#                 pt.SetFillStyle(0)     # 透明背景樣式
                
#                 # 更新
#                 ROOT.gPad.Modified()

#         canvas.Print(output_pdf_name)
#         canvas.Close()

#     # TOT分佈
#     TOT_all = np.array(TOT_all)
#     mean_TOT = np.mean(TOT_all)
#     std_TOT = np.std(TOT_all)
#     print(f"Overall ToT Mean: {mean_TOT:.2f}, Std Deviation: {std_TOT:.2f}")
#     TOT_hist = ROOT.TH1F("Overall_ToT", "Overall ToT Distribution;ToT;Counts", int(np.max(TOT_all)*1.1), 0, np.max(TOT_all)*1.1)
#     n_tot = len(TOT_all)
#     if n_tot > 0:
#         TOT_hist.FillN(n_tot, TOT_all.astype(np.float64), np.ones(n_tot, dtype=np.float64))
#     TOT_hist.GetXaxis().SetTitle("ToT(100ns)")
    
#     TOT_canvas = ROOT.TCanvas("Overall_ToT_Canvas", "Overall ToT", 1200, 800)
#     # 開啟統計框
#     ROOT.gStyle.SetOptStat(1111)
#     TOT_hist.Draw()
#     TOT_canvas.Print(output_pdf_name)
#     TOT_canvas.Close()

#     # GSigma 分佈
#     GSigma_all = np.array(GSigma_all)
#     mean_GSigma = np.mean(GSigma_all)
#     std_GSigma = np.std(GSigma_all)
#     print(f"Overall GSigma Mean: {mean_GSigma:.2f}, Std Deviation: {std_GSigma:.2f}")
#     GSigma_hist = ROOT.TH1F("Overall_GSigma", "Overall GSigma Distribution;GSigma;Counts", 100, 0, int(np.max(GSigma_all)*1.2))
#     n_gsigma = len(GSigma_all)
#     if n_gsigma > 0:
#         GSigma_hist.FillN(n_gsigma, GSigma_all.astype(np.float64), np.ones(n_gsigma, dtype=np.float64))
#     GSigma_canvas = ROOT.TCanvas("Overall_GSigma_Canvas", "Overall GSigma", 1200, 800)
#     GSigma_hist.Draw()
#     GSigma_canvas.Print(output_pdf_name)
#     GSigma_canvas.Close()

#     # RedChiSq 分佈
#     redchisq_all = np.array(redchisq_all)
#     redchisq_hist = ROOT.TH1F("Overall_RedChiSq", "Overall RedChiSq Distribution;RedChiSq;Counts", 50, 0, int(max(redchisq_all)*1.2)+1)
#     n_redchisq = len(redchisq_all)
#     if n_redchisq > 0:
#         redchisq_hist.FillN(n_redchisq, redchisq_all.astype(np.float64), np.ones(n_redchisq, dtype=np.float64))
#     redchisq_canvas = ROOT.TCanvas("Overall_RedChiSq_Canvas", "Overall RedChiSq", 1200, 800)
#     redchisq_hist.Draw()
#     redchisq_canvas.Print(output_pdf_name)
#     redchisq_canvas.Close()

#     dummy_canvas = ROOT.TCanvas()
#     dummy_canvas.Print(output_pdf_name + "]")
#     dummy_canvas.Close()

#     print("Pwidth distribution histograms have been generated and saved.")
    

import uproot
import numpy as np
import ROOT
from tqdm import tqdm, trange
import sys
import os
from array import array

""" ROOT 全域設定 """
# 設定擬和結果展示
ROOT.gStyle.SetOptFit(1111)
# 關閉直方圖統計框
ROOT.gStyle.SetOptStat(0)
    # 設定寬度和高度
ROOT.gStyle.SetStatW(0.15) # 寬度 
ROOT.gStyle.SetStatH(0.1) # 高度 
    # 設定位置 (X, Y是統計筐右上角)
ROOT.gStyle.SetStatX(0.85) # 靠右
ROOT.gStyle.SetStatY(0.85) # 靠上
# 靜默模式
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPalette(ROOT.kCool) # 設定顏色主題
# 子圖邊距
ROOT.gStyle.SetPadLeftMargin(0.20)
ROOT.gStyle.SetPadRightMargin(0.10)
ROOT.gStyle.SetPadTopMargin(0.125)
ROOT.gStyle.SetPadBottomMargin(0.125)

""" 設定 Minimizer """
# 1. 設定 Minimizer
ROOT.Math.MinimizerOptions.SetDefaultMinimizer("Minuit2", "Combined")

# 其他設定
ROOT.Math.MinimizerOptions.SetDefaultMaxFunctionCalls(1000000) # 增加最大迭代次數
ROOT.Math.MinimizerOptions.SetDefaultTolerance(0.01)           # 設定收斂容許度
ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(0)             # 設定輸出 (0=靜默, 避免隨機嘗試時刷屏)

""" 載入 langaus2.C  """
macro_path = "/data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/langaus2.C"
if os.path.exists(macro_path):
    ROOT.gInterpreter.LoadMacro(f"{macro_path}")
else:
    print(f"Error: {macro_path} not found!")
    exit()


""" 路徑設定 """
# 檢查參數是否存在，否則給預設值或報錯 (這裡假設使用者會傳入參數)
if len(sys.argv) < 2:
    print("Usage: python script.py <filename> ...")
    sys.exit(1)

filename = sys.argv[1]  

path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData'
# 儲存圖片路徑
output_path = f"/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots"
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
output_pdf_name = f"{output_path}/RandomFit_{filename}_TOT_.pdf" # 改檔名以區別

""" 讀取 ROOT file 為字典 """
try:
    file = uproot.open(f"{path}/{filename}_AfterToTSelection1.root")
    tree = file["HitsTree"]
    hits_dict = tree.arrays(library="np")
except FileNotFoundError:
    print(f"Error: File {path}/{filename}_AfterToTSelection1.root not found.")
    exit()


if __name__ == "__main__":

    # 建立空的 histogram 字典
    histograms = {'B1': [], 'B2': [],'B3': [], 'B4': [], 
                  'B5': [], 'B6': [], 'B7': [], 'B8': [], 
                  'B9': [], 'B10': [], 'B11': [], 'B12': [], 
                  'B13': [], 'B14': [], 'B15': [], 'B16': []}

    # 為每個 Board 和 Channel 建立 TH1F 物件
    for board, bid in tqdm(zip(histograms.keys(), range(1, 17)), desc='Building Histograms', total=len(histograms)):
        for channel in range(0, 16):
            amplitudes = hits_dict['Amplitude'][(hits_dict['BoardID'] == bid) & (hits_dict['ChannelID'] == channel)]


            pwidths = hits_dict['PWidth'][(hits_dict['BoardID'] == bid) & (hits_dict['ChannelID'] == channel)]
            np.save(f'./pwidhArray{board}_Ch{channel}.npy', pwidths)
            quit()


            edges = np.concatenate([
                np.arange(0, 100, 10),      # 0-500 之間 5 為一格
                np.arange(100, 200,15),
                np.arange(200, 300,20),    
                np.arange(300, 600,50),
            ])
            xbins = array('d', edges)       # 轉成 ROOT 吃的 double array
            n_bins = len(xbins) - 1         # 計算 bin 數量

            hist = ROOT.TH1F(f"{board}_Ch{channel}_Amps", 
                 f"{board} Channel {channel} Amps Distribution;Amps;Counts", 
                 n_bins, xbins)

            hist.Sumw2()

            hist.FillN(len(amplitudes), amplitudes.astype(np.float64), np.ones(len(amplitudes), dtype=np.float64))
            hist.Scale(1.0, "width") # 除以binwidth
            histograms[board].append(hist)

    pythonic_Pad_mapping = [13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4]
    
    # 開啟 PDF
    dummy_canvas = ROOT.TCanvas("dummy_canvas", "Dummy Canvas", 4000, 4000 )
    dummy_canvas.Print(output_pdf_name + "[")
    dummy_canvas.Close()


    """擬合與繪圖"""
    TOT_all = []
    GSigma_all = []
    redchisq_all = []
    
    # 設定隨機嘗試次數
    N_RANDOM_TRIALS = 20

    for board, hists in tqdm(histograms.items(), desc="Plotting Boards"):
        canvas = ROOT.TCanvas(f"{board}_ToT", f"{board} ToT", 4000, 4000)
        canvas.Divide(4, 4)  # 4x4 網格

        for i, hist in enumerate(hists):       
            canvas.cd(pythonic_Pad_mapping[i]) 
            
            # # --- 尋找峰值與半高寬範圍 ---
            # left_half_max = None
            # right_half_max = None
            # max_bin_index = hist.GetMaximumBin()
            # max_content = hist.GetBinContent(max_bin_index)
            # half_max = max_content * 0.3 # 這裡設為 0.3 倍高
            
            # # 向左尋找
            # for bin_idx in range(max_bin_index, 0, -1):
            #     if hist.GetBinContent(bin_idx) <= half_max:
            #         left_half_max = hist.GetXaxis().GetBinCenter(bin_idx)
            #         break
            # # 向右尋找
            # for bin_idx in range(max_bin_index, hist.GetNbinsX() + 1):
            #     if hist.GetBinContent(bin_idx) <= half_max:
            #         right_half_max = hist.GetXaxis().GetBinCenter(bin_idx)
            #         break
            
            # if left_half_max is None or right_half_max is None:
            #     print(f"Warning: Could not find half max points for {board} Channel {i}. Skipping fit.")
            #     hist.Draw()
            #     continue
            
            # === 修改開始：使用平滑直方圖來尋找範圍 ===
            
            # 1. 複製一個暫時的直方圖用於尋找範圍
            h_temp = hist.Clone(f"temp_{board}_{i}")
            
            # 2. 對暫時直方圖進行平滑化 (Smooth)
            # 參數 1 代表平滑次數，如果雜訊很大可以設為 2 或 3
            # 平滑後雜訊坑洞會被填平，不會誤判邊界
            h_temp.Smooth(1) 

            # 3. 在平滑後的直方圖上尋找最大值與 0.3 倍高
            max_bin_index = h_temp.GetMaximumBin()
            max_content = h_temp.GetBinContent(max_bin_index)
            max_x_center = h_temp.GetXaxis().GetBinCenter(max_bin_index)
            half_max = max_content * 0.4
            
            left_half_max = None
            right_half_max = None
            # 4. 向左尋找 (使用平滑過的 h_temp)
            for bin_idx in range(max_bin_index, 0, -1):
                if h_temp.GetBinContent(bin_idx) <= half_max:
                    left_half_max = h_temp.GetXaxis().GetBinCenter(bin_idx)
                    break  
            # 5. 向右尋找 (使用平滑過的 h_temp)
            for bin_idx in range(max_bin_index, h_temp.GetNbinsX() + 1):
                if h_temp.GetBinContent(bin_idx) <= half_max:
                    right_half_max = h_temp.GetXaxis().GetBinCenter(bin_idx)
                    break
            # 6. 刪除暫時物件釋放記憶體
            del h_temp
            # 檢查是否找到
            if left_half_max is None: left_half_max = hist.GetXaxis().GetXmin()
            if right_half_max is None: right_half_max = hist.GetXaxis().GetXmax()


            # --- 設定擬合範圍 (Fit Range) ---
            # 修改：使用動態計算的範圍，並稍微向右延伸包含 Landau 尾部
            # fr = array('d', [left_half_max, right_half_max])
            
            # 動態邊界: 左邊為峰值發生處-50，右邊延伸 300 單位
            fr = array('d', [max_x_center - 45.0, max_x_center + 300.0])
            
            # --- 設定參數初始值與限制 ---
            max_x_center = hist.GetXaxis().GetBinCenter(max_bin_index)
            area_guess = hist.Integral("width")

            # 參數限制: Width, MP, Area, GSigma
            # pllo = array('d', [15.0, max_x_center - 5.0, area_guess * 0.1, 8.0])
            # plhi = array('d', [40.0, max_x_center + 5.0, area_guess * 5.0, 12.0])

            pllo = array('d', [15.0, 170, area_guess * 0.1, 8.0])
            plhi = array('d', [40.0, 190, area_guess * 5.0, 12.0])
            
            # 確保下限不為負 (物理上 Width, Area, GSigma > 0)
            if pllo[1] < 0: pllo[1] = 0
            
            # 預設的初始值 (Fallback)
            sv = array('d', [30.0, max_x_center, area_guess, 20.0])

            # ==========================================
            #   隨機擬合核心 (Randomized Fitting Loop)
            # ==========================================
            best_redchisq = float('inf')
            best_sv = array('d', [sv[0], sv[1], sv[2], sv[3]])

            # 暫存擬合結果的容器
            tmp_fp = array('d', [0.0]*4)
            tmp_fpe = array('d', [0.0]*4)
            tmp_chisqr = array('d', [0.0])
            tmp_ndf = array('i', [0])

            for trial in range(N_RANDOM_TRIALS):
                # 在參數限制範圍內隨機生成初始值
                rnd_width = np.random.uniform(pllo[0], plhi[0])
                rnd_mp    = np.random.uniform(pllo[1], plhi[1])
                rnd_area  = np.random.uniform(pllo[2], plhi[2])
                rnd_gsigma= np.random.uniform(pllo[3], plhi[3])
                
                trial_sv = array('d', [rnd_width, rnd_mp, rnd_area, rnd_gsigma])

                try:
                    # 執行擬合 (不畫圖 "N", 安靜 "Q", 不更新統計 "0")
                    ROOT.langaufit(hist, fr, trial_sv, pllo, plhi, tmp_fp, tmp_fpe, tmp_chisqr, tmp_ndf)
                    
                    if tmp_ndf[0] > 0:
                        current_redchisq = tmp_chisqr[0] / tmp_ndf[0]
                    else:
                        current_redchisq = float('inf')

                    # 判斷是否為更好的結果 (ChiSq 更小 且 擬合成功)
                    if current_redchisq < best_redchisq and current_redchisq > 1e-5:
                        best_redchisq = current_redchisq
                        # 複製最佳初始值
                        best_sv = array('d', list(trial_sv)) # 使用 list 強制複製值
                except Exception:
                    continue 

            # ==========================================
            #   最終擬合 (Final Fit with Best SV)
            # ==========================================
            print(f"{board} Ch{i}: Best RedChiSq found: {best_redchisq:.2f}")

            # 用於接收最終結果的 Array
            fp = array('d', [0.0]*4)
            fpe = array('d', [0.0]*4)
            chisqr = array('d', [0.0])
            ndf = array('i', [0])

            # 使用找到的最佳初始值進行最後一次擬合，這次會畫在圖上
            fit_func = ROOT.langaufit(hist, fr, best_sv, pllo, plhi, fp, fpe, chisqr, ndf)
            
            # 收集數據
            TOT_all.append(fp[1]) # MP Value
            GSigma_all.append(fp[3])
            redchisq = chisqr[0] / ndf[0] if ndf[0] != 0 else 0
            redchisq_all.append(redchisq)

            # --- 繪圖設定 ---
            hist.GetXaxis().SetLabelSize(0.06)
            hist.GetXaxis().SetTitleSize(0.06)
            hist.GetXaxis().SetTitle("Amplitude") # 修改為 Amplitude
            hist.GetXaxis().SetNdivisions(505)

            hist.GetYaxis().SetLabelSize(0.06)
            hist.GetYaxis().SetTitleSize(0.06)
            hist.SetLineColor(ROOT.kBlack)
            # hist.Draw()
            hist.Draw('HIST')
            
            # 根據擬合好壞設定顏色
            if redchisq > 5.0 :
                fit_func.SetLineColor(ROOT.kRed)
            elif redchisq < 0.5:
                fit_func.SetLineColor(ROOT.kGreen)
            else:
                fit_func.SetLineColor(ROOT.kBlue)

            fit_func.SetLineWidth(1)
            fit_func.Draw("lsame")
            ROOT.gPad.Update()
            
            # 修改標題屬性
            pt = ROOT.gPad.GetPrimitive("title")
            if pt:
                pt.SetTextSize(0.05)   
                pt.SetTextAlign(23)    
                pt.SetX1NDC(0.25)
                pt.SetX2NDC(0.9)
                pt.SetY1NDC(0.90)
                pt.SetY2NDC(0.98)
                pt.SetBorderSize(0)
                pt.SetFillColor(0)
                pt.SetFillStyle(0)
                ROOT.gPad.Modified()

        canvas.Print(output_pdf_name)
        canvas.Close()

    # --- 總結圖表 (Summary Plots) ---
    
    # 1. MP (Amplitude) 分佈
    TOT_all = np.array(TOT_all)
    mean_TOT = np.mean(TOT_all)
    std_TOT = np.std(TOT_all)
    print(f"Overall Amplitude Mean: {mean_TOT:.2f}, Std Deviation: {std_TOT:.2f}")
    
    # 動態設定 Histogram 範圍
    max_val = np.max(TOT_all) if len(TOT_all) > 0 else 100
    TOT_hist = ROOT.TH1F("Overall_MP", "Overall Amplitude MP Distribution;Amplitude;Counts", int(max_val*1.1), 0, max_val*1.1)
    
    n_tot = len(TOT_all)
    if n_tot > 0:
        TOT_hist.FillN(n_tot, TOT_all.astype(np.float64), np.ones(n_tot, dtype=np.float64))
    
    TOT_canvas = ROOT.TCanvas("Overall_MP_Canvas", "Overall MP", 1200, 800)
    ROOT.gStyle.SetOptStat(1111)
    TOT_hist.Draw()
    TOT_canvas.Print(output_pdf_name)
    TOT_canvas.Close()

    # 2. GSigma 分佈
    GSigma_all = np.array(GSigma_all)
    mean_GSigma = np.mean(GSigma_all)
    std_GSigma = np.std(GSigma_all)
    print(f"Overall GSigma Mean: {mean_GSigma:.2f}, Std Deviation: {std_GSigma:.2f}")
    
    max_sigma = np.max(GSigma_all) if len(GSigma_all) > 0 else 50
    GSigma_hist = ROOT.TH1F("Overall_GSigma", "Overall GSigma Distribution;GSigma;Counts", 100, 0, int(max_sigma*1.2))
    
    n_gsigma = len(GSigma_all)
    if n_gsigma > 0:
        GSigma_hist.FillN(n_gsigma, GSigma_all.astype(np.float64), np.ones(n_gsigma, dtype=np.float64))
    
    GSigma_canvas = ROOT.TCanvas("Overall_GSigma_Canvas", "Overall GSigma", 1200, 800)
    GSigma_hist.Draw()
    GSigma_canvas.Print(output_pdf_name)
    GSigma_canvas.Close()

    # 3. RedChiSq 分佈
    redchisq_all = np.array(redchisq_all)
    max_chi = np.max(redchisq_all) if len(redchisq_all) > 0 else 10
    redchisq_hist = ROOT.TH1F("Overall_RedChiSq", "Overall RedChiSq Distribution;RedChiSq;Counts", 50, 0, int(max_chi*1.2)+1)
    
    n_redchisq = len(redchisq_all)
    if n_redchisq > 0:
        redchisq_hist.FillN(n_redchisq, redchisq_all.astype(np.float64), np.ones(n_redchisq, dtype=np.float64))
    
    redchisq_canvas = ROOT.TCanvas("Overall_RedChiSq_Canvas", "Overall RedChiSq", 1200, 800)
    redchisq_hist.Draw()
    redchisq_canvas.Print(output_pdf_name)
    redchisq_canvas.Close()

    # 關閉 PDF
    dummy_canvas = ROOT.TCanvas()
    dummy_canvas.Print(output_pdf_name + "]")
    dummy_canvas.Close()

    print("Pwidth distribution histograms (Random Fit) have been generated and saved.")
