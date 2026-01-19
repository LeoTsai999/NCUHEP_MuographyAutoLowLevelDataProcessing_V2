import uproot
import numpy as np
import ROOT
from tqdm import tqdm, trange
import array
import sys
import os
import time
import datetime
import awkward as ak

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

if __name__ == "__main__":
    print("Starting Pwidth Distribution Plotting...")

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
    ROOT.gStyle.SetPalette(ROOT.kCool) # 設定顏色主題 https://root.cern.ch/doc/v636/classTColor.html
    # 子圖邊距
    ROOT.gStyle.SetPadLeftMargin(0.20)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPadTopMargin(0.125)
    ROOT.gStyle.SetPadBottomMargin(0.125)

    # import C++ 函數們
    macro_path = "/data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/langaus2.C"
    if os.path.exists(macro_path):
        ROOT.gInterpreter.LoadMacro(f"{macro_path}")
    else:
        print(f"Error: {macro_path} not found!")
        exit()
    
    # 1. 設定 Minimizer(例如 "Minuit2", "Minuit", "GSLMultiMin")
    # 2. 設定演算法 ("Migrad", "Simplex", "Combined")
    ROOT.Math.MinimizerOptions.SetDefaultMinimizer("Minuit2", "Combined")

    # 其他常用的調整參數
    ROOT.Math.MinimizerOptions.SetDefaultMaxFunctionCalls(1000000) # 增加最大迭代次數
    ROOT.Math.MinimizerOptions.SetDefaultTolerance(0.01)           # 設定收斂容許度
    ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(1)             # 設定輸出多少 (0=靜默, 1=正常, 2=詳細)

    """ 列印 Minimizer 設定參數 """
    ROOT.Math.MinimizerOptions.PrintDefault()


    """ 設定參數 """
    # 讀取檔案
    # filename = "20251215_Det01_Exp0001_Run000004_001_Mu"
    filename = sys.argv[1]  # <- 讀取第一個參數

    # filename2 = sys.argv[2]  # <- 讀取第二個參數
    # filename3 = sys.argv[3]  # <- 讀取第三個參數
    # filename4 = sys.argv[4]  # <- 讀取第四個參數
    # filename5 = sys.argv[5]  # <- 讀取第五個參數
    # filename6 = sys.argv[6]  # <- 讀取第六個參數
    # filename7 = sys.argv[7]  # <- 讀取第七個參數
    # filename8 = sys.argv[8]  # <- 讀取第八個參數
    # filename9 = sys.argv[9]  # <- 讀取第九個參數
    # filename10 = sys.argv[10]  # <- 讀取第十個參數


    path = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData'
    # 儲存圖片路徑
    output_path = f"/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots"
    output_pdf_name = f"{output_path}/{filename}_TOT_TEST.pdf"

    """"""
    try:
        file = uproot.open(f"{path}/{filename}_AfterTOTSelection.root")
        tree = file["DataTree"]
        ak_array = tree.arrays(library="ak")
        event_dict = {field: ak_array[field] for field in ak_array.fields}
        hits_dict = FlattenEventsToHits(ak_array)
    except FileNotFoundError:
        print(f"Error: File {path}/{filename}_AfterTOTSelection.root not found.")
        exit()

    # # 臨時用: 合併多個檔案的 hits_dict
    # for fn in [filename2, filename3, filename4, filename5, filename6, filename7, filename8, filename9, filename10]:
    #     try:
    #         file_tmp = uproot.open(f"{path}/{fn}_AfterToTSelection.root")
    #         tree_tmp = file_tmp["DataTree"]
    #         hits_dict_tmp = tree_tmp.arrays(library="np")
    #         for key in hits_dict:
    #             hits_dict[key] = np.concatenate((hits_dict[key], hits_dict_tmp[key]))
    #     except FileNotFoundError:
    #         print(f"Warning: File {path}/{fn}_AfterToTSelection.root not found. Skipping this file.")

    histograms = {'B1': [],
                'B2': [],
                'B3': [],
                'B4': [],
                'B5': [],
                'B6': [],
                'B7': [],
                'B8': [],
                'B9': [],
                'B10': [],
                'B11': [],
                'B12': [],
                'B13': [],
                'B14': [],
                'B15': [],
                'B16': []}
    
    histograms_pwidth = {'B1': [], 'B2': [], 'B3': [], 'B4': [], 'B5': [], 'B6': [], 'B7': [], 'B8': [], 'B9': [], 'B10': [], 'B11': [], 'B12': [], 'B13': [], 'B14': [], 'B15': [], 'B16': []}


    for board, bid in tqdm(zip(histograms.keys(), range(1, 17)), desc='Building Histograms', total=len(histograms)):

        for channel in range(0, 16):

            # amplitudes = hits_dict['Amplitude'][(hits_dict['BoardID'] == bid) & (hits_dict['ChannelID'] == channel)]
            pwidths = hits_dict['PWidth'][(hits_dict['BoardID'] == bid) & (hits_dict['ChannelID'] == channel)]
          
            # hist = ROOT.TH1F(f"{board}_Ch{channel}_PWidth", f"{board} Channel {channel} PWidth Distribution;PWidth;Counts", 50, 0, 100)
            hist = ROOT.TH1F(f"{board}_Ch{channel}_PWidth", f"{board} Channel {channel} PWidth Distribution;PWidth;Counts", 60, 0, 60)
            hist.Sumw2()

            hist.FillN(len(pwidths), pwidths.astype(np.float64), np.ones(len(pwidths), dtype=np.float64))   
           
            histograms[board].append(hist)

    pythonic_Pad_mapping = [13, 14, 15, 16, 9, 10, 11, 12, 5, 6, 7, 8, 1, 2, 3, 4]

    dummy_canvas = ROOT.TCanvas("dummy_canvas", "Dummy Canvas", 4000, 4000 )
    dummy_canvas.Print(output_pdf_name + "[")
    dummy_canvas.Close()

    TOT_all=[]
    GSigma_all=[]
    redchisq_all=[]
    difference_all=[]
    for board, hists in tqdm(histograms.items(), desc="Plotting Boards"):
        canvas = ROOT.TCanvas(f"{board}_ToT", f"{board} ToT", 4000, 4000)
        canvas.Divide(4, 4)  # 4x4 網格

        for i, hist in enumerate(hists):       # hists 裡面有 16 個 histogram, 代表CH0~CH15。每個CH都是一個hist, 為TH1F物件
            canvas.cd(pythonic_Pad_mapping[i]) # 切換到指定子圖 用pythonic mapping(ROOT左上角是1 右下角是16)
            
            # 尋找0.4倍高寬點
            left_half_max = None
            right_half_max = None
            max_bin_index = hist.GetMaximumBin()
            max_content = hist.GetBinContent(max_bin_index)
            half_max = max_content * 0.4
            # 向左尋找
            for bin_idx in range(max_bin_index, 0, -1):
                if hist.GetBinContent(bin_idx) <= half_max:
                    left_half_max = hist.GetXaxis().GetBinCenter(bin_idx)
                    break
            # 向右尋找
            for bin_idx in range(max_bin_index, hist.GetNbinsX() + 1):
                if hist.GetBinContent(bin_idx) <= half_max:
                    right_half_max = hist.GetXaxis().GetBinCenter(bin_idx)
                    break
            if left_half_max is None or right_half_max is None:
                print(f"Warning: Could not find half max points for {board} Channel {i}. Skipping fit.")
                hist.Draw()
                continue

            # Fit Range
            # fr = array.array('d', [left_half_max, right_half_max])
            fr = array.array('d', [left_half_max, right_half_max])
            # Start Values (sv): Width, MP, Area, GSigma
            # 找到最大值位置作為MP初始值
            max_bin_index = hist.GetMaximumBin()
            max_content = hist.GetBinContent(max_bin_index)
            max_x_center = hist.GetXaxis().GetBinCenter(max_bin_index)

            # 面積作為Area初始值
            area_guess = hist.Integral()

            sv = array.array('d', [20.0, max_x_center, area_guess, 7.5]) 
            
            # Parameter Limits (pllo, plhi)
            # Width, MP, Area, GSigma
            pllo = array.array('d', [1.0, 15.0, 1.0, 1])
            plhi = array.array('d', [100.0, 25.0, 100000.0, 5.0])
            
            # 用於接收結果的 Array
            fp = array.array('d', [0.0]*4)    # fit params
            fpe = array.array('d', [0.0]*4)   # fit errors
            chisqr = array.array('d', [0.0])  # chi square
            ndf = array.array('i', [0])       # NDF

            # 執行擬合
            fit_func = ROOT.langaufit(hist, fr, sv, pllo, plhi, fp, fpe, chisqr, ndf)
            TOT_all.append(fp[1])
            GSigma_all.append(fp[3])
            redchisq = chisqr[0] / ndf[0] if ndf[0] != 0 else 0
            redchisq_all.append(redchisq)

            hist.GetXaxis().SetLabelSize(0.06)
            hist.GetXaxis().SetTitleSize(0.06)
            hist.GetXaxis().SetTitle("PWidth(100ns)")
            hist.GetXaxis().SetNdivisions(505) # 設定 X 軸刻度數量

            hist.GetYaxis().SetLabelSize(0.06)
            hist.GetYaxis().SetTitleSize(0.06)
            hist.SetLineColor(ROOT.kBlack)
            hist.Draw()
            
            if redchisq > 5.0 :
                fit_func.SetLineColor(ROOT.kRed)
            elif redchisq < 0.5:
                fit_func.SetLineColor(ROOT.kGreen)
            else:
                fit_func.SetLineColor(ROOT.kBlue)

            fit_func.SetLineWidth(1)
            fit_func.Draw("lsame")
            # 強制更新畫面
            ROOT.gPad.Update()
            
            # 抓取標題物件
            pt = ROOT.gPad.GetPrimitive("title")
            # 修改標題屬性
            if pt:
                # === 設定對齊與大小 ===
                pt.SetTextSize(0.05)   
                pt.SetTextAlign(23)    
                
                pt.SetX1NDC(0.25)      # 左邊界
                pt.SetX2NDC(0.9)       # 右邊界
                pt.SetY1NDC(0.90)      # 方塊底部高度
                pt.SetY2NDC(0.98)      # 方塊頂部高度
                
                pt.SetBorderSize(0)    # 去除框黑線
                pt.SetFillColor(0)     # 背景透明
                pt.SetFillStyle(0)     # 透明背景樣式
                
                # 更新
                ROOT.gPad.Modified()

        canvas.Print(output_pdf_name)
        canvas.Close()

    # TOT分佈
    TOT_all = np.array(TOT_all)
    mean_TOT = np.mean(TOT_all)
    std_TOT = np.std(TOT_all)
    print(f"Overall ToT Mean: {mean_TOT:.2f}, Std Deviation: {std_TOT:.2f}")
    TOT_hist = ROOT.TH1F("Overall_ToT", "Overall ToT Distribution;ToT;Counts", int(np.max(TOT_all)*1.1), 0, np.max(TOT_all)*1.1)
    n_tot = len(TOT_all)
    if n_tot > 0:
        TOT_hist.FillN(n_tot, TOT_all.astype(np.float64), np.ones(n_tot, dtype=np.float64))
    TOT_hist.GetXaxis().SetTitle("ToT(100ns)")
    
    TOT_canvas = ROOT.TCanvas("Overall_ToT_Canvas", "Overall ToT", 1200, 800)
    # 開啟統計框
    ROOT.gStyle.SetOptStat(1111)
    TOT_hist.Draw()
    TOT_canvas.Print(output_pdf_name)
    TOT_canvas.Close()

    # GSigma 分佈
    GSigma_all = np.array(GSigma_all)
    mean_GSigma = np.mean(GSigma_all)
    std_GSigma = np.std(GSigma_all)
    print(f"Overall GSigma Mean: {mean_GSigma:.2f}, Std Deviation: {std_GSigma:.2f}")
    GSigma_hist = ROOT.TH1F("Overall_GSigma", "Overall GSigma Distribution;GSigma;Counts", 100, 0, int(np.max(GSigma_all)*1.2))
    n_gsigma = len(GSigma_all)
    if n_gsigma > 0:
        GSigma_hist.FillN(n_gsigma, GSigma_all.astype(np.float64), np.ones(n_gsigma, dtype=np.float64))
    GSigma_canvas = ROOT.TCanvas("Overall_GSigma_Canvas", "Overall GSigma", 1200, 800)
    GSigma_hist.Draw()
    GSigma_canvas.Print(output_pdf_name)
    GSigma_canvas.Close()

    # RedChiSq 分佈
    redchisq_all = np.array(redchisq_all)
    redchisq_hist = ROOT.TH1F("Overall_RedChiSq", "Overall RedChiSq Distribution;RedChiSq;Counts", 50, 0, int(max(redchisq_all)*1.2)+1)
    n_redchisq = len(redchisq_all)
    if n_redchisq > 0:
        redchisq_hist.FillN(n_redchisq, redchisq_all.astype(np.float64), np.ones(n_redchisq, dtype=np.float64))
    redchisq_canvas = ROOT.TCanvas("Overall_RedChiSq_Canvas", "Overall RedChiSq", 1200, 800)
    redchisq_hist.Draw()
    redchisq_canvas.Print(output_pdf_name)
    redchisq_canvas.Close()

    dummy_canvas = ROOT.TCanvas()
    dummy_canvas.Print(output_pdf_name + "]")
    dummy_canvas.Close()

    print("Pwidth distribution histograms have been generated and saved.")
    


