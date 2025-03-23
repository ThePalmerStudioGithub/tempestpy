from bs4 import BeautifulSoup
import requests
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
version = "0.0.0.1";
# Function to scrape active storm data from Force-13
def scrape_active_storms():
    url = "https://www.force-13.com/cyclones"  # Replace with the actual URL
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract storm data from <option> tags, excluding those with "comments"
        storm_ids = [option.text.strip() for option in soup.find_all('option') if "comments" not in option.text.lower()]
        
        # Define the status texts to remove
        remove_statuses = ["Tropical Depression", "Invest", "Tropical Storm", "Tropical Cyclone"]
        
        # Remove any of the status text from the storm IDs
        cleaned_storm_ids = []
        for storm_id in storm_ids:
            for status in remove_statuses:
                storm_id = storm_id.replace(status, "").strip()  # Remove status text
            if storm_id:  # Only add if the storm_id is not empty
                cleaned_storm_ids.append(storm_id)
        
        return cleaned_storm_ids
    except requests.RequestException as e:
        print(f"Error scraping active storms: {e}")
        return []

# Function to fetch active tropical systems from Force-13
def get_active_tropical_systems():
    return scrape_active_storms()  # Get storm IDs dynamically from Force-13

# Function to fetch the real-time imagery of a tropical system
def fetch_image(system_name, imagery_type):
    # Example image URL logic:
    if imagery_type == "still":
        image_url = f"https://www.force-13.com/floaters/{system_name.replace(' ', '_')}/imagery/ott.png"
    elif imagery_type == "animated":
        image_url = f"https://www.force-13.com/floaters/{system_name.replace(' ', '_')}/imagery/ott-animated.gif"
    else:
        print("Invalid imagery type selected.")
        return None
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        img_data = response.content
        img = Image.open(BytesIO(img_data))  # Load image from byte data
        print(f"Link to {system_name}'s imagery: {image_url}")
        return img
    except requests.RequestException as e:
        print(f"Error fetching image for {system_name}: {e}")
        return None

# Function to display static imagery in a Tkinter window
def display_image(image):
    if image:
        # Create a window
        root = Tk()
        root.title("Tropical System Imagery (Still)")

        # Convert the image to a format suitable for Tkinter
        img_tk = ImageTk.PhotoImage(image)
        
        # Create a label to display the image
        label = Label(root, image=img_tk)
        label.pack()

        # Run the Tkinter event loop
        root.mainloop()

# Function to display animated imagery in a Tkinter window
def display_animated_image(image):
    if image:
        # Create a window
        root = Tk()
        root.title("Tropical System Imagery (Animated)")

        # Create a label to display the image
        label = Label(root)
        label.pack()

        # This will animate the frames of the GIF
        def update_frame(frame_index):
            try:
                image.seek(frame_index)  # Seek to the current frame
                img_tk = ImageTk.PhotoImage(image)
                label.config(image=img_tk)
                label.image = img_tk  # Keep a reference to the image
                # Schedule the next frame update, wrapping around when we reach the end
                root.after(100, update_frame, (frame_index + 1) % image.n_frames)
            except EOFError:
                # This exception occurs when the seek goes beyond the last frame. 
                # Simply start again from the first frame.
                root.after(100, update_frame, 0)  # Restart from frame 0

        # Start the animation
        update_frame(0)

        # Run the Tkinter event loop
        root.mainloop()

# Main function to interact with the user
def main():
    print("Welcome to the TropiCapture!")
    print("A program/script that is a part of the TempestPy Weather Enthusiast Suite")
    print(f"Version {version}")
    print("by Blaine Palmer")
    print("==================");
    print("Fetching currently active tropical systems....");
    print("==================");
    # Fetch list of active tropical systems
    active_systems = get_active_tropical_systems()
    
    if not active_systems:
        print("Sorry, no active tropical systems found.")
        return
    
    print("Currently active tropical systems:")
    print("==================")
    for idx, system in enumerate(active_systems, 1):
        print(f"{idx}. {system}")
    
    try:
        # Ask user which system they'd like to view
        choice = int(input("Enter the number of the tropical system you want to view: "))
        if choice < 1 or choice > len(active_systems):
            print("Invalid choice, please select a valid number.")
            return
        system_name = active_systems[choice - 1]
        
        # Ask the user whether they want still imagery or animated imagery
        imagery_type = input("Would you like still imagery or animated imagery? (Enter 'still' or 'animated'): ").strip().lower()
        if imagery_type not in ['still', 'animated']:
            print("Invalid choice! Please enter 'still' or 'animated'.")
            return
        
        # Fetch the imagery of the chosen tropical system based on their choice
        print(f"Fetching {imagery_type} imagery for {system_name}...")
        image = fetch_image(system_name, imagery_type)
        
        if image:
            # Display the fetched image in a Tkinter window
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
