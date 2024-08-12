import os
from DeepImageSearch import Load_Data, Search_Setup


# Function to count the number of image files in the folder
def count_images_in_folder(folder_path):
    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".gif",
    )  # Common image file extensions
    return sum(
        1
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(image_extensions)
    )


# Load images from the folder
image_list = Load_Data().from_folder(["data"])

# Determine the number of images in the data folder
image_count = count_images_in_folder("data")

# Set up the search engine with the determined image_count
st = Search_Setup(
    image_list=image_list,
    model_name="resnet50",
    pretrained=True,
    image_count=image_count,
)

# Index the images
st.run_index()

# Infinite loop to process image queries
while True:
    try:
        # Get image path input from user
        image_path = input("Enter image path (or type 'exit' to end): ")

        # Check if the user wants to exit the loop
        if image_path.lower() == "exit":
            break

        # Get similar images
        similar_images = st.get_similar_images(
            image_path=image_path, number_of_images=10
        )

        # Print similar images
        print(similar_images)

    except Exception as e:
        print(f"An error occurred: {e}")

# End of the program
print("Process ended.")
