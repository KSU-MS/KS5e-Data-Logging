import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

# Sample DataFrame
def sort_df_closed_shape(dfe):
    # Compute centroid
    cent = (dfe['X'].mean(), dfe['Y'].mean())

    # Sort by polar angle
    dfe['angle'] = dfe.apply(lambda row: math.atan2(row['Y'] - cent[1], row['X'] - cent[0]), axis=1)
    df_sorted = dfe.sort_values(by='angle')
    return df_sorted
df = pd.read_csv("efficiency_plot\greenCurveEff.csv")

# Plot points
df_sorted = sort_df_closed_shape(df)
# Plot polyline
# plt.scatter(df_sorted['X'], df_sorted['Y'],alpha=0.2)
plt.scatter(1,1)
plt.gca().add_patch(patches.Polygon(df_sorted[['X', 'Y']].values, closed=True, fill=False,color="red"))

plt.grid()
plt.show()
