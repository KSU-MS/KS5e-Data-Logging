# library
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import datetime
import tkinter as tk
from tkinter import filedialog
from folder_selection_utils import select_file_and_get_path
# set start and ends for trimming the DF
# trim point where no change or bad values, etc.
DF_TRIM_START=20000
DF_TRIM_END=230000

filename='temps_real_interpolated'
new_df=pd.read_csv(filename+'.csv')

# can also trim to short range to test
new_df = new_df.truncate(before=DF_TRIM_START,after=DF_TRIM_END)

def append_strings(item):
    return 'cell' + str(item) + 'temp'

def print_dataframe(df):
    for index, row in df.iterrows():
        print(f"Index: {index}")
        for col_name, value in row.items():
            print(f"  {col_name}: {value}")
        print("\n")


def print_dataframe_arrays(df):
    for index, row in df.iterrows():
        # print(row)
        print(f"[",end="")
        for col_name, value in row.items():
            print(f"df.at[row,'{value}'],",end="")
        print("],",end="")

name_df = pd.read_csv("cellarraycsv.csv")
# made array in excel that has cell # in index i desire for the heat map
# then print each value in appropriate index to get the format below, for "get_array_for_row"
df_modified=name_df.applymap(append_strings)

def get_array_for_row(df,row):
    return np.array([[df.at[row,'cell67temp'],df.at[row,'cell66temp'],df.at[row,'cell55temp'],df.at[row,'cell54temp'],df.at[row,'cell43temp'],df.at[row,'cell42temp'],df.at[row,'cell31temp'],df.at[row,'cell30temp'],df.at[row,'cell19temp'],df.at[row,'cell18temp'],df.at[row,'cell7temp'],df.at[row,'cell6temp']],
                     [df.at[row,'cell68temp'],df.at[row,'cell65temp'],df.at[row,'cell56temp'],df.at[row,'cell53temp'],df.at[row,'cell44temp'],df.at[row,'cell41temp'],df.at[row,'cell32temp'],df.at[row,'cell29temp'],df.at[row,'cell20temp'],df.at[row,'cell17temp'],df.at[row,'cell8temp'],df.at[row,'cell5temp']],
                     [df.at[row,'cell69temp'],df.at[row,'cell64temp'],df.at[row,'cell57temp'],df.at[row,'cell52temp'],df.at[row,'cell45temp'],df.at[row,'cell40temp'],df.at[row,'cell33temp'],df.at[row,'cell28temp'],df.at[row,'cell21temp'],df.at[row,'cell16temp'],df.at[row,'cell9temp'],df.at[row,'cell4temp']],
                     [df.at[row,'cell70temp'],df.at[row,'cell63temp'],df.at[row,'cell58temp'],df.at[row,'cell51temp'],df.at[row,'cell46temp'],df.at[row,'cell39temp'],df.at[row,'cell34temp'],df.at[row,'cell27temp'],df.at[row,'cell22temp'],df.at[row,'cell15temp'],df.at[row,'cell10temp'],df.at[row,'cell3temp']],
                     [df.at[row,'cell71temp'],df.at[row,'cell62temp'],df.at[row,'cell59temp'],df.at[row,'cell50temp'],df.at[row,'cell47temp'],df.at[row,'cell38temp'],df.at[row,'cell35temp'],df.at[row,'cell26temp'],df.at[row,'cell23temp'],df.at[row,'cell14temp'],df.at[row,'cell11temp'],df.at[row,'cell2temp']],
                     [df.at[row,'cell72temp'],df.at[row,'cell61temp'],df.at[row,'cell60temp'],df.at[row,'cell49temp'],df.at[row,'cell48temp'],df.at[row,'cell37temp'],df.at[row,'cell36temp'],df.at[row,'cell25temp'],df.at[row,'cell24temp'],df.at[row,'cell13temp'],df.at[row,'cell12temp'],df.at[row,'cell1temp']]])

cell_temp_array_list = []

for index, row in new_df.iterrows():
    new_array=get_array_for_row(new_df,index)
    cell_temp_array_list.append(pd.DataFrame(new_array,columns=["12","11","10","9","8","7","6","5","4","3","2","1"]))

# plotting stuff starts here
RENDER_SKIP_SPEED=1000
fig = plt.figure(figsize=(13,7))
ax=fig.add_subplot(2,4,(1,4))
ax1=fig.add_subplot(2,4,(5,6))
ax2=fig.add_subplot(2,4,(7,8))

