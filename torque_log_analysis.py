import pandas as pd
from pandas import DataFrame
from scipy.fft import fft, fftfreq, rfft, rfftfreq
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from parser_utils import folder_selection_utils
from scipy.stats import linregress
import os
import math
import parser_utils.parser_logger
import logging
import json


def drop_rows_from_df(df: DataFrame, column_name, min, max):
    newdf = df[(df[column_name] >= min) & (df[column_name] <= max)]
    rows_dropped = len(df) - len(newdf)
    logging.info(f"{column_name}: dropped {rows_dropped} rows")
    return newdf


def resample_data(df: DataFrame, time_column_name: str):
    df = df
    # Assuming 'df' is your original DataFrame with 'Time' as epoch time in milliseconds
    df[time_column_name] = pd.to_datetime(
        df[time_column_name], unit='ms')  # Convert epoch time to datetime
    df.set_index(time_column_name, inplace=True)  # Set 'Time' as index
    df = df.interpolate()
    # df.to_csv('interpdata.csv')
    # Assuming 'D3_VAB_Vd_Voltage' is the column containing the signal
    plot_to_compare = False

    df = df[~df.index.duplicated()]
    # Resample to 100ms intervals and forward fill missing values
    df_resampled = df.resample('100L', convention='start').ffill()

    # Save resampled DataFrame to a file
    # df_resampled.to_csv('resampled_data.csv')
    if plot_to_compare:
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(df.index, df['D2_Torque_Feedback'], label='Original')
        plt.title('D2_Torque_Feedback vs Time (Original)')
        plt.xlabel('Time')
        plt.ylabel('D2_Torque_Feedback')
        plt.legend()
        # # Plot resampled data
        plt.subplot(2, 1, 2)
        plt.plot(df_resampled.index,
                 df_resampled['D2_Torque_Feedback'], label='Resampled')
        plt.title('D2_Torque_Feedback vs Time (Resampled)')
        plt.xlabel('Time')
        plt.ylabel('D2_Torque_Feedback')
        plt.legend()
        plt.tight_layout()
        # plt.show()
    # Show plots

    return df_resampled


def annot_max(df: DataFrame, seriesname, ax=None):
    ymax = df[seriesname].max()
    xmax = df[seriesname].idxmax()
    xmax = xmax.to_numpy()

    text = "max={:.3f}v".format(ymax)
    if not ax:
        ax = plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops = dict(arrowstyle="simple",facecolor='black')
    kw = dict(xycoords='data', textcoords="axes fraction",
              arrowprops=arrowprops, ha="center", va="top")
    ax.annotate(text, xy=(mdates.date2num(xmax), ymax),
                xytext=(0.15, -0.2), **kw)


def annot_min(df: DataFrame, seriesname, ax=None):
    ymin = df[seriesname].min()
    xmin = df[seriesname].idxmin()
    xmin = xmin.to_numpy()

    text = "min={:.3f}v".format(ymin)
    if not ax:
        ax = plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops = dict(
        arrowstyle="simple",facecolor='black')
    kw = dict(xycoords='data', textcoords="axes fraction",
              arrowprops=arrowprops,  ha="center", va="top")
    ax.annotate(text, xy=(xmin, ymin), xytext=(.85, -0.2), **kw)


