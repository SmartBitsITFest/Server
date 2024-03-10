import subprocess
import time
import json
import os


async def process_expiration_date():
    # Path to the first executable file
    exe1_path = './services/expiration_date_model/run_detection.exe'

    start_detection = time.time()
    # Run the first executable
    process1 = subprocess.Popen(exe1_path)

    # Check if the first executable has exited
    while True:
        return_code = process1.poll()
        if return_code is not None:
            print("First executable exited with return code:", return_code)
            break
    end_detection = time.time()

    not_found = True
    with open('./images_rec/cropped_img_list.json') as f:
        possible_areas = json.load(f)
        for val in possible_areas.values():
            if val != []:
                not_found = False
    
    if not_found:
        return None

    # Path to the second script
    exe2_path = './services/expiration_date_model/run_recognition.exe'

    start_recognition = time.time()
    # Run the second script
    process2 = subprocess.Popen(exe2_path)

    # Check if the first executable has exited
    while True:
        return_code = process2.poll()
        if return_code is not None:
            print("Second executable exited with return code:", return_code)
            break
    end_recognition = time.time()

    print(f'Detection took {end_detection - start_detection}')
    print(f'Recognition took {end_recognition - start_recognition}')