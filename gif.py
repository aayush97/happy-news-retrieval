import glob
from PIL import Image

def make_gif(category):
    frame_folder = 'Plots/' + category
    images = []
    for image in glob.glob(f"{frame_folder}/*.png"):
        images.append(image)
    images.sort()
    frames = [Image.open(image) for image in images]
    frame_one = frames[0]
    frame_one.save(f"Plots/{category}.gif", format="GIF", append_images=frames,
               save_all=True, duration=1000, loop=0)
    
if __name__ == "__main__":
    categories = ['Cats', 'Puppies', 'Nature', 'Sports']
    for i in categories:
        make_gif(i)