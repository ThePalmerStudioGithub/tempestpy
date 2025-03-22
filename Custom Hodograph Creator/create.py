import numpy as np
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.plots import Hodograph
from metpy.units import units
version = "0.0.0.4";

# Open the file in read mode
with open('..\globalversionnumber.txt', 'r') as file:
    tempestpy_releasenameandversion = file.read()
with open('..\iconlocation.txt', 'r') as file:
    tempestpy_icon = file.read()

print("Custom Hodograph Creator")
print("A program/script that is a part of the TempestPy Weather Enthusiast Suite")
print(f"Version {version}")
print("by Blaine Palmer")
print("===========================")
print("What do you want to name your hodograph?")
name_of_hodograph = input()
print("---------------------")
print("What date is this hodograph for?")
date_of_hodograph = input()
print("---------------------")
print("What timestamp is this hodograph for (must be in UTC)?")
timestamp_of_hodograph = input()
print("---------------------")
print("Time to enter the sounding data for your hodograph!")
print("Tell us what the wind speed and direction is for the following barometric pressure levels in the atmosphere:")

def get_input_data(pressure):
    print(f"{pressure} hPa:")
    wind_speed = float(input("Wind Speed (in kts): "))
    wind_direction = float(input("Wind Direction (0-360°): "))
    print("---------------------")
    return wind_speed, wind_direction

# Getting input for each pressure level
windspeed_surface, winddirection_surface = get_input_data(1000)
windspeed_two, winddirection_two = get_input_data(850)
windspeed_three, winddirection_three = get_input_data(600)
windspeed_four, winddirection_four = get_input_data(350)
windspeed_five, winddirection_five = get_input_data(150)

# Sample wind data (pressure levels in hPa, wind speed in knots, wind direction in degrees)
pressure_levels = np.array([1000, 850, 600, 350, 150]) * units.hPa
wind_speed = np.array([windspeed_surface, windspeed_two, windspeed_three, windspeed_four, windspeed_five]) * units.knots
wind_direction = np.array([winddirection_surface, winddirection_two, winddirection_three, winddirection_four, winddirection_five]) * units.degrees

# Convert wind speed and direction to u/v components
u, v = mpcalc.wind_components(wind_speed, wind_direction)
# Define the upper and lower pressure levels for calculating helicity
lower_level = 1000 * units.hPa
upper_level = 500 * units.hPa  # You can adjust this based on your needs
# Calculate helicity (storm-relative helicity)
helicity = mpcalc.storm_relative_helicity(pressure_levels, u, v, depth=upper_level - lower_level)
helicity_value = helicity.magnitude

# Calculate wind shear (wind speed difference between surface and upper levels)
shear_u, shear_v = u[-1] - u[0], v[-1] - v[0]  # Deep-layer shear vector
shear_mag = np.sqrt(shear_u**2 + shear_v**2)

# Processing your data and creating a Skew-T diagram
print("Processing your data and creating a Hodograph out of it......")

# Mean wind (0-6 km layer)
mean_u, mean_v = np.mean(u[:4]), np.mean(v[:4])

# Compute storm motion vectors using Bunkers' method
perp_shear_u = -shear_v / shear_mag * 7.5 * units.knots  # Perpendicular component
perp_shear_v = shear_u / shear_mag * 7.5 * units.knots

rm_u, rm_v = mean_u + perp_shear_u, mean_v + perp_shear_v  # Right-moving
lm_u, lm_v = mean_u - perp_shear_u, mean_v - perp_shear_v  # Left-moving

# Create hodograph plot
fig, ax = plt.subplots(figsize=(6, 6))
hod = Hodograph(ax, component_range=100)  # Set range based on max wind speed
hod.add_grid(increment=20)
hod.plot(u, v, marker='o', linestyle='-', color='b', label="Wind Profile")

# Annotate points with pressure levels and wind speeds
sc = ax.scatter(u.magnitude, v.magnitude, color='b', label="Wind Data", picker=True)
annotation = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                         ha='center', fontsize=10, fontweight='bold', backgroundcolor='white', visible=False)

def on_motion(event):
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            index = ind["ind"][0]
            annotation.set_text(f'{pressure_levels[index].m:.0f} hPa\n{wind_speed[index].m:.1f} kt')
            annotation.set_position((u[index].m, v[index].m))
            annotation.set_visible(True)
        else:
            annotation.set_visible(False)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", on_motion)

# Plot RM and LM storm motions
ax.plot([mean_u.m, rm_u.m], [mean_v.m, rm_v.m], 'r-', label='Right-Moving (RM)')
ax.plot([mean_u.m, lm_u.m], [mean_v.m, lm_v.m], 'g-', label='Left-Moving (LM)')
ax.scatter([rm_u.m, lm_u.m], [rm_v.m, lm_v.m], color=['r', 'g'], zorder=3)

# Mark RM and LM points
ax.text(rm_u.m, rm_v.m, 'RM', color='r', fontsize=12, fontweight='bold', ha='left')
ax.text(lm_u.m, lm_v.m, 'LM', color='g', fontsize=12, fontweight='bold', ha='right')

# Display helicity and shear on the plot
ax.text(0.95, 0.05, f"Helicity: {helicity_value:.2f} m²/s²", transform=ax.transAxes, fontsize=12, ha='right', color='purple')
ax.text(0.95, 0.07, f"Wind Shear: {shear_mag:.2f} knots", transform=ax.transAxes, fontsize=12, ha='right', color='purple')

plt.legend()
plt.title(name_of_hodograph)
plt.get_current_fig_manager().window.title(f"{name_of_hodograph} - {date_of_hodograph} @ {timestamp_of_hodograph}z - Custom Hodograph Creator by Blaine Palmer (Ver {version}) || TempestPy {tempestpy_releasenameandversion} ")
print("Hodograph generated✅")

# Set the custom icon
fig_manager = plt.get_current_fig_manager()
# Access Tkinter root window and set the icon
root = fig_manager.canvas.manager.window
root.iconbitmap(tempestpy_icon)  # Use .ico file for Windows or .png for others

plt.show()