def main():
    parser_utils.parser_logger.setup_logger()
    # folder = folder_selection_utils.select_folder_and_get_path()
    plt.style.use('bmh')
    # # outfolder = folder_selection_utils.select_folder_and_get_path()
    outfolder = r'D:/MatthewS/motor_analysis_fsae/'
    outfolder_set = False
    # # parsed_data_path = "test.csv"
    # Specify the path to the exported JSON file
    json_file_path = 'path_of_csvs.json'
    
    # Load the list of paths from the JSON file
    with open(json_file_path, 'r') as json_file:
        folder_list = json.load(json_file)
    real_list = set()
    
    for file in folder_list:
        print(file)
        real_list.add(os.path.dirname(file))
        
    df_list = []
    for folder in real_list:
        for filename in os.listdir(folder):
            if filename.endswith('.csv') or filename.endswith('.CSV'):
                file_path = os.path.join(folder, filename)
                try:
                    df = pd.read_csv(file_path)
                    if ("D2_Torque_Feedback") not in list(df):
                        continue
                    try:
                        df = resample_data(df, "Time")
                    except KeyError as e:
                        logging.error(f"Key missing {e} in {filename}")
                        continue
                    try:
                        df = drop_rows_from_df(df, "D1_VSM_State", 4, 7)
                    except KeyError as e:
                        logging.error(f"Key missing {e} in {filename}")
                        continue
                    try:
                        df = drop_rows_from_df(df, "D2_Motor_Speed", -2000, 7000)
                    except KeyError as e:
                        logging.error(f"Key missing {e} in {filename}")
                        continue
                    try:
                        df = drop_rows_from_df(df, "D2_Torque_Feedback", 20, 300)
                    except KeyError as e:
                        logging.error(f"Key missing {e} in {filename}")
                        continue

                    earliest_timestamp = df.index.min()

                    try:
                        df = drop_rows_from_df(df, "Torque_Command", 50, 400)
                    except:
                        logging.error(
                            f"using torque command (0xc0) to filter failed {filename}")
                        try:
                            df = drop_rows_from_df(
                                df, "D1_Commanded_Torque", 50, 400)
                        except:
                            logging.error("damn LMAO!")
                    logging.info(len(df))
                    if len(df) <= 10:
                        logging.info("fuck this df")
                        continue

                    # plt.legend()
                    # plt.show()
                    fig = plt.figure(figsize=(16.2, 9.1))
                    ax1 = fig.add_subplot(4, 4, (1, 12))
                    ax2 = fig.add_subplot(4, 4, (13, 14))
                    ax3 = fig.add_subplot(4, 4, (15, 16))
                    ax1.scatter(df['D2_Motor_Speed'], df['D1_Commanded_Torque'],
                                marker='o', label="Command Torque", c='blue')
                    ax1.scatter(df['D2_Motor_Speed'], df['D2_Torque_Feedback'],
                                marker='o', label="Feedback Torque", c='aqua')
                    ax1.set_xlabel("RPM")
                    ax1.set_ylabel("Torque Command and Est. Torque (Nm)")
                    # ax1.tick_params(axis='y', labelcolor='tab:blue')

                    ax1_1 = ax1.twinx()
                    ax1_1.scatter(df["D2_Motor_Speed"], df["D4_Iq_Command"],
                                label="Iq Command", marker='.', c='maroon')
                    ax1_1.scatter(df["D2_Motor_Speed"], abs(df["D3_Id_Command"]),
                                label="Id Command", marker='.', c='darkolivegreen')
                    ax1_1.scatter(df["D2_Motor_Speed"], abs(
                        df["D2_Flux_Weakening_Output"]), label="Flux Weakening Output", c='palegreen', marker='.')
                    ax1_1.scatter(df["D2_Motor_Speed"], df["D4_Iq"],
                                label="Iq", marker='.', c='tomato')
                    ax1_1.scatter(df["D2_Motor_Speed"], abs(df["D3_Id"]),
                                label="Id", marker='.', c='yellowgreen')
                    ax1_1.set_ylabel("Q and D axis current (Amps)")

                    nticks = 10
                    ax1.yaxis.set_major_locator(
                        matplotlib.ticker.LinearLocator(nticks))
                    ax1_1.yaxis.set_major_locator(
                        matplotlib.ticker.LinearLocator(nticks))
                    # ax1_1.tick_params(axis='y', labelcolor='tab:red')

                    iq_rms = df["D4_Iq"] / (math.sqrt(2))

                    ax2.scatter(iq_rms, df["D2_Torque_Feedback"], label="Torque")

                    slope, intercept, r_value, p_value, std_err = linregress(
                        iq_rms, df['D2_Torque_Feedback'])
                    line = slope * iq_rms + intercept
                    ax2.plot(iq_rms, line, color='tab:red', linestyle='--',
                            label=f'Linear Fit: y = {slope:.2f}x + {intercept:.2f}')

                    ax2.set_xlabel('Q-axis Current (RMS)')
                    ax2.set_ylabel('Torque Feedback')
                    # ax2.tick_params(axis='y', labelcolor='tab:green')

                    ax3.scatter(df.index, df['D1_DC_Bus_Voltage'],
                            label='DC Bus Voltage (V)',marker='.')
                    ax3.scatter(df.index, df["D4_DC_Bus_Current"],
                            label="DC Bus Current (A)",marker='.')
                    ax3.scatter(df.index, df["D2_Motor_Speed"]/10, label="RPM/10",marker='.')

                    annot_max(df, "D1_DC_Bus_Voltage", ax=ax3)
                    annot_min(df, "D1_DC_Bus_Voltage", ax=ax3)

                    ax3.set_xlabel('Time')
                    ax3.set_ylabel('Volts, Amps, RPM')

                    ax1.legend(loc='upper left')
                    ax1_1.legend(loc='upper right')
                    ax2.legend(loc='upper left')
                    ax3.legend(loc='lower center')

                    plt.title("Torque, Current, RPM of log: "+filename+" timestamp: " +
                            str(earliest_timestamp))
                    # plt.tight_layout()
                    file_friendly_timestamp = str(
                        earliest_timestamp.strftime("%Y_%m_%d-%H-%M-%S"))
                    file_friendly_filename = filename.replace(".", "")

                    if not outfolder_set:
                        outfolder += str(
                            earliest_timestamp.strftime("%Y_%m"))
                        os.makedirs(outfolder, exist_ok=True)
                        outfolder_set = True
                    export_filename = f"kt{slope:.2f}_{file_friendly_timestamp}_{file_friendly_filename}"
                    plt.savefig(os.path.join(outfolder, export_filename+".png"))
                    # df.to_csv(os.path.join(
                    #     outfolder, export_filename+".csv"), sep=",")
                    # mng = plt.get_current_fig_manager()
                    # mng.full_screen_toggle()
                    # plt.show()
                    # df_list.append(df)

                except ValueError as e:
                    logging.error(f"error with {file_path}, {e}")
        # big_df = pd.concat(df_list)
        # fig, (ax1, ax2) = plt.subplots(2, figsize=(16.2, 9.1))
        # ax1.scatter(big_df['D2_Motor_Speed'], big_df['D1_Commanded_Torque'],
        #             marker='o', label="Command Torque", c='blue')
        # ax1.scatter(big_df['D2_Motor_Speed'], big_df['D2_Torque_Feedback'],
        #             marker='o', label="Feedback Torque", c='royalblue')
        # ax1.set_xlabel("RPM")
        # ax1.set_ylabel("Torque Command and Est. Torque (Nm)")
        # ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax1_1 = ax1.twinx()
    # ax1_1.scatter(big_df["D2_Motor_Speed"], big_df["D4_Iq_Command"],
    #               label="Iq Command", marker='.', c='maroon')
    # ax1_1.scatter(big_df["D2_Motor_Speed"], abs(big_df["D3_Id_Command"]),
    #               label="Id Command", marker='.', c='darkolivegreen')
    # ax1_1.scatter(big_df["D2_Motor_Speed"], abs(
    #     big_df["D2_Flux_Weakening_Output"]), label="Flux Weakening Output", c='palegreen', marker='.')
    ax1_1.scatter(big_df["D2_Motor_Speed"], big_df["D4_Iq"],
                  label="Iq", marker='.', c='tomato')
    ax1_1.scatter(big_df["D2_Motor_Speed"], abs(big_df["D3_Id"]),
                  label="Id", marker='.', c='yellowgreen')
    ax1_1.set_ylabel("Q and D axis current (Amps)")

    nticks = 10
    ax1.yaxis.set_major_locator(
        matplotlib.ticker.LinearLocator(nticks))
    ax1_1.yaxis.set_major_locator(
        matplotlib.ticker.LinearLocator(nticks))
    # ax1_1.tick_params(axis='y', labelcolor='tab:red')

    iq_rms = big_df["D4_Iq"] / (math.sqrt(2))

    ax2.scatter(iq_rms, big_df["D2_Torque_Feedback"], label="Torque")

    slope, intercept, r_value, p_value, std_err = linregress(
        iq_rms, big_df['D2_Torque_Feedback'])
    line = slope * iq_rms + intercept
    ax2.plot(iq_rms, line, color='tab:red', linestyle='--',
             label=f'Linear Fit: y = {slope:.2f}x + {intercept:.2f}')

    ax2.set_xlabel('Q-axis Current (RMS)')
    ax2.set_ylabel('Torque Feedback')
    # ax2.tick_params(axis='y', labelcolor='tab:green')

    ax1.legend(loc='upper left')
    ax1_1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.title("Torque, Current, RPM of all logs, timestamp: " +
              str(earliest_timestamp))
    plt.tight_layout()
    file_friendly_timestamp = str(
        earliest_timestamp.strftime("%Y_%m_%d-%H-%M-%S"))
    file_friendly_filename = filename.replace(".", "")
    export_filename = f"kt{slope:.2f}_{file_friendly_timestamp}"
    plt.savefig(os.path.join(folder, export_filename+".png"),
                bbox_inches='tight')
    # big_df.to_csv(outfolder+export_filename+".csv",sep=",")
    # mng = plt.get_current_fig_manager()
    # mng.full_screen_toggle()
    # plt.show()


if __name__ == "__main__":
    main()
