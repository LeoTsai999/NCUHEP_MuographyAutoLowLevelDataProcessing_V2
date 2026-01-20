import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

file_name = sys.argv[1]
# file_name = '20251214_Det01_Exp0001_Run000004_001'

# 拿掉字串中的_Mu
s = file_name.replace('_Mu', '')
file_name = s

df = pd.read_csv(f'/data9/YangMingShanExperiments/YangMingHotspotResort/RawData/HK/{file_name}_HK.txt', sep='\t')

tmp100_temp0 = df.iloc[:, 9].to_numpy()
tmp100_temp1 = df.iloc[:, 10].to_numpy()
tmp100_temp2 = df.iloc[:, 11].to_numpy()
tmp100_temp3 = df.iloc[:, 12].to_numpy()
PCNT = df.iloc[:, 3].to_numpy()
BoardID = df.iloc[:, 1].to_numpy()

temp_min = np.min([tmp100_temp0, tmp100_temp1, tmp100_temp2, tmp100_temp3])
temp_max = np.max([tmp100_temp0, tmp100_temp1, tmp100_temp2, tmp100_temp3])

fig, axes = plt.subplots(4, 4, figsize=(25, 25))
for board in range(1, 17):
    
    tmp100_temp0 = df.iloc[:, 9].to_numpy()
    tmp100_temp1 = df.iloc[:, 10].to_numpy()
    tmp100_temp2 = df.iloc[:, 11].to_numpy()
    tmp100_temp3 = df.iloc[:, 12].to_numpy()
    PCNT = df.iloc[:, 3].to_numpy()
    BoardID = df.iloc[:, 1].to_numpy()

    mask = (BoardID == board)
    PCNT = PCNT[mask]
    tmp100_temp0 = tmp100_temp0[mask]
    tmp100_temp1 = tmp100_temp1[mask]
    tmp100_temp2 = tmp100_temp2[mask]
    tmp100_temp3 = tmp100_temp3[mask]

    temp_avg = (tmp100_temp0 + tmp100_temp1 + tmp100_temp2 + tmp100_temp3) / 4.0
    temp_err = np.std([tmp100_temp0, tmp100_temp1, tmp100_temp2, tmp100_temp3], axis=0)

    PCNT = PCNT - PCNT[0]  # Normalize PCNT to the first value
    PCNT = PCNT / (60* 60)  # Convert to hours

    time_mask = (PCNT >= 0) & (PCNT <= 24)

    PCNT = PCNT[time_mask]
    temp_avg = temp_avg[time_mask]
    temp_err = temp_err[time_mask]

    ax = axes[(board-1)//4, (board-1)%4]
    ax.errorbar(PCNT, temp_avg, yerr=temp_err, fmt='.', label=f'B{board}', color='red', ecolor='gray', elinewidth=1, capsize=2)
    # ax.axhline(35, color='r', linestyle='--', label='35 degree C')
    # ax.axhline(25, color='orange', linestyle='--', label='25 degree C')
    ax.set_ylabel('Temperature (degree C)')
    ax.set_xlabel('Time (hours)')
    ax.set_ylim(temp_min-2, temp_max+2)
    ax.set_yticks(np.arange(int(temp_min-2), int(temp_max+3), 1))
    ax.set_title(f'B{board}')
    ax.legend(fontsize=12)
    ax.grid()
    

plt.subplots_adjust(hspace=0.25, wspace=0.25)
print('Saving figure...')
plt.savefig(f'/data9/YangMingShanExperiments/YangMingHotspotResort/LowLevelProcessedData/DailyPlots/{file_name}_Mu_TempOverDay.png')
plt.clf()
        



        
        

            


 