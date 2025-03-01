import numpy as np
import matplotlib.pyplot as plt

# Default outdoor temperature data for Memphis, September 21, 2025 (heat wave)
outside_temps = [
    75, 72, 70, 71, 73, 69,  # Hours 0-5 (midnight to 5 AM)
    70, 73, 79, 83, 85, 87,  # Hours 6-11 (6 AM to 11 AM)
    90, 90, 90, 89, 88, 88,  # Hours 12-17 (noon to 5 PM)
    82, 80, 78, 78, 75, 75   # Hours 18-23 (6 PM to 11 PM)
]

# Hourly relative humidity (%) - fixed to 24 values to match outside_temps
humidity = [
    62, 68, 76, 73, 66, 79,  # Hours 0-5
    73, 69, 56, 50, 45, 42,  # Hours 6-11
    39, 38, 35, 37, 36, 40,  # Hours 12-17
    45, 43, 53, 58, 62, 64   # Hours 18-23
]

# Verify data length
if len(outside_temps) != 24 or len(humidity) != 24:
    raise ValueError("Temperature and humidity lists must have 24 hourly values.")

# Calculate T_avg and A from outdoor temperature data
T_avg = np.mean(outside_temps)
A = (max(outside_temps) - min(outside_temps)) / 2
print(f"Calculated T_avg: {T_avg:.2f}°F")
print(f"Calculated Amplitude (A): {A:.2f}°F")

# Function to calculate daylight hours for Memphis on September 21, 2025
def calculate_daylight_hours(latitude=35.15, day_of_year=264):
    delta = 23.45 * np.sin(np.deg2rad(360 / 365 * (284 + day_of_year)))
    phi_rad = np.deg2rad(latitude)
    delta_rad = np.deg2rad(delta)
    daylight_hours = (24 / np.pi) * np.arccos(-np.tan(phi_rad) * np.tan(delta_rad))
    solar_noon = 12.0
    sunrise = solar_noon - (daylight_hours / 2)
    sunset = solar_noon + (daylight_hours / 2)
    return sunrise, sunset, daylight_hours

sunrise, sunset, daylight_hours = calculate_daylight_hours()
print(f"Sunrise: {sunrise:.2f} hours (approx {int(sunrise)}:{int((sunrise % 1) * 60):02d} AM)")
print(f"Sunset: {sunset:.2f} hours (approx {int(sunset)-12}:{int((sunset % 1) * 60):02d} PM)")
print(f"Daylight Hours: {daylight_hours:.2f} hours")

# House materials with thermal time constants (tau in hours)
# Note: These are simplified; real tau depends on insulation, house size, etc.
house_materials = {"wood": 4, "brick": 6, "concrete": 8}

def select_house_material():
    print("\nSelect the house material:")
    for material in house_materials:
        print(f"- {material} (tau = {house_materials[material]} hours)")
    selected_material = input("Enter the material: ").lower()
    while selected_material not in house_materials:
        print("Invalid material. Please select from the list.")
        selected_material = input("Enter the material: ").lower()
    return house_materials[selected_material]

tau = select_house_material()
print(f"Selected house material with tau = {tau} hours")

# Simplified humidity adjustment using heat index approximation
def humidity_adjustment(T_out, rh):
    if T_out > 80:
        heat_index = T_out + 0.0036 * (rh - 70) * (T_out - 80)  # Nonlinear effect
        return max(0, heat_index - T_out)
    return 0

# Simplified solar gain (default rate, no window area input)
def solar_gain(t, sunrise, sunset):
    if sunrise <= t <= sunset:
        return 1.5  # Default solar gain rate in °F/hour (simplified)
    return 0

# Effective temperature combining outdoor temp, humidity, and solar gain
def effective_temperature(t, T_out, rh, sunrise, sunset):
    T_eff = T_out + humidity_adjustment(T_out, rh) + solar_gain(t, sunrise, sunset)
    return T_eff

# Initialize indoor temperature to 70°F as specified
T_in = [70.0]  # Hardcoded initial condition

# Simulate indoor temperature for 24 hours
for t in range(1, 24):
    T_eff = effective_temperature(t, outside_temps[t], humidity[t], sunrise, sunset)
    # Update indoor temp using thermal response: dT_in = (T_eff - T_in) / tau
    dT_in = (T_eff - T_in[-1]) / tau
    T_in.append(T_in[-1] + dT_in)

# Plot the results
hours = np.arange(0, 24)
plt.figure(figsize=(10, 6))  # Larger figure for readability
plt.plot(hours, outside_temps, label='Outdoor Temp (°F)', color='orange', linewidth=2)
plt.plot(hours, T_in, label='Indoor Temp (°F)', color='blue', linewidth=2)
plt.axvspan(sunrise, sunset, color='yellow', alpha=0.2, label='Daylight Hours')
plt.xlabel('Hour of the Day')
plt.ylabel('Temperature (°F)')
plt.title('24-Hour Indoor Temperature Prediction in Memphis (Sept 21, Broken AC)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Print final indoor temperature
print(f"Predicted indoor temperature at hour 24: {T_in[-1]:.2f}°F")
