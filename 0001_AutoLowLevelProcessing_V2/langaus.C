#include "TH1.h"
#include "TF1.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TMath.h"

// -------------------------------------------------------------------------
// 核心數學模型：Landau (x) Gaussian 卷積
// -------------------------------------------------------------------------
double langaufun(double *x, double *par) {
   //Fit parameters:
   //par[0]=Width (scale) parameter of Landau density
   //par[1]=Most Probable (MP, location) parameter of Landau density
   //par[2]=Total area (integral -inf to inf, normalization constant)
   //par[3]=Width (sigma) of convoluted Gaussian function

   double invsq2pi = 0.3989422804014;   // (2 pi)^(-1/2)
   double mpshift  = -0.22278298;       // Landau maximum location

   double np = 10000.0;    // convolution steps
   double sc =   5.0;      // convolution range (sigma units)

   double xx, mpc, fland, sum = 0.0;
   double xlow, xupp, step, i;

   mpc = par[1] - mpshift * par[0];

   xlow = x[0] - sc * par[3];
   xupp = x[0] + sc * par[3];
   step = (xupp-xlow) / np;

   for(i=1.0; i<=np/2; i++) {
      xx = xlow + (i-.5) * step;
      fland = TMath::Landau(xx,mpc,par[0]) / par[0];
      sum += fland * TMath::Gaus(x[0],xx,par[3]);

      xx = xupp - (i-.5) * step;
      fland = TMath::Landau(xx,mpc,par[0]) / par[0];
      sum += fland * TMath::Gaus(x[0],xx,par[3]);
   }

   return (par[2] * step * sum * invsq2pi / par[3]);
}

// -------------------------------------------------------------------------
// 擬合函數：只回傳 TF1 物件
// -------------------------------------------------------------------------
TF1 *langaufit(TH1F *his, double *fitrange, double *startvalues, double *parlimitslo, double *parlimitshi, bool perform_fit=true)
{
   // 輸入參數簡化為：直方圖、範圍、初始值、上下限
   // 不再接收 fp, fpe, ChiSqr, NDF 等輸出容器

   char FunName[100];
   sprintf(FunName,"Fitfcn_%s",his->GetName());

   // 如果已存在同名函數則刪除，避免衝突
   TF1 *ffitold = (TF1*)gROOT->GetListOfFunctions()->FindObject(FunName);
   if (ffitold) delete ffitold;

   // 建立函數物件
   TF1 *ffit = new TF1(FunName,langaufun,fitrange[0],fitrange[1],4);
   ffit->SetNpx(1000);  // 加入這行，增加取樣點數
   ffit->SetParameters(startvalues);
   ffit->SetParNames("Width","MP","Area","GSigma");

   // 設定參數限制
   for (int i=0; i<4; i++) {
      ffit->SetParLimits(i, parlimitslo[i], parlimitshi[i]);
   }

   // 執行擬合
   // "R": Use Range specified in function range
   // "B": Use built-in Predefined functions (not applicable here strictly but good practice)
   // "0": Do not plot the result automatically (we will handle plotting later)
   // "Q": Quiet mode (optional, remove Q if you want to see log)
   if (perform_fit) {
      his->Fit(FunName,"RB0QS"); 
   }

   // 注意：這裡不再提取參數填入陣列，直接回傳物件
   // 使用者應該使用 ffit->GetParameter() 等方法獲取結果

   return (ffit); 
}

// -------------------------------------------------------------------------
// 測試主程式
// -------------------------------------------------------------------------
void langaus() {
   // 1. 產生測試數據
   int data[100] = {0,0,0,0,0,0,2,6,11,18,18,55,90,141,255,323,454,563,681,
                    737,821,796,832,720,637,558,519,460,357,291,279,241,212,
                    153,164,139,106,95,91,76,80,80,59,58,51,30,49,23,35,28,23,
                    22,27,27,24,20,16,17,14,20,12,12,13,10,17,7,6,12,6,12,4,
                    9,9,10,3,4,5,2,4,1,5,5,1,7,1,6,3,3,3,4,5,4,4,2,2,7,2,4};
   TH1F *hSNR = new TH1F("snr","Signal-to-noise",400,0,400);
   for (int i=0; i<100; i++) hSNR->Fill(i,data[i]);

   printf("Fitting...\n");

   // 2. 準備設定
   double fr[2];
   double sv[4], pllo[4], plhi[4];
   
   fr[0]=0.3*hSNR->GetMean();
   fr[1]=3.0*hSNR->GetMean();

   pllo[0]=0.5; pllo[1]=5.0; pllo[2]=1.0; pllo[3]=0.4;
   plhi[0]=5.0; plhi[1]=50.0; plhi[2]=1000000.0; plhi[3]=5.0;
   sv[0]=1.8; sv[1]=20.0; sv[2]=50000.0; sv[3]=3.0;

   // 3. 呼叫擬合 (參數變少了)
   TF1 *fitsnr = langaufit(hSNR, fr, sv, pllo, plhi);

   // 4. 從 TF1 物件獲取結果 (OOP 風格)
   printf("Fitting done. Retrieving results from TF1 object:\n");
   
   double mpv      = fitsnr->GetParameter(1);       // 取得參數
   double mpv_err  = fitsnr->GetParError(1);        // 取得誤差
   double chi2     = fitsnr->GetChisquare();        // 取得卡方
   int    ndf      = fitsnr->GetNDF();              // 取得自由度
   
   // 取得物理峰值 (替代原本的 langaupro)
   // 在擬合範圍內搜尋最大值的 X 座標
   double peak_pos = fitsnr->GetMaximumX(fr[0], fr[1]); 

   printf("  Landau MPV (Parameter): %f +/- %f\n", mpv, mpv_err);
   printf("  Physical Peak (Max X):  %f\n", peak_pos);
   printf("  Chi2 / NDF:             %f / %d\n", chi2, ndf);

   // 5. 繪圖
   gStyle->SetOptStat(1111);
   gStyle->SetOptFit(111);
   hSNR->GetXaxis()->SetRange(0,70);
   hSNR->Draw();
   fitsnr->Draw("lsame");
}