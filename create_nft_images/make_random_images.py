from PIL import Image
import random
import os
from dotenv import load_dotenv
from google.cloud import storage
import time

start_time = time.time() 
# load google cloud credentals
load_dotenv()
gcp_key = os.getenv("GCP_KEY")
gcp_bucket = os.getenv("BUCKET_NAME")
# Set random
random.seed(1691691)
# Number of images to generate
num_images = 9990
# Set numbers that trigger an ultra rare background and anime realtor being picked
u_rare_background_triggers = []
u_rare_backgrounds_count = 0
for _ in range(3):
    u_rare_background_triggers.append(random.randint(0, num_images - 100))
u_rare_realtor_triggers = []
u_rare_realtor_count = 0
for _ in range(3):
    u_rare_realtor_triggers.append(random.randint(0, num_images - 100))
# swap out 50% of the zebra's that get picked
zebra_cut = 2

# Define directories for the images
backgrounds_dir = "backgrounds/"  # Directory with your background images
anime_realtors_dir = "anime_realtors/"  # Directory with your anime realtor images
output_dir = "output/"  # Directory to save the combined images
ultra_rare_background_dir = "ultra_rare_backgrounds"  # Directory with ultra rare background images
ultra_rare_realtors_dir = "ultra_rare_anime_realtors"  # Directory with ultra rare anime realtor images

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get lists of files in both directories
backgrounds = [_file for _file in os.listdir(backgrounds_dir) if _file != ".DS_Store"]
anime_realtors = [_file for _file in os.listdir(anime_realtors_dir) if _file != ".DS_Store"]
# And list of ultra rare backgrounds and anime realtors
u_rare_backgrounds = [_file for _file in os.listdir(ultra_rare_background_dir) if _file != ".DS_Store"]
u_rare_realtors = [_file for _file in os.listdir(ultra_rare_realtors_dir) if _file != ".DS_Store"]

# share how many of each file we have
initial_status = f"""
Combining from {len(backgrounds)} backgrounds, {len(anime_realtors)} realtors, {len(u_rare_backgrounds)} rare backgrounds, and {len(u_rare_realtors)} rare realtors.
"""
print(initial_status)


def upload_png_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """
    Uploads a PNG file to the specified Google Cloud Storage bucket.
    """
    # Initialize the GCS client
    client = storage.Client()
    
    # Get the bucket
    bucket = client.bucket(bucket_name)
    
    # Create a blob (object) in the bucket
    blob = bucket.blob(destination_blob_name)
    
    # Upload the PNG file
    blob.upload_from_filename(source_file_path, content_type="image/png")

    # delete file from local storage
    os.remove(source_file_path)

    # tell us every 50
    if len(os.listdir(backgrounds_dir)) % 50 == 0:
        print(f"File {source_file_path} uploaded to {bucket_name}/{destination_blob_name}")
    

# Define a function to count how many files are in a directory
def count_files(directory):
    n_files = 0
    for _file in os.listdir(directory):
        if _file != ".DS_Store" and os.path.isfile(os.path.join(directory, _file)):
            n_files += 1
    return n_files


# Function to combine images
def combine_images(background_path, realtor_path, output_path, realtor_size=0.8):
    # Open the background and anime realtor images
    background = Image.open(background_path)
    realtor = Image.open(realtor_path).convert("RGBA")

    # Resize realtor to fit the background 
    realtor = realtor.resize(background.size, Image.LANCZOS)
    
    # Get original sizes
    bg_width, bg_height = background.size
    realtor_width, realtor_height = realtor.size

    # Resize realtor to x% of its original size
    # unless it is a designated file
    if "deep_love" in realtor_path:
        new_width = int(realtor_width * 1)
        new_height = int(realtor_height * 1)
        print(f"deep love detected at {realtor_path}")
    elif "goldfish_man" in realtor_path:
        new_width = int(realtor_width * 1)
        new_height = int(realtor_height * 1)
        print(f"was that goldfish man? at {realtor_path}")
    else:
        new_width = int(realtor_width * realtor_size)
        new_height = int(realtor_height * realtor_size)

    realtor = realtor.resize((new_width, new_height), Image.LANCZOS)

    # Calculate position to align the bottom
    x_position = (bg_width - new_width) // 2  # Center horizontally
    y_position = bg_height - new_height  # Align bottom

    # Create a transparent layer
    combined = background.convert("RGBA")
    combined.paste(realtor, (x_position, y_position), realtor)

    # Save the result
    combined.save(output_path, format="PNG")


# create nft images and upload them to google cloud storage bucket
if __name__=="__main__":
    # record number of files that are elgible to be cut
    count_for_cut = 0

    # Generate the collection
    for i in range(num_images):
        # Randomly select a background and anime realtor image
        background_file = random.choice(backgrounds)
        realtor_file = random.choice(anime_realtors)

        # cut choices randomly
        if "zebra" in realtor_file:
            # did we let the last one thru?
            if count_for_cut % 2 == 1:
                print("zebra cut")
                # pick a new file
                realtor_file = random.choice(anime_realtors)
                count_for_cut += 1
            else:
                print("zebra thru")
                count_for_cut += 1

        
        # Construct the full file paths
        b_path = os.path.join(backgrounds_dir, background_file)
        r_path = os.path.join(anime_realtors_dir, realtor_file)

        # Roll to see if an ultra rare background or ultra rare realtor is unlocked for this image
        random_roll = random.randint(0, num_images)
        u_rare_tag = ""
        if random_roll in u_rare_background_triggers:
            u_rare_tag = "urbg"
            u_rare_backgrounds_count += 1
            print(f"Ultra Rare Background Unlocked w/ code {random_roll} for nft_{i+1}.png! Total {u_rare_backgrounds_count}")
            background_file = random.choice(u_rare_backgrounds)
            b_path = os.path.join(ultra_rare_background_dir, background_file)
        if random_roll in u_rare_realtor_triggers:
            u_rare_realtor_count += 1
            if u_rare_tag == "urbg":
                u_rare_tag = u_rare_tag + "_urar"
            else:
                u_rare_tag = "urar"
            u_rare_tag = u_rare_tag + "rare_realtor"
            print(f"Ultra Rare Realtor Unlocked w/ code {random_roll} for nft_{i+1}.png! Total {u_rare_realtor_count}")
            realtor_file = random.choice(u_rare_realtors)
            r_path = os.path.join(ultra_rare_realtors_dir, realtor_file)
        if u_rare_tag != "":
            u_rare_tag = u_rare_tag + "_"
        
        # Output file path
        out_path = os.path.join(output_dir, f"{u_rare_tag}nft_{i+1}.png")
        
        # Combine the images and save the result
        combine_images(background_path=b_path, realtor_path=r_path, output_path=out_path)

        upload_png_to_gcs(gcp_bucket, out_path, f"nft_{i+1}.png")

        if (i + 1) % 100 == 0:  # Print progress every 100 images
            print(f"Generated {i + 1}/{num_images} images.")
            print(f"Runtime: {time.time() - start_time:.6f} seconds.\n")

    print("Image generation complete!")

    end_time = time.time()
    print(f"Runtime: {end_time - start_time:.6f} seconds")
    print(f"Runtime: {(end_time - start_time)/100} seconds per image")
