from DeepImageSearch import Load_Data, Search_Setup

# Load images from a folder
image_list = Load_Data().from_folder(["data"])

# Set up the search engine
st = Search_Setup(
    image_list=image_list, model_name="vgg19", pretrained=True, image_count=7777
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
