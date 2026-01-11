import kagglehub
import shutil
import os

# Download latest version
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

# Create data folder if it doesn't exist
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

# Copy all files from the downloaded path to the data folder
for item in os.listdir(path):
    source = os.path.join(path, item)
    destination = os.path.join(data_folder, item)
    
    if os.path.isfile(source):
        shutil.copy2(source, destination)
        print(f"Copied: {item}")

print(f"\nAll files saved to '{data_folder}' folder")