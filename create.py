import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from metpy.plots import SkewT
from metpy.units import units
from metpy.calc import parcel_profile, lcl, lfc, wind_components, surface_based_cape_cin
import mplcursors
version = "0.0.0.2"
print("Custom Skew-T Diagram Creator")
print(f"Version {version}")
print("by Blaine Palmer")
print("===========================")
print("What do you want to name your Skew-T diagram?")
name_of_diagram = input()
print("---------------------")
print("What date is this Skew-T diagram for?")
date_of_diagram = input()
print("---------------------")
print("What timestamp is this Skew-T diagram for (must be in UTC)?")
timestamp_of_diagram = input()
print("---------------------")
print("Time to enter the sounding data for your Skew-T diagram!")
print("Tell us what the temperature, dew point, wind speed, and direction is for the following barometric pressure(s) in the atmosphere:")

# Reading input and converting to float for further calculation
def get_input_data(pressure):
    print(f"{pressure} hPa:")
    temperature = float(input("Temperature (°C): "))
    dewpoint = float(input("Dew Point (°C): "))
    wind_speed = float(input("Wind Speed (in kts): "))
    wind_direction = float(input("Wind Direction (0-360°): "))
    print("---------------------")
    return temperature, dewpoint, wind_speed, wind_direction

# Getting input for each pressure level
temperature_surface, dewpoint_surface, windspeed_surface, winddirection_surface = get_input_data(1000)
temperature_two, dewpoint_two, windspeed_two, winddirection_two = get_input_data(850)
temperature_three, dewpoint_three, windspeed_three, winddirection_three = get_input_data(600)
temperature_four, dewpoint_four, windspeed_four, winddirection_four = get_input_data(350)
temperature_five, dewpoint_five, windspeed_five, winddirection_five = get_input_data(150)

# Processing your data and creating a Skew-T diagram
print("Processing your data and creating a Skew-T diagram out of it......")

# Real data
data = {
    'Pressure': [1000, 850, 600, 350, 150],  # hPa
    'Temperature': [temperature_surface, temperature_two, temperature_three, temperature_four, temperature_five],  # °C
    'Dew Point': [dewpoint_surface, dewpoint_two, dewpoint_three, dewpoint_four, dewpoint_five],  # °C
    'Wind Speed': [windspeed_surface, windspeed_two, windspeed_three, windspeed_four, windspeed_five],
    'Wind Direction': [winddirection_surface, winddirection_two, winddirection_three, winddirection_four, winddirection_five]
}

# Convert to a pandas DataFrame
df = pd.DataFrame(data)

# Convert data to MetPy units
pressure = df['Pressure'].values * units.hPa
temperature = df['Temperature'].values * units.degC
dewpoint = df['Dew Point'].values * units.degC
wind_speed = df['Wind Speed'].values * units.knots
wind_direction = df['Wind Direction'].values * units.degrees

# Convert wind direction & speed to U/V components
u, v = wind_components(wind_speed, wind_direction)

# Compute the parcel profile (surface-based)
parcel_prof = parcel_profile(pressure, temperature[0], dewpoint[0])

# Compute Lifting Condensation Level (LCL)
lcl_pressure, lcl_temperature = lcl(pressure[0], temperature[0], dewpoint[0])

# Compute Level of Free Convection (LFC)
lfc_pressure, lfc_temperature = lfc(pressure, temperature, dewpoint)

# Calculate CAPE
cape_value, cin_value = surface_based_cape_cin(pressure, temperature, dewpoint)

# Create Skew-T plot
fig = plt.figure(figsize=(8, 10))
skew = SkewT(fig, rotation=45)

# Plot temperature and dew point
skew.plot(pressure, temperature, 'r', linewidth=2, label="Temperature")
skew.plot(pressure, dewpoint, 'g', linewidth=2, label="Dew Point")

# Plot the parcel ascent path
skew.plot(pressure, parcel_prof, 'k', linewidth=2, linestyle='dashed', label="Parcel Ascent")

# Plot LCL as a black dot
skew.ax.plot(lcl_temperature, lcl_pressure, 'ko', markersize=8, label="LCL")

# Plot LFC as a blue dot (if LFC exists)
if lfc_pressure is not None:
    skew.ax.plot(lfc_temperature, lfc_pressure, 'bo', markersize=8, label="LFC")

# Plot wind barbs on the right side
skew.plot_barbs(pressure, u, v)

# Customize the labels for temperature and pressure
skew.ax.set_xlabel("Temperature (°C)")  # Custom X-axis label for temperature
skew.ax.set_ylabel("Pressure (hPa)")  # Custom Y-axis label for pressure

# Add dry adiabats, moist adiabats, and mixing ratio lines
skew.plot_dry_adiabats()
skew.plot_moist_adiabats()
skew.plot_mixing_lines()

# Add text annotations for TCON, LCL, LFC, and CAPE in the corner
plt.figtext(0.02, 0.98, f"TCON: {temperature[0].magnitude:.1f}°C", fontsize=10, color='black', ha='left', va='top')
plt.figtext(0.02, 0.94, f"LCL: {lcl_pressure.magnitude:.1f} hPa, {lcl_temperature.magnitude:.1f}°C", fontsize=10, color='black', ha='left', va='top')
plt.figtext(0.02, 0.82, f"Note: The temperature values at the bottom of the diagram above\n where it says `Temperature (℃)` is incorrect.", fontsize=10, color='black', ha='left', va='top')

# Add LFC label if it exists
if lfc_pressure is not None:
    plt.figtext(0.02, 0.90, f"LFC: {lfc_pressure.magnitude:.1f} hPa, {lfc_temperature.magnitude:.1f}°C", fontsize=10, color='blue', ha='left', va='top')

# Add CAPE label
plt.figtext(0.02, 0.86, f"CAPE: {cape_value.magnitude:.2f} J/kg", fontsize=10, color='red', ha='left', va='top')
plt.figtext(0.02, 0.84, f"CIN: {cin_value.magnitude:.2f} J/kg", fontsize=10, color='red', ha='left', va='top')

# Add interactive hover functionality
sc_temp = skew.ax.plot(temperature, pressure, color='r', label="Temperature_hover")[0]
sc_dew = skew.ax.plot(dewpoint, pressure, color='b', label="Dew Point_hover")[0]

# Using mplcursors to add hover
mplcursors.cursor([sc_temp, sc_dew], hover=True).connect(
    "add", lambda sel: sel.annotation.set_text(
        f"Temperature: {sel.target[0]:.1f}°C"
    )
)

# Add labels, grid, and legend
plt.title(name_of_diagram, fontsize=14)
plt.legend(loc="best")
plt.grid(True)
plt.get_current_fig_manager().window.title(f"{name_of_diagram} - {date_of_diagram} @ {timestamp_of_diagram}z - Custom Skew-T Diagram Creator by Blaine Palmer (Ver {version})")
print("Skew-T Diagram generated.")
# Show the plot
plt.show()
print("Diagram opened ✅")