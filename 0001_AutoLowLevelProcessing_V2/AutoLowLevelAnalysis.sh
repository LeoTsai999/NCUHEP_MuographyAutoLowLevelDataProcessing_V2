#!/bin/bash

# Exit immediately if a command exits with a non-zero status
# (Prevents sending a success email if the analysis fails midway)
set -e

THE_DATE=$(date -d "yesterday" +%Y%m%d)
echo "========================================="
echo "Auto Low-Level Analysis ${THE_DATE}"
echo "========================================="

# 1. Set Run Number/ID
USER_INPUT="Det01_Exp0001_Run000005_001_Mu"

# Automatically move HK and UDP log files to the appropriate directory
echo "Moving HK and UDP log files to the appropriate directory..."
bash /data9/YangMingShanExperiments/YangMingHotspotResort/RawData/MoveFiles.sh


# 2. Automatically get yesterday's date (Format: YYYYMMDD)
# For Linux systems, use -d "yesterday"
# If you are using macOS, please use: TARGET_DATE=$(date -v-1d +%Y%m%d)
TARGET_DATE=$(date -d "yesterday" +%Y%m%d)

# Combine the final argument (Date_InputString)
FULL_ARGUMENT="${TARGET_DATE}_${USER_INPUT}"

echo "========================================="
echo "Starting Analysis Task"
echo "Target Date: $TARGET_DATE"
echo "Full Argument: $FULL_ARGUMENT"
echo "========================================="

# 3. Execute Python scripts sequentially
# Pass ${FULL_ARGUMENT} as the argument

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/conda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
        . "/opt/conda/etc/profile.d/conda.sh"
    else
        export PATH="/opt/conda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
conda activate data_analysis

echo "[1/5] Executing 001_HitsProcessing.py ..."
python3 /data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/001_HitsProcessing.py "$FULL_ARGUMENT"

echo "[2/5] Executing 002_EventSelection.py ..."
python3 /data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/002_EventSelection.py "$FULL_ARGUMENT"

echo "[3/5] Executing 003_1_HitLevel.py ..."
python3 /data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/003_1_HitLevel.py "$FULL_ARGUMENT"

echo "[4/5] Executing 003_2_PwidthDistribution.py ..."
python3 /data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/003_2_PwidthDistribution.py "$FULL_ARGUMENT"

echo "[5/5] Executing 003_3TempOverDay.py ..."
python3 /data9/YangMingShanExperiments/YangMingHotspotResort/Programs/0001_AutoLowLevelProcessing/003_3TempOverDay.py "$FULL_ARGUMENT"


# 4. Send Email Notification with Image
python3 <<EOF
import smtplib
import os
from email.mime.multipart import MIMEMultipart # 用來建立多部分郵件（文字+附件）
from email.mime.text import MIMEText
from email.mime.image import MIMEImage # 用來處理圖片
from email.header import Header
from email.mime.application import MIMEApplication

# ================= 設定區 =================
smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender = 'muography@phy.ncu.edu.tw'
password = 'gacw kzqj nmst qdli'  # 注意：請確保此密碼安全，不要公開
receiver = 'muography@phy.ncu.edu.tw'
PNG_HitLevelPath = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots/${FULL_ARGUMENT}_HitLevelCombined4Layers.png'
PDF_PwidthDistPath = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots/${FULL_ARGUMENT}_TOT.pdf'
PNG_TempOverDayPath = '/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots/${FULL_ARGUMENT}_TempOverDay.png'
# =========================================


# 建立 MIMEMultipart 物件（這是一個容器）
msg = MIMEMultipart()
msg['Subject'] = Header('Daily Auto LowLevel Analysis Report', 'utf-8')
msg['From'] = sender
msg['To'] = receiver

# 1. 加入郵件內文 (Body)
body_content = 'Today\'s auto low-level analysis is complete!\nThese two plots are ${FULL_ARGUMENT}\nPlease check the attached plot.'
msg.attach(MIMEText(body_content, 'plain', 'utf-8'))

# 2. 加入圖片附件 (HitLevel)
# 檢查檔案是否存在，避免程式崩潰
if os.path.exists(PNG_HitLevelPath):
    try:
        with open(PNG_HitLevelPath, 'rb') as f:
            # 讀取圖片檔案
            img_data = f.read()
            # 建立 MIMEImage 物件
            image = MIMEImage(img_data)
            # 設定附件檔名 (讓收件人看到正確的檔名)
            image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(PNG_HitLevelPath))
            # 將圖片附加上去
            msg.attach(image)
    except Exception as e:
        print(f'讀取圖片失敗: {e}')
else:
    print(f'警告: 找不到圖片檔案 {PNG_HitLevelPath}，將只發送文字郵件。')
# 2. 加入 PDF 附件 (Pwidth Distribution)
if os.path.exists(PDF_PwidthDistPath):
    try:
        with open(PDF_PwidthDistPath, 'rb') as f:
            # 讀取 PDF 檔案
            pdf_data = f.read()
            # 建立 MIMEApplication 物件，並指定子類型為 pdf
            pdf_attachment = MIMEApplication(pdf_data, _subtype="pdf")
            
            # 設定附件檔名 (確保收件人下載時有正確的副檔名)
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(PDF_PwidthDistPath))
            
            # 將附件加入郵件容器
            msg.attach(pdf_attachment)
    except Exception as e:
        print(f'讀取 PDF 失敗: {e}')
else:
    print(f'警告: 找不到檔案 {PDF_PwidthDistPath}')

# 溫度紀錄圖
if os.path.exists(PNG_TempOverDayPath):
    try:
        with open(PNG_TempOverDayPath, 'rb') as f:
            # 讀取圖片檔案
            img_data = f.read()
            # 建立 MIMEImage 物件
            image = MIMEImage(img_data)
            # 設定附件檔名 (讓收件人看到正確的檔名)
            image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(PNG_TempOverDayPath))
            # 將圖片附加上去
            msg.attach(image)
    except Exception as e:
        print(f'讀取圖片失敗: {e}')
else:
    print(f'警告: 找不到圖片檔案 {PNG_TempOverDayPath}，將只發送文字郵件。')


# 3. 寄出郵件
try:
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, password)
    
    smtp.send_message(msg)
    print('包含圖片的郵件傳送成功！')
    
    smtp.quit()
except Exception as e:
    print(f'郵件傳送失敗: {e}')
EOF
echo "========================================="
echo "Task fully completed. Notification sent."
echo "========================================="