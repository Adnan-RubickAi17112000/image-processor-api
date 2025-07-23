# processor.py
import os, zipfile
import pandas as pd
from PIL import Image
from utilis import *
from googledriver import download_folder

def run_processor(filepath, output_dir):
    if filepath.endswith('.DS_Store'):
        os.remove(filepath)

    df = pd.read_excel(filepath).astype(str)
    df = df.rename(columns=lambda x: x.strip())

    datadict = df.to_dict("records")
    filtered = [temp for temp in datadict if str(temp.get('StyleCode_Image', '')).lower() != "nan"]
    df = pd.DataFrame(filtered)
    datadict = df.to_dict("records")

    seen = set()
    duplicates = []
    for rec in datadict:
        style = rec.get('StyleCode_Image')
        if style in seen:
            duplicates.append(style)
        seen.add(style)

    print(f"Records: {len(datadict)}, Unique: {len(seen)}")
    if duplicates:
        raise ValueError("Duplicates found in StyleCode_Image")

    domains = list(set([link.split("//")[-1].split("/")[0] for link in df["Link_1"] if str(link) != 'nan']))
    print("Domains detected:", domains)

    excel_name = os.path.basename(filepath).split(".")[0]

    for index, temp in enumerate(datadict):
        temp["S.no"] = index + 1
        temp["Excel_name"] = excel_name

    if len(domains) != 1:
        print("Flow 1")
        for temp in datadict:
            route_link(temp, [temp])
    else:
        print("Flow 2")
        route_link(datadict[0], datadict)

    zip_path = os.path.join(output_dir, f'{excel_name}_images.zip')
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for foldername, _, files in os.walk("output"):
            for file in files:
                path = os.path.join(foldername, file)
                arcname = os.path.relpath(path, "output")
                zf.write(path, arcname=arcname)

    return zip_path


def route_link(temp, data):
    url = temp["Link_1"]
    if "postimg" in url:
        process(data, get_post_url, 6)
    elif "dropbox" in url and "." in url.split("https://www.dropbox.com/")[-1]:
        print("image")
        process(data, get_dropbox_url, 3)
    elif "dropbox" in url and "." not in url.split("https://www.dropbox.com/")[-1]:
        print("folder")
        process(data, get_dropbox_url_folder, 3)
    elif "drive.google.com" in url and "file" in url:
        process(data, get_google_url, 3)
    elif "drive.google.com" in url and "folder" in url:
        process(data, get_google_folder_url, 3)
    else:
        process(data, get_url, 5)
