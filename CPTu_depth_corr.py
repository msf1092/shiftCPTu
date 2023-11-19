# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 11:28:42 2023

@author: M.S. Farhadi

The code should be enhanced! It should be modified using a class, for three different classes!
A good plot function can be developed to shorten the code!

"""
directory_path = 'C:/Users/qdmofa/OneDrive - TUNI.fi/Fincone II-adjunct/Asli/FINCONE II - Analytical tools/CPTu depth corrections/in/'
directory_out = 'C:/Users/qdmofa/OneDrive - TUNI.fi/Fincone II-adjunct/Asli/FINCONE II - Analytical tools/CPTu depth corrections/out/' # Specify the path where you want to save the file



# Import the necessary libraries
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.ticker as ticker
import re
import statistics

# Create a function to load the file
def load_file():
    # Open a directory dialog and get the directory path
    directory_path = filedialog.askdirectory()
    
    # Get a list of all .txt files in the directory
    txt_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    
    # Create a simple GUI to display the .txt files
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    new_window = tk.Toplevel(root)  # Create a new window
    new_window.title('File Selector')
    new_window.geometry('300x200')  # Set the size of the window
    style = ttk.Style(new_window)
    style.theme_use('clam')  # Set the theme of the window

    # Create a label
    label = ttk.Label(new_window, text='Select a file:')
    label.pack(pady=10)

    # Create a dropdown menu
    var = tk.StringVar(new_window)
    var.set(txt_files[0])  # set the default option
    dropdown = ttk.OptionMenu(new_window, var, *txt_files)
    dropdown.pack(pady=10)

    # Create a function to load the selected file when a button is clicked
    def load_selected_file():
        # Get the selected file
        selected_file = var.get()
        
        # Load the text file into a pandas DataFrame
        df = pd.read_csv(os.path.join(directory_path, selected_file), delimiter='\t')
        
        # Write the DataFrame to a new CSV file
        df.to_csv('loaded_data.csv', index=False)
        
        # Display the first few rows of the DataFrame
        print(df.head())

        # Close the GUI window
        new_window.destroy()
        root.quit()

    # Create a button that, when clicked, runs the load_selected_file function
    button = ttk.Button(new_window, text='Load Selected File', command=load_selected_file)
    button.pack(pady=10)

    # Run the GUI
    root.mainloop()

# Run the load_file function
load_file()

#%% For plotting Q_c
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end



# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the Qc unit. If it is in kPa, change it to MPa, for the plot!
def qc_plot_unit(df):
    qc = df['Qc'].astype(float)
    avg_qc = np.mean(qc)
    if avg_qc > 50:
        qc = qc * 0.001
    return qc


# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.7/2.54, 12/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0
        end = strt_ind[i] - 1
    else:
        start = strt_ind[i-1]
        end = strt_ind[i] - 1
    
    plot_part(qc_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i]
end = max(df.shape)
plot_part(qc_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$Q_c \: [MPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure

#%% For plotting F_s
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end



# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the Fs unit. If it is in MPa, change it to kPa, for the plot!
def fs_plot_unit(df):
    fs = df['Fs'].astype(float)
    avg_fs = np.mean(fs)
    if avg_fs > 50:
        fs = fs * 0.001
    return fs


# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.7/2.54, 12/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0
        end = strt_ind[i] - 1
    else:
        start = strt_ind[i-1]
        end = strt_ind[i] - 1
    
    plot_part(fs_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i]
end = max(df.shape)
plot_part(fs_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$F_s \: [kPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(40))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure
#%% For plotting u_2
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end



# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the u2 unit. If it is in MPa, change it to kPa, for the plot!
def u2_plot_unit(df):
    u2 = df['U2'].astype(float)
    avg_u2 = np.mean(u2)
    if avg_u2 > 500:
        u2 = u2 * 0.001
    return u2



# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.7/2.54, 12/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0
        end = strt_ind[i] - 1
    else:
        start = strt_ind[i-1]
        end = strt_ind[i] - 1
    
    plot_part(u2_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i]
end = max(df.shape)
plot_part(u2_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$u_2 \: [kPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(400))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(50))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure
#%%
# =============================================================================
# Above, the depths are not corrected for shifting the fs n u2.
# =============================================================================
# =============================================================================
# Below, the depths are corrected for shifting the fs n u2 measurements.
# =============================================================================

#%% For plotting Q_c
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end



# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the Qc unit. If it is in kPa, change it to MPa, for the plot!
def qc_plot_unit(df):
    qc = df['Qc'].astype(float)
    avg_qc = np.mean(qc)
    if avg_qc > 50:
        qc = qc * 0.001
    return qc


# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.4/2.54, 10/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 7
        end = strt_ind[i] - 8
    else:
        start = strt_ind[i-1] + 7
        end = strt_ind[i] - 8
    
    plot_part(qc_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i] + 7
end = max(df.shape) - 7
plot_part(qc_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$Q_c \: [MPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure

#%% For plotting F_s
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end



# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the Fs unit. If it is in MPa, change it to kPa, for the plot!
def fs_plot_unit(df):
    fs = df['Fs'].astype(float)
    avg_fs = np.mean(fs)
    if avg_fs > 50:
        fs = fs * 0.001
    return fs


# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.4/2.54, 10/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0 + 7
        end = strt_ind[i] - 1 - 7
    else:
        start = strt_ind[i-1] + 7
        end = strt_ind[i] - 1 - 7
    
    plot_part(fs_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i] + 7
end = max(df.shape) - 7
plot_part(fs_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$F_s \: [kPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(40))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure
#%% For plotting u_2
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end



# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the u2 unit. If it is in MPa, change it to kPa, for the plot!
def u2_plot_unit(df):
    u2 = df['U2'].astype(float)
    avg_u2 = np.mean(u2)
    if avg_u2 > 500:
        u2 = u2 * 0.001
    return u2



# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.4/2.54, 10/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0 + 7
        end = strt_ind[i] - 1 - 7
    else:
        start = strt_ind[i-1] + 7
        end = strt_ind[i] - 1 - 7
    
    plot_part(u2_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i] + 7
end = max(df.shape) - 7
plot_part(u2_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$u_2 \: [kPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(400))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(50))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure
#%%
# =============================================================================
# Above, the depths are corrected for shifting the fs n u2 measurements.
# =============================================================================
# =============================================================================
# Below, drawing a section of the figures
# =============================================================================

#%% For plotting Q_c
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end

############%% Removing the rows using the chosen depths ################
# removing from the df
d_strt_section = input("Enter the start depth of the section (default is '[4.36]! Even number!'): ") or "4.36" 
d_strt_section = float(d_strt_section)
strt_section_ind = str(np.where(D == d_strt_section))
strt_section_ind = int(re.search(r'\d+', strt_section_ind).group())
d_end_section = input("Enter the end depth of the section (default is '[4.84]! Even number!'): ") or "4.84"
d_end_section = float(d_end_section)
end_section_ind = str(np.where(D == d_end_section))
end_section_ind = int(re.search(r'\d+', end_section_ind).group())

xmin = input("Enter the plot min limit of Q_c (default is '[0.0]'): ") or "0.0" 
xmin = float(xmin)
xmax = input("Enter the plot max limit of Q_c (default is '[15.0]'): ") or "15.0" 
xmax = float(xmax)

df = df.iloc[strt_section_ind:end_section_ind + 1]
#########################################################################

# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the Qc unit. If it is in kPa, change it to MPa, for the plot!
def qc_plot_unit(df):
    qc = df['Qc'].astype(float)
    avg_qc = np.mean(qc)
    if avg_qc > 50:
        qc = qc * 0.001
    return qc


# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.4/2.54, 5/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0
        end = strt_ind[i] - 1
    else:
        start = strt_ind[i-1] + 0
        end = strt_ind[i] - 1 - 0
    
    plot_part(qc_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i] + 0
end = max(df.shape) - 0
plot_part(qc_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.axis([xmin, xmax, min(d_plot_unit(df)), max(d_plot_unit(df))])  # set x and y limits: [xmin, xmax, ymin, ymax]
plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$Q_c \: [MPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.yticks(np.arange(min(d_plot_unit(df)), max(d_plot_unit(df)),0.1))  # replace ymin, ymid, ymax with your values: (ymin, ymax, step)

plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure

#%% For plotting F_s
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end


############%% Removing the rows using the chosen depths ################
# removing from the df
d_strt_section = input("Enter the start depth of the section (default is '[4.36]! Even number!'): ") or "4.36" 
d_strt_section = float(d_strt_section)
strt_section_ind = str(np.where(D == d_strt_section))
strt_section_ind = int(re.search(r'\d+', strt_section_ind).group())
d_end_section = input("Enter the end depth of the section (default is '[4.84]! Even number!'): ") or "4.84"
d_end_section = float(d_end_section)
end_section_ind = str(np.where(D == d_end_section))
end_section_ind = int(re.search(r'\d+', end_section_ind).group())

xmin = input("Enter the plot min limit of F_s (default is '[0.0]'): ") or "0.0" 
xmin = float(xmin)
xmax = input("Enter the plot max limit of F_s (default is '[80.0]'): ") or "80.0" 
xmax = float(xmax)

df = df.iloc[strt_section_ind:end_section_ind + 1]
#########################################################################


# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the Fs unit. If it is in MPa, change it to kPa, for the plot!
def fs_plot_unit(df):
    fs = df['Fs'].astype(float)
    avg_fs = np.mean(fs)
    if avg_fs > 50:
        fs = fs * 0.001
    return fs


# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.4/2.54, 5/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0 + 0
        end = strt_ind[i] - 1 - 0
    else:
        start = strt_ind[i-1] + 0
        end = strt_ind[i] - 1 - 0
    
    plot_part(fs_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i]
end = max(df.shape)
plot_part(fs_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.axis([xmin, xmax, min(d_plot_unit(df)), max(d_plot_unit(df))])  # set x and y limits: [xmin, xmax, ymin, ymax]
plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$F_s \: [kPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(40))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.yticks(np.arange(min(d_plot_unit(df)), max(d_plot_unit(df)),0.1))  # replace ymin, ymid, ymax with your values: (ymin, ymax, step)
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure
#%% For plotting u_2
# load the selected file, which is saved as a csv file.

# Get the directory of the current file
current_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the directory of your CSV file
file_path = os.path.join(current_directory, 'loaded_data.csv')  # replace with your file path if needed

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, delimiter='\,')

# Display the first few rows of the DataFrame
print(df.head())

######################%% Removing the rows based on duplicates in depth

# Assuming df is your DataFrame
df = df.drop_duplicates(subset='Depth', keep='first')

######################%% Finding the discontinuities depths and their indices, using the input
# Asks for the inputs (discontinuities and their depths)
def get_input(prompt, default_value):
    raw = input(prompt)
    if raw == '':
        return default_value
    else:
        # Remove brackets and split rows by semicolon
        rows = raw.replace('[', '').replace(']', '').split(';')
        # Convert each row to a list of floats
        return [list(map(float, row.split(','))) for row in rows]
    
discontinuity = np.matrix(get_input("Number of discontinuities (default is '[2]'): ", '2'))
missed_depths = np.matrix(get_input("Start and end depths of each discontinuity (default is '[2.2, 2.5; 3.2, 3.7]'): ", "[2.2, 2.5; 3.2, 3.7]"))

print("discontinuity: ", discontinuity)
print("missed_depths: ", missed_depths)

D = np.matrix(df['Depth']) * 0.01 # Converting depth from cm to m
D = D.reshape(-1, 1) # ' in MATLAB


# to find the index for the start or ending depth
def strt_end_ind(missed_depths, D, i):
    d_strt = missed_depths[i,0]
    strt_ind = str(np.where(D == d_strt))
    # Extract the first number from the string using regular expressions
    strt_ind = int(re.search(r'\d+', strt_ind).group())
    
    d_end = missed_depths[i,1]
    end_ind = str(np.where(D == d_end))
    end_ind = int(re.search(r'\d+', end_ind).group())
    return strt_ind, end_ind, d_strt, d_end


############%% Removing the rows using the chosen depths ################
# removing from the df
d_strt_section = input("Enter the start depth of the section (default is '[4.36]! Even number!'): ") or "4.36" 
d_strt_section = float(d_strt_section)
strt_section_ind = str(np.where(D == d_strt_section))
strt_section_ind = int(re.search(r'\d+', strt_section_ind).group())
d_end_section = input("Enter the end depth of the section (default is '[4.84]! Even number!'): ") or "4.84"
d_end_section = float(d_end_section)
end_section_ind = str(np.where(D == d_end_section))
end_section_ind = int(re.search(r'\d+', end_section_ind).group())

xmin = input("Enter the plot min limit of u_2 (default is '[-150.0]'): ") or "-150.0" 
xmin = float(xmin)
xmax = input("Enter the plot max limit of u_2 (default is '[500.0]'): ") or "500.0" 
xmax = float(xmax)

df = df.iloc[strt_section_ind:end_section_ind + 1]
#########################################################################


# Check the depth unit. If it is in cm, change it to m, for the plot!
def d_plot_unit(df):
    d = df['Depth'].astype(float)
    avg_d = np.mean(d)
    if avg_d > 50: # So this part works for penetration to 100 m.
        d = d * 0.01 # Change the unit from cm to m
    return d

# Check the u2 unit. If it is in MPa, change it to kPa, for the plot!
def u2_plot_unit(df):
    u2 = df['U2'].astype(float)
    avg_u2 = np.mean(u2)
    if avg_u2 > 500:
        u2 = u2 * 0.001
    return u2



# Set the figure size to 3cm x 10cm (converted to inches)
plt.figure(figsize=(3.4/2.54, 5/2.54))
plt.rc('lines', linewidth=1.0)
plt.rcParams['text.usetex'] = True

def plot_part(x, y, start, end):
    plt.plot(x[start:end], y[start:end],linestyle='-',color='midnightblue')

strt_ind = []
end_ind = []
d_strt = []
d_end = []

for i in range(int(discontinuity)):
    strt, end, dst, dnd = strt_end_ind(missed_depths, D, i)
    print("*****For the discontinuity number {}".format(i))
    strt_ind.append(strt)
    d_strt.append(dst)
    end_ind.append(end)
    d_end.append(dnd)    
    print("Starting depth index of discontinuity: ", strt_ind[i])
    print("Starting depth of discontinuity: ", d_strt[i])
    
    print("Ending depth index of the discontinuity: ", end_ind[i])
    print("Ending depth of the discontinuity: ", d_end[i])
    
    # Rmoving discontinuities from data
    df.drop(df.index[strt_ind[i]:end_ind[i]], inplace=True)
    D = np.matrix(df['Depth']) * 0.01 # Updating df for next iteration, and converting depth from cm to m
    D = D.reshape(-1, 1) # ' in MATLAB
    
    if i == 0:
        start = 0 + 0
        end = strt_ind[i] - 1 - 0
    else:
        start = strt_ind[i-1] + 0
        end = strt_ind[i] - 1 - 0
    
    plot_part(u2_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

#plot the ending part of the curve
start = strt_ind[i]
end = max(df.shape)
plot_part(u2_plot_unit(df), d_plot_unit(df), start, end)  # Plot a part of the data on the current figure

plt.axis([xmin, xmax, min(d_plot_unit(df)), max(d_plot_unit(df))])  # set x and y limits: [xmin, xmax, ymin, ymax]
plt.gca().xaxis.set_label_position('top') # Set the label for the top x-axis
plt.xlabel('$u_2 \: [kPa]$', fontsize=10)  # Label for x-axis
plt.ylabel('$Depth \: [m]$', fontsize=10)  # Label for y-axis
plt.gca().invert_yaxis()  # Invert the y-axis
plt.gca().xaxis.tick_top() # Move the x-axis to the top
plt.tick_params(axis='both', labelsize=9) # Change the font size of the x and y axes tick numbers
# Set major and minor tick locations
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(400))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(50))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
plt.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
plt.grid(which='major', linestyle='-', linewidth='0.5', color='cadetblue') # Customize the major grid
plt.grid(which='minor', linestyle=':', linewidth='0.5', color='mediumaquamarine') # Customize the minor grid
plt.yticks(np.arange(min(d_plot_unit(df)), max(d_plot_unit(df)),0.1))  # replace ymin, ymid, ymax with your values: (ymin, ymax, step)
plt.tight_layout() # Adjust subplot parameters to give specified padding
# Save the figure in different formats
plt.savefig(f"{directory_out}figure.tif", format='tif', dpi=600)  # TIFF format
plt.savefig(f"{directory_out}figure.png", format='png', dpi=600)  # PNG format
plt.savefig(f"{directory_out}figure.jpg", format='jpg', dpi=600)  # JPG format
plt.savefig(f"{directory_out}figure.eps", format='eps', dpi=600)  # EPS format
plt.savefig(f"{directory_out}figure.svg", format='svg', dpi=600)  # SVG format

plt.show()  # Display the figure
