from PIL import Image
import glob


def get_weeks():
    """Returns a list of weeks that we currently have data for."""

    import glob

    path_list = glob.glob("/Users/loganfries/iCloud/Hockey/Data/GF_v_GA/*.csv")

    return [path.split("_")[-1].split(".")[0] for path in path_list]


sorted_list_of_files = []
number_of_files_str = []
number_of_files = []

weeks = get_weeks()

fp_in = "/Users/loganfries/iCloud/Hockey/GIF_Images/GF_v_GA/*.png"
fp_out = "/Users/loganfries/iCloud/Hockey/GIFs/GF_v_GA.gif"

num_frames = len(glob.glob(fp_in))
target_seconds = 5 * len(weeks)

milliseconds_per_frame = target_seconds * 1000 / num_frames

list_of_files = glob.glob(fp_in)

for k in list_of_files:
    number_of_files_str.append(k.split("/")[-1].split(".")[0])

for i in number_of_files_str:
    number = int(i)
    number_of_files.append(number)

for j in sorted(number_of_files):
    for z in list_of_files:
        f = int(z.split("/")[-1].split(".")[0])
        if j == f:
            sorted_list_of_files.append(z)

img, *imgs = [Image.open(i) for i in sorted_list_of_files]
img.save(
    fp=fp_out,
    format="GIF",
    append_images=imgs,
    save_all=True,
    duration=milliseconds_per_frame,
    loop=0,
)
