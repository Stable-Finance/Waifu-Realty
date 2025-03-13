from PIL import Image
import random
import os
from dotenv import load_dotenv
from google.cloud.storage import Client, transfer_manager
import time

start_time = time.time() 
# set up google cloud storage connection
load_dotenv()
gcp_key = os.getenv("GCP_KEY")
gcp_bucket = os.getenv("BUCKET_NAME")
storage_client = Client()
# Set random seed
random.seed(1691691)
# Number of images to generate
num_images = 9990
images_per_upload = 100
# Set numbers that trigger an ultra rare background and anime realtor being picked
u_rare_background_triggers = []
u_rare_backgrounds_count = 0
for _ in range(10):
    u_rare_background_triggers.append(random.randint(0, num_images - 100))
u_rare_realtor_triggers = []
u_rare_realtor_count = 0
for _ in range(10):
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

# # share how many of each file we have
# initial_status = f"""
# Combining from {len(backgrounds)} backgrounds, {len(anime_realtors)} realtors, {len(u_rare_backgrounds)} rare backgrounds, and {len(u_rare_realtors)} rare realtors.
# """
# print(initial_status)

def upload_many_blobs_with_transfer_manager(
    bucket_name, filenames, source_directory="", workers=8
):
    """Upload every file in a list to a bucket, concurrently in a process pool.

    Each blob name is derived from the filename, not including the
    `source_directory` parameter. For complete control of the blob name for each
    file (and other aspects of individual blob metadata), use
    transfer_manager.upload_many() instead.
    """

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # A list (or other iterable) of filenames to upload.
    # filenames = ["file_1.txt", "file_2.txt"]

    # The directory on your computer that is the root of all of the files in the
    # list of filenames. This string is prepended (with os.path.join()) to each
    # filename to get the full path to the file. Relative paths and absolute
    # paths are both accepted. This string is not included in the name of the
    # uploaded blob; it is only used to find the source files. An empty string
    # means "the current working directory". Note that this parameter allows
    # directory traversal (e.g. "/", "../") and is not intended for unsanitized
    # end user input.
    # source_directory=""

    # The maximum number of processes to use for the operation. The performance
    # impact of this value depends on the use case, but smaller files usually
    # benefit from a higher number of processes. Each additional process occupies
    # some CPU and memory resources until finished. Threads can be used instead
    # of processes by passing `worker_type=transfer_manager.THREAD`.
    # workers=8
    bucket = storage_client.bucket(bucket_name)

    results = transfer_manager.upload_many_from_filenames(
        bucket, filenames, source_directory=source_directory, max_workers=workers
    )

    for name, result in zip(filenames, results):
        # The results list is either `None` or an exception for each filename in
        # the input list, in order.

        if isinstance(result, Exception):
            print("Failed to upload {} due to exception: {}".format(name, result))
        else:
            # delete the file from local storage
            os.remove(f"{source_directory}/{name}")
            if "rare" in name:
                print("Uploaded {} to {}.".format(name, bucket.name))


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
    files_for_bulk_upload = []

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
        output_file_name = f"{u_rare_tag}nft_{i+1}.png"
        out_path = os.path.join(output_dir, output_file_name)
        
        # Combine the images and save the result
        combine_images(background_path=b_path, 
                       realtor_path=r_path, 
                       output_path=out_path
                       )
        # add the file name to the list for the next bulk upload
        files_for_bulk_upload.append(output_file_name)

        # bulk upload images to GCS every 10 images
        if len(files_for_bulk_upload) % images_per_upload == 0  or (i + 1) == num_images:
            print("\nBulk upload underway!\n")
            upload_many_blobs_with_transfer_manager(
                gcp_bucket, 
                files_for_bulk_upload, 
                source_directory=output_dir, 
                workers=8
                                                )
            # reset collection of files for upload
            files_for_bulk_upload = []

        if (i + 1) % 100 == 0:  # Print progress every 100 images
            print(f"Generated {i + 1}/{num_images} images.")
            print(f"Runtime: {time.time() - start_time:.6f} seconds.\n")

    print("Image generation complete!")

    end_time = time.time()
    print(f"Runtime: {end_time - start_time:.6f} seconds")
    print(f"Runtime: {(end_time - start_time)/100} seconds per image")
