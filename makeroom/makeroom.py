import os
import shutil
import sys

# Define the categories and their corresponding file extensions
CATEGORIES = {
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
    "Documents": ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt'],
    "Videos": ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'],
    "Music": ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma'],
    "Executables": ['.exe', '.bat', '.msi', '.sh'],
    "Archives": ['.zip', '.rar', '.tar', '.gz', '.7z'],
    "Folders": [],
    "Others": []
}

def categorize_file(file_name):
    # Get the file extension and convert to lowercase
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()

    # Determine the category
    for category, extensions in CATEGORIES.items():
        if file_extension in extensions:
            return category
    return "Others"

def organize_directory(directory):
    # Iterate through the files in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        if os.path.isdir(item_path):
            # Skip if it's a directory and categorize as 'Folders'
            category = "Folders"
        else:
            # Categorize the file based on its extension
            category = categorize_file(item)

        # Create the category directory if it doesn't exist
        category_path = os.path.join(directory, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

        # Move the file or directory to the appropriate category folder
        shutil.move(item_path, os.path.join(category_path, item))

if __name__ == "__main__":
    # Check if the user provided a directory path as an argument
    if len(sys.argv) != 2:
        print("Usage: python organize_files.py <directory_path>")
        sys.exit(1)

    # Get the directory to organize from the command-line argument
    directory_to_organize = sys.argv[1]

    # Check if the provided path is a valid directory
    if not os.path.isdir(directory_to_organize):
        print(f"Error: {directory_to_organize} is not a valid directory.")
        sys.exit(1)

    # Organize the directory
    organize_directory(directory_to_organize)

    print(f"Files in '{directory_to_organize}' have been organized successfully.")
