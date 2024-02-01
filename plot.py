import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt

def select_file():
    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    return file_path

def load_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading the CSV file: {e}")
        return None

def select_columns(df):
    columns = df.columns.tolist()
    
    # Select X-axis column
    # x_axis_column = input("Select X-axis column from the following options:\n{}\n".format(columns))
    x_axis_column = "Time"
    # Select first Y-axis column
    y1_axis_column = input("Select first Y-axis column from the following options:\n{}\n".format(columns))
    
    # Select second Y-axis column
    y2_axis_column = input("Select second Y-axis column from the following options:\n{}\n".format(columns))
    
    return x_axis_column, y1_axis_column, y2_axis_column

def plot_data(df, x_column, y1_column, y2_column):
    plt.figure(figsize=(10, 6))
    plt.plot(df[x_column], df[y1_column].interpolate(), label=y1_column)
    plt.plot(df[x_column], df[y2_column].interpolate(), label=y2_column)
    plt.xlabel(x_column)
    plt.ylabel("Values")
    plt.legend()
    plt.title("Data Plot")
    plt.show()

def main():
    root = tk.Tk()
    root.withdraw()

    # Step 1: Select CSV file
    file_path = select_file()
    
    # Step 2: Load CSV file into a Pandas DataFrame
    if file_path:
        df = load_dataframe(file_path)
        
        if df is not None:
            # Step 3: Select X-axis, Y1-axis, and Y2-axis columns
            x_column, y1_column, y2_column = select_columns(df)
            
            # Step 4: Plot the data
            plot_data(df, x_column, y1_column, y2_column)

if __name__ == "__main__":
    main()
