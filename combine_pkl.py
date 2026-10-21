import glob
import os

def combine_chunks():
    # Get the absolute path of the folder containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set input pattern and output file
    chunk_pattern = os.path.join(script_dir, "chunk_*")
    output_file = os.path.join(script_dir, "MethodsDataDict.pkl")
    
    # Find and sort all chunk files
    chunk_files = sorted(glob.glob(chunk_pattern))
    
    if not chunk_files:
        print(f"Error: No chunk files found in {script_dir}")
        return

    print(f"Found {len(chunk_files)} chunks. Combining them in: {script_dir}\n")
    
    # Reassemble the raw binary file
    with open(output_file, "wb") as outfile:
        for chunk_path in chunk_files:
            filename = os.path.basename(chunk_path)
            print(f"Appending {filename}...")
            
            with open(chunk_path, "rb") as infile:
                while True:
                    buffer = infile.read(64 * 1024 * 1024)
                    if not buffer:
                        break
                    outfile.write(buffer)

    print("\n")
    print(f"Successfully combined into: {output_file}")


if __name__ == "__main__":
    combine_chunks()
