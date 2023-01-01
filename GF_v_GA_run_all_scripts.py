import subprocess
import numpy as np

program_list = np.loadtxt(
    "/Users/loganfries/iCloud/Hockey/Codes/GF_v_GA/GF_v_GA_scripts.txt", dtype=str
)

for program in program_list:

    subprocess.call(["python", str(program)])
    print("Finished running " + str(program))
