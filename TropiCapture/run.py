from bs4 import BeautifulSoup
import requests
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
import re
from urllib.parse import urlparse, parse_qs

version = "0.0.0.3"

# Open the file in read mode
with open('..\globalversionnumber.txt', 'r') as file:
    tempestpy_releasenameandversion = file.read()

# Function to scrape active storm data from Force-13
def scrape_active_storms():
    url = "https://www.force-13.com/cyclones"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 1: From <option> tags (excluding comments)
        storm_ids = [option.text.strip() for option in soup.find_all('option') if "comments" not in option.text.lower()]
        
        remove_statuses = ["Tropical Depression", "Invest", "Tropical Storm", "CYCLONE", "Cyclone"]
        cleaned_storm_ids = []
        for storm_id in storm_ids:
            for status in remove_statuses:
                storm_id = storm_id.replace(status, "").strip()
            if storm_id:
                cleaned_storm_ids.append(storm_id)

        # Step 2: Extract 'flt' values from <a href="...flt=27S">
        storm_links = soup.find_all('a', href=True)
        for link in storm_links:
            href = link['href']
            if 'flt=' in href:
                parsed_url = urlparse(href)
                query = parse_qs(parsed_url.query)
                if 'flt' in query:
                    cyclone_id = query['flt'][0].strip()
                    if cyclone_id and cyclone_id not in cleaned_storm_ids:
                        cleaned_storm_ids.append(cyclone_id)

        return cleaned_storm_ids

    except requests.RequestException as e:
        print(f"Error scraping active storms: {e}")
        return []

# Function to fetch active tropical systems from Force-13
def get_active_tropical_systems():
    return scrape_active_storms()

# Function to fetch the real-time imagery of a tropical system
def fetch_image(system_name, imagery_type):
    if imagery_type == "still":
        image_url = f"https://www.force-13.com/floaters/{system_name.replace(' ', '_')}/imagery/ott.png"
    elif imagery_type == "animated":
        image_url = f"https://www.force-13.com/floaters/{system_name.replace(' ', '_')}/imagery/ott-animated.gif"
    else:
        print("Invalid imagery type selected.")
        return None
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        print(f"Link to {system_name}'s imagery: {image_url}")
        return img
    except requests.RequestException as e:
        print(f"Error fetching image for {system_name}: {e}")
        return None

# Function to display static imagery in a Tkinter window
def display_image(image):
    if image:
        root = Tk()
        root.title(f"Tropical System Imagery (Still) - TropiCapture by Blaine Palmer (Ver {version}) || TempestPy {tempestpy_releasenameandversion}")
        img_tk = ImageTk.PhotoImage(image)
        label = Label(root, image=img_tk)
        label.pack()
        root.mainloop()

# Function to display animated imagery in a Tkinter window
def display_animated_image(image):
    if image:
        root = Tk()
        root.title(f"Tropical System Imagery (Animated) - TropiCapture by Blaine Palmer (Ver {version}) || TempestPy {tempestpy_releasenameandversion}")
        label = Label(root)
        label.pack()
        def update_frame(frame_index):
            try:
                image.seek(frame_index)
                img_tk = ImageTk.PhotoImage(image)
                label.config(image=img_tk)
                label.image = img_tk
                root.after(100, update_frame, (frame_index + 1) % image.n_frames)
            except EOFError:
                root.after(100, update_frame, 0)
        update_frame(0)
        root.mainloop()

# Main function to interact with the user
def main():
    print("Welcome to TropiCapture!")
    print("A program/script that is a part of the TempestPy Weather Enthusiast Suite")
    print(f"Version {version}")
    print("by Blaine Palmer")
    print("==================")
    print("Fetching currently active tropical systems....")
    print("==================")
    active_systems = get_active_tropical_systems()
    
    if not active_systems:
        print("Sorry, no active tropical systems found.")
        return
    
    print("Currently active tropical systems:")
    print("==================")
    for idx, system in enumerate(active_systems, 1):
        print(f"{idx}. {system}")
    
    try:
        choice = int(input("Enter the number of the tropical system you want to view: "))
        if choice < 1 or choice > len(active_systems):
            print("Invalid choice, please select a valid number.")
            return
        system_name = active_systems[choice - 1]
        
        imagery_type = input("Would you like still imagery or animated imagery? (Enter 'still' or 'animated'): ").strip().lower()
        if imagery_type not in ['still', 'animated']:
            print("Invalid choice! Please enter 'still' or 'animated'.")
            return
        
        print(f"Fetching {imagery_type} imagery for {system_name}...")
        image = fetch_image(system_name, imagery_type)
        
        if image:
            if imagery_type == "still":
                display_image(image)
            elif imagery_type == "animated":
                display_animated_image(image)
        else:
            print("Failed to load image.")
    
    except ValueError:
        print("Invalid input! Please enter a valid number.")

if __name__ == "__main__":
    main()