ax1_1=ax1.twinx()
ax2_2=ax2.twinx()

cmap="coolwarm" # this changes the color of the map
linewidths=1
linecolor='black'
center=35
new_df["timeSecs"]=new_df["Time"]/1000

col = "Pack_Summed_Voltage"
max_x = new_df.loc[new_df[col].idxmax()]
print(max_x)
max_v = (max_x["Pack_Summed_Voltage"])
new_df["Pack_Current"]=new_df["Pack_Current"].rolling(100).mean()
new_df["Pack_Summed_Voltage"]=new_df["Pack_Summed_Voltage"].rolling(100).mean()
new_df["pack_ir"]=round(1000*((max_v - new_df['Pack_Summed_Voltage'])/new_df['Pack_Current']),4)
new_df["pack_ir"]=new_df['pack_ir'].rolling(100).mean()
new_df["heat_power"] = new_df['pack_ir']*((new_df['Pack_Current'].rolling(100).mean())**2)

def init():
    s=sns.heatmap(np.zeros((6, 12)),annot=True,fmt=".1f",vmin=10,vmax=80,
                  square=True,ax=ax,cbar=False,cmap=cmap,
                  linewidths=linewidths,linecolor=linecolor,
                  center=center)
    ax.set_title("Pack Cells Heat Map")
    ax1.set_title("Battery Pack Current")
    ax1.set_xlabel("Time:      Current:     ")
    ax1.set_ylabel("Current (Amps)")
    ax1.plot(new_df["timeSecs"],new_df["Pack_Current"],color='tomato',label="PackI")

    ax1_1.plot(new_df['timeSecs'],new_df["Pack_Summed_Voltage"],color='mediumpurple',label="PackV")
    ax1_1.set_ylabel("Pack Voltage")
    ax1.legend()
    ax1_1.legend()

    ax2.plot(new_df['timeSecs'],new_df['pack_ir'],color='teal',label="ir")
    ax2.set_ylim([0,800])
    ax2.set_ylabel("Pack IR (mOhms)")
    
    ax2_2.plot(new_df['timeSecs'],new_df['heat_power'],color='darkgoldenrod',label='heat')
    ax2_2.set_ylabel("Estimated Pack Heat Power")
    ax2.set_xlabel("IR:      Power:     ")
    ax2.legend()
    ax2_2.legend()
    line = ax1.axvline(x=(new_df.at[(DF_TRIM_START),"timeSecs"]),linestyle='-.',color='black')
    line = ax2.axvline(x=(new_df.at[(DF_TRIM_START),"timeSecs"]),linestyle='-.',color='black')
    fig.tight_layout()


def animate(i):
    data = cell_temp_array_list[i*RENDER_SKIP_SPEED]
    # print(data)
    ax.cla()
    s=sns.heatmap(data,annot=data,fmt=".1f",vmin=10,vmax=80,
                  square=True,ax=ax,cbar=False,cmap=cmap,
                  linewidths=linewidths,linecolor=linecolor,
                  center=center)
    timestamp=str(datetime.datetime.fromtimestamp((new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),"Time"])//1000))
    current=str(round(new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),"Pack_Current"],1))
    # print(timestamp)
    ax1.set_xlabel("Time: " + timestamp+" Current: " + current+"A")
    try:
        ax1.lines[1].remove()
    except:
        print(ax1.lines)
        pass
    line = ax1.axvline(x=(new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),"timeSecs"]),linestyle='-.',color='black')
    ir=str(round(new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),'pack_ir'],1))
    power=str(round(new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),'heat_power'],1))

    ax2.set_xlabel("IR: " + ir+"mOhms" + " Power: " + power+"W")

    try:
        ax2.lines[1].remove()
    except:
        print(ax2.lines)
        pass
    line = ax2.axvline(x=(new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),"timeSecs"]),linestyle='-.',color='black')

fig.suptitle("Battery Pack Thermal Test No Fans")
anim=animation.FuncAnimation(fig,animate,init_func=init,frames=(len(cell_temp_array_list)//RENDER_SKIP_SPEED),repeat=False,interval=1)
anim.save('heatmap'+filename+'.gif', writer='imagemagick', fps=10,dpi=100)
plt.show()