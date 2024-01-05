# library
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import datetime
# Create a dataset
# a2D = np.array([[1, 2], [3, 4]])
# print(a2D)
# df = pd.DataFrame(a2D, columns=["a","b"])
# print(df)
# Default heatmap
# p1 = sns.heatmap(df)
# plt.show()
DF_TRIM_START=10000
DF_TRIM_END=200000
new_df=pd.read_csv("temps_real_interpolated.csv")
# long
# new_df = new_df.truncate(before=25000,after=150000)
# short to test
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
df_modified=name_df.applymap(append_strings)
# print(df_modified)


# print_dataframe_arrays(df_modified)
# print(new_name_df)
cell_temp_array_list = []


def get_array_for_row(df,row):
    return np.array([[df.at[row,'cell67temp'],df.at[row,'cell66temp'],df.at[row,'cell55temp'],df.at[row,'cell54temp'],df.at[row,'cell43temp'],df.at[row,'cell42temp'],df.at[row,'cell31temp'],df.at[row,'cell30temp'],df.at[row,'cell19temp'],df.at[row,'cell18temp'],df.at[row,'cell7temp'],df.at[row,'cell6temp']],
                     [df.at[row,'cell68temp'],df.at[row,'cell65temp'],df.at[row,'cell56temp'],df.at[row,'cell53temp'],df.at[row,'cell44temp'],df.at[row,'cell41temp'],df.at[row,'cell32temp'],df.at[row,'cell29temp'],df.at[row,'cell20temp'],df.at[row,'cell17temp'],df.at[row,'cell8temp'],df.at[row,'cell5temp']],
                     [df.at[row,'cell69temp'],df.at[row,'cell64temp'],df.at[row,'cell57temp'],df.at[row,'cell52temp'],df.at[row,'cell45temp'],df.at[row,'cell40temp'],df.at[row,'cell33temp'],df.at[row,'cell28temp'],df.at[row,'cell21temp'],df.at[row,'cell16temp'],df.at[row,'cell9temp'],df.at[row,'cell4temp']],
                     [df.at[row,'cell70temp'],df.at[row,'cell63temp'],df.at[row,'cell58temp'],df.at[row,'cell51temp'],df.at[row,'cell46temp'],df.at[row,'cell39temp'],df.at[row,'cell34temp'],df.at[row,'cell27temp'],df.at[row,'cell22temp'],df.at[row,'cell15temp'],df.at[row,'cell10temp'],df.at[row,'cell3temp']],
                     [df.at[row,'cell71temp'],df.at[row,'cell62temp'],df.at[row,'cell59temp'],df.at[row,'cell50temp'],df.at[row,'cell47temp'],df.at[row,'cell38temp'],df.at[row,'cell35temp'],df.at[row,'cell26temp'],df.at[row,'cell23temp'],df.at[row,'cell14temp'],df.at[row,'cell11temp'],df.at[row,'cell2temp']],
                     [df.at[row,'cell72temp'],df.at[row,'cell61temp'],df.at[row,'cell60temp'],df.at[row,'cell49temp'],df.at[row,'cell48temp'],df.at[row,'cell37temp'],df.at[row,'cell36temp'],df.at[row,'cell25temp'],df.at[row,'cell24temp'],df.at[row,'cell13temp'],df.at[row,'cell12temp'],df.at[row,'cell1temp']]])

for index, row in new_df.iterrows():
    new_array=get_array_for_row(new_df,index)
    cell_temp_array_list.append(pd.DataFrame(new_array,columns=["12","11","10","9","8","7","6","5","4","3","2","1"]))

RENDER_SKIP_SPEED=1000

fig,ax = plt.subplots()
cmap="jet"
linewidths=1
linecolor='black'
def init():
    s=sns.heatmap(np.zeros((6, 12)),annot=True,fmt=".1f",vmin=10,vmax=80,
                  square=True,ax=ax,cbar=False,cmap=cmap,
                  linewidths=linewidths,linecolor=linecolor)
    s.set_xlabel("Time:")

def animate(i):
    data = cell_temp_array_list[i*RENDER_SKIP_SPEED]
    # print(data)
    ax.cla()
    s=sns.heatmap(data,annot=data,fmt=".1f",vmin=10,vmax=80,
                  square=True,ax=ax,cbar=False,cmap=cmap,
                  linewidths=linewidths,linecolor=linecolor)
    timestamp=str(datetime.datetime.fromtimestamp((new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),"Time"])//1000))
    current=str(round(new_df.at[(DF_TRIM_START+(i*RENDER_SKIP_SPEED)),"Pack_Current"],1))
    # print(timestamp)
    s.set_xlabel("Time: " + timestamp+" Current: " + current)

anim=animation.FuncAnimation(fig,animate,init_func=init,frames=(len(cell_temp_array_list)//RENDER_SKIP_SPEED),repeat=False,interval=300)
anim.save('heatmap2.gif', writer='imagemagick', fps=10)
plt.show()