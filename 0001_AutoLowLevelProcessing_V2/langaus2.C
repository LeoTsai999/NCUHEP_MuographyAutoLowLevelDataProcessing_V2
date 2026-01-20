#include "TH1.h"
#include "TF1.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TMath.h"

// 核心卷積函數 (保持不變)
double langaufun(double *x, double *par) {
   double invsq2pi = 0.3989422804014; 
   double mpshift  = -0.22278298;       
   double np = 100.0;      
   double sc =   5.0;      
   double xx, mpc, fland, sum = 0.0, xlow, xupp, step, i;

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

// 擬合函數 (保持不變)
TF1 *langaufit(TH1F *his, double *fitrange, double *startvalues, double *parlimitslo, double *parlimitshi, double *fitparams, double *fiterrors, double *ChiSqr, int *NDF)
{
   int i;
   char FunName[100];
   sprintf(FunName,"Fitfcn_%s",his->GetName());
   TF1 *ffitold = (TF1*)gROOT->GetListOfFunctions()->FindObject(FunName);
   if (ffitold) delete ffitold;

   TF1 *ffit = new TF1(FunName,langaufun,fitrange[0],fitrange[1],4);
   ffit->SetParameters(startvalues);
   ffit->SetParNames("Width","MP","Area","GSigma");

   for (i=0; i<4; i++) {
      ffit->SetParLimits(i, parlimitslo[i], parlimitshi[i]);
   }
   his->Sumw2();
   his->Fit(FunName,"RB0");   
   ffit->GetParameters(fitparams);    
   for (i=0; i<4; i++) {
      fiterrors[i] = ffit->GetParError(i);     
   }
   ChiSqr[0] = ffit->GetChisquare();  
   NDF[0] = ffit->GetNDF();           
   return (ffit);              
}

// 峰值計算函數
// 修改：將 double &maxx 改為 double *maxx 以便於 Python 指標操作
int langaupro(double *params, double *maxx, double *FWHM) {
   double p,x,fy,fxr,fxl;
   double step;
   double l,lold;
   int i = 0;
   int MAXCALLS = 10000;

   // Search for maximum
   p = params[1] - 0.1 * params[0];
   step = 0.05 * params[0];
   lold = -2.0; l = -1.0;
   while ( (l != lold) && (i < MAXCALLS) ) {
      i++; lold = l; x = p + step;
      l = langaufun(&x,params);
      if (l < lold) step = -step/10;
      p += step;
   }
   if (i == MAXCALLS) return (-1);
   *maxx = x;  // 使用指標賦值
   fy = l/2;

   // Search for right
   p = *maxx + params[0]; step = params[0]; lold = -2.0; l = -1e300; i = 0;
   while ( (l != lold) && (i < MAXCALLS) ) {
      i++; lold = l; x = p + step;
      l = TMath::Abs(langaufun(&x,params) - fy);
      if (l > lold) step = -step/10;
      p += step;
   }
   if (i == MAXCALLS) return (-2);
   fxr = x;

   // Search for left
   p = *maxx - 0.5 * params[0]; step = -params[0]; lold = -2.0; l = -1e300; i = 0;
   while ( (l != lold) && (i < MAXCALLS) ) {
      i++; lold = l; x = p + step;
      l = TMath::Abs(langaufun(&x,params) - fy);
      if (l > lold) step = -step/10;
      p += step;
   }
   if (i == MAXCALLS) return (-3);
   fxl = x;
   *FWHM = fxr - fxl; // 使用指標賦值
   return (0);
}