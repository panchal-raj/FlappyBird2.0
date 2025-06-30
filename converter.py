import os

def convert_to_txt(directory):
    # Check all files in the directory
    for filename in os.listdir(directory):
        # Get the file extension
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Check if file is .js or .html
        if file_extension in ['.js', '.html']:
            # Create the new filename with .txt extension
            old_path = os.path.join(directory, filename)
            new_filename = os.path.splitext(filename)[0] + '.txt'
            new_path = os.path.join(directory, new_filename)
            
            try:
                # Read content from original file
                with open(old_path, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()
                
                # Write content to new .txt file
                with open(new_path, 'w', encoding='utf-8') as target_file:
                    target_file.write(content)
                
                # Delete the original file
                os.remove(old_path)
                print(f"Converted and removed {filename} -> {new_filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

# Example usage
directory_path = "D:/Users/Z0054N6M/Projekte/ProjectFAU/FlappyBird-Smile/flappyWeb/txt"  # Replace with your directory path
convert_to_txt(directory_path)