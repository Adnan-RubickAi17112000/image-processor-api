import requests
import os
import glob
import pandas as pd
import concurrent.futures
import shutil
from zipfile import ZipFile 
from googledriver import download_folder


#This function hit  the image url and return the response content
def download_image(url):
    try:
        response=requests.get(url)
    except Exception as e:
        print(e)        
    return response

#This funtion is specific for the post image with hit the given post url to get the image url from the post website
def post_download_image(url):
    try:
        response=requests.get(url)
        image_url=response.text.split('"og:image" content="')[-1].split(" /")[0].replace('"',"")
        response=requests.get(image_url)
    except Exception as e:
        print(e)        
    return response

#This funtion will create the image_path and folder_path
def Image_name(document,No_of): 
    try:
        if "/" in str(document["StyleCode_Image"]):
            document["StyleCode_Image"]=str(document["StyleCode_Image"]).replace("/","_")
        image_path="Output/"
        image_path=image_path+str(document["Excel_name"])
        image_path=image_path+"/"+str(document["StyleCode_Image"])
        folder_path=image_path
        image_path=image_path+"/"+"{}_{}.{}".format(document["StyleCode_Image"],No_of,document["Image_format"].lower().replace('.',''))
    except Exception as e:
        print(e)    
    return image_path,folder_path


#create folder path for gdrive folders
def Folder_path_gdrive(document):
    try:
        if "/" in str(document["StyleCode_Image"]):
            document["StyleCode_Image"]=str(document["StyleCode_Image"]).replace("/","_")
        image_path="Output/"
        image_path=image_path+str(document["Excel_name"])
        image_path=image_path+"/"+str(document["StyleCode_Image"])
        folder_path=image_path
    except Exception as e:
        print(e)        
    return(folder_path)

def Folder_path_dropbox(document): 
    try:
        if "/" in str(document["StyleCode_Image"]):
            document["StyleCode_Image"]=str(document["StyleCode_Image"]).replace("/","_")
        image_path="Output/"
        folder_path=image_path+str(document["Excel_name"])
        image_path=folder_path+"/"+"{}.zip".format(document["StyleCode_Image"])
    except Exception as e:
        print(e)    
    return image_path,folder_path

#This funtion is to download the image from url end point.
#...Image_name
#...download_image
def get_url(document):
    try:
        print("Reach funtion direct url:",document["S.no"])
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        for index,temp in enumerate(Number_of_links):
            
            image_path,folder_path=Image_name(document,index+1)
            image_url = document[temp]
            
        
            if "http" in str(image_url):            
                Image = download_image(image_url)
                if Image.status_code == 200:
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    if not os.path.exists(image_path):
                        with open(image_path, "wb") as file:
                            file.write(Image.content)
                else:
                    print(image_url)            
        print("Completed No:",document["S.no"])
    except Exception as e:
        print(e)        

#This funtion is to download the image from dropbox url.
#...Image_name
#...download_image
def get_dropbox_url(document):
    try:
        print("Reach funtion dropbox:",document["S.no"])
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        for index,temp in enumerate(Number_of_links):
            image_path,folder_path=Image_name(document,index+1)
            image_url = document[temp].replace("dl=0","dl=1").replace(' ','%20')
            if "http" in str(image_url):
                Image = download_image(image_url)
                if Image.status_code == 200:
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                              
                    if not os.path.exists(image_path):
                        with open(image_path, "wb") as file:
                            file.write(Image.content)
                else:
                    print(image_url)             
        print("Completed No:",document["S.no"])
    except Exception as e:
        print(e)    

# This funtion is to download the folders from dropbox url as zip.
def get_dropbox_url_folder(document):
    try:
        print("Reach funtion dropbox folder:",document["S.no"])
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        for index,temp in enumerate(Number_of_links):
            image_path,folder_path=Folder_path_dropbox(document)
            image_url = document[temp].replace("dl=0","dl=1").replace(' ','%20')
            if "http" in str(image_url):
                Image = download_image(image_url)
                if Image.status_code == 200:
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                              
                    if not os.path.exists(image_path):
                        with open(image_path, "wb") as file:
                            file.write(Image.content)
                    # unzip the downloaded file
                    folder_path = folder_path
                    a = document["StyleCode_Image"]
                    with ZipFile(folder_path+"/"+a+".zip") as zObject:
                        zObject.extractall(path=folder_path+"/"+a)
                        # print("unzipped "+a)
                    # delete downloaded zip
                    paths = folder_path+"/"+a+".zip"
                    os.remove(paths)
                    # print("deleted "+a+".zip")
                    #rename sku images that dont have subfolder
                    paths = folder_path+"/"+a
                    list_subfolders_with_paths = [f.path for f in os.scandir(paths) if f.is_dir()]
                    if len(list_subfolders_with_paths) != 0:
                        shutil.rmtree(paths, ignore_errors=False)    
                        print("<<<<<<<<<<<<<<<<<<<<<<< "+document["StyleCode_Image"]+" has subfolders. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")  
                    else:      
                        filess = os.listdir(paths)
                        for files in filess:
                            if "." in files:
                                a = filess.index(files)+1
                                fsrc = paths +"/"+files
                                fdest = paths +"/"+ document["StyleCode_Image"]+"_"+str(a)+"."+document["Image_format"].lower().replace('.','')
                                os.rename(fsrc,fdest)
                        print("renamed")
                else:
                    print(image_url)   

        print("Completed No:",document["S.no"])
    except Exception as e:
        print(e)    

#This funtion is to download the image from post url.
#...Image_name
#...post_download_image
def get_post_url(document):
    try:
        print("Reach funtion post_url:",document["S.no"])
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        for index,temp in enumerate(Number_of_links):
            image_path,folder_path=Image_name(document,index+1)
            image_url = document[temp]
            if "http" in str(image_url):
                Image = post_download_image(image_url)
                if Image.status_code == 200:
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    if not os.path.exists(image_path):
                        with open(image_path, "wb") as file:
                            file.write(Image.content)
                else:
                    print(image_url)             
        print("Completed No:",document["S.no"])
    except Exception as e:
        print(e)        

#This funtion is to download the image from drive url.
#...Image_name
def get_google_url(document):
    try:
        print("Reach funtion gdrive image url:",document["S.no"])
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        for index,temp in enumerate(Number_of_links):
            image_path,folder_path=Image_name(document,index+1)
            image_url = document[temp].replace('open?id=','file/d/').replace('&usp=drive_fs','/view')
            print(image_url)
            if "drive.google.com" and "file" in str(image_url):
                file_id = image_url.split('/d/')[1].split('/')[0]
                image_url = "https://drive.google.com/uc?export=download&id={}".format(file_id)
                if "http" in str(image_url):
                    Image = download_image(image_url)
                    if Image.status_code == 200:
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                        if not os.path.exists(image_path):
                            with open(image_path, "wb") as file:
                                file.write(Image.content)
                    else:
                        print(image_url)         
            print("Completed No:",document["S.no"])
    except Exception as e:
        print(e)    
# for downloading gdrive folders
def get_google_folder_url(document):
    try:
        print("Reach funtion gdrive folder:",document["S.no"])
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        
        for index,temp in enumerate(Number_of_links):
            folder_path=Folder_path_gdrive(document)
            
            folder_url =  document[temp]
            
            if "drive.google.com" in str(folder_url) and "folders" in str(folder_url):
                
                download_folder(folder_url, folder_path)
            break
        paths = folder_path
        list_subfolders_with_paths = [f.path for f in os.scandir(paths) if f.is_dir()]
        if len(list_subfolders_with_paths) != 0:
            shutil.rmtree(paths, ignore_errors=False)    
            print("<<<<<<<<<<<<<<<<<<<<<<< "+document["StyleCode_Image"]+" has subfolders. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")  
        else:      
            filess = os.listdir(folder_path)
            for files in filess:
                if "." in files:
                    a = filess.index(files)+1
                    fsrc = folder_path +"/"+files
                    fdest = folder_path +"/"+ document["StyleCode_Image"]+"_"+str(a)+"."+document["Image_format"].lower().replace('.','')
                    os.rename(fsrc,fdest)         
                print("renamed")
        print("Completed No:",document["S.no"])    
        
    except Exception as e:
        print(e)        




    
#this function get the funtion name and the no of workers as the argument and make concurrent request
def process(datadict,funtion,worker):
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as exe:
        data=exe.map(funtion,datadict)

#This funtion will check the number of images that we get in the input and the image that has been download to Analys the missing images
def Analysis(sheetname):
    all_image_generated=0
    df=pd.read_excel("input/{}".format(sheetname))
    datadict=df.to_dict("records")
    for index,document in enumerate(datadict):
        Number_of_links=[i for i in document.keys() if "Link" in str(i)]
        for index,temp in enumerate(Number_of_links):
            if "http" in str(document[temp]):
                all_image_generated=all_image_generated+1
    all_image_cerated=glob.glob("Output/{}/**/*".format(sheetname.split(".")[0]))
    print("**********Status of {}**********\n".format(sheetname),len(all_image_cerated),all_image_generated)


# import requests
# import os
# import glob
# import pandas as pd
# import concurrent.futures
# import shutil
# from zipfile import ZipFile 
# from googledriver import download_folder
# import re

# # Sanitize folder/file names to remove invalid characters
# def sanitize_filename(name):
#     return re.sub(r'[<>:"/\\|?*\n\r]', "_", str(name))


# def download_image(url):
#     try:
#         response = requests.get(url)
#         return response
#     except Exception as e:
#         print(e)
#         return None

# /Users/Adnan/Desktop/bau/tatacliq/Tata_clique_image/Output/Image Links - UCW-12358/LUX_124601_SJSS250480HSXS
# def post_download_image(url):
#     try:
#         response = requests.get(url)
#         image_url = response.text.split('"og:image" content="')[-1].split(" /")[0].replace('"', "")
#         response = requests.get(image_url)
#         return response
#     except Exception as e:
#         print(e)
#         return None


# def Image_name(document, No_of):
#     try:
#         document["StyleCode_Image"] = sanitize_filename(document["StyleCode_Image"])
#         excel_name = sanitize_filename(document["Excel_name"])
#         image_path = os.path.join("Output", excel_name, document["StyleCode_Image"])
#         folder_path = image_path
#         file_name = "{}_{}.{}".format(document["StyleCode_Image"], No_of, document["Image_format"].lower().replace('.', ''))
#         image_path = os.path.join(image_path, file_name)
#         return image_path, folder_path
#     except Exception as e:
#         print(e)
#         return None, None


# def Folder_path_gdrive(document):
#     try:
#         document["StyleCode_Image"] = sanitize_filename(document["StyleCode_Image"])
#         excel_name = sanitize_filename(document["Excel_name"])
#         image_path = os.path.join("Output", f"Image Links - {excel_name}", document["StyleCode_Image"])
#         return image_path
#     except Exception as e:
#         print(e)
#         return None


# def Folder_path_dropbox(document):
#     try:
#         document["StyleCode_Image"] = sanitize_filename(document["StyleCode_Image"])
#         excel_name = sanitize_filename(document["Excel_name"])
#         folder_path = os.path.join("Output", excel_name)
#         zip_path = os.path.join(folder_path, f"{document['StyleCode_Image']}.zip")
#         return zip_path, folder_path
#     except Exception as e:
#         print(e)
#         return None, None


# def get_url(document):
#     try:
#         print("Reach function direct url:", document["S.no"])
#         Number_of_links = [i for i in document.keys() if "Link" in str(i)]
#         for index, temp in enumerate(Number_of_links):
#             image_path, folder_path = Image_name(document, index + 1)
#             image_url = document[temp]
#             if "http" in str(image_url):
#                 Image = download_image(image_url)
#                 if Image and Image.status_code == 200:
#                     os.makedirs(folder_path, exist_ok=True)
#                     if not os.path.exists(image_path):
#                         with open(image_path, "wb") as file:
#                             file.write(Image.content)
#                 else:
#                     print(image_url)
#         print("Completed No:", document["S.no"])
#     except Exception as e:
#         print(e)


# def get_dropbox_url(document):
#     try:
#         print("Reach function dropbox:", document["S.no"])
#         Number_of_links = [i for i in document.keys() if "Link" in str(i)]
#         for index, temp in enumerate(Number_of_links):
#             image_path, folder_path = Image_name(document, index + 1)
#             image_url = document[temp].replace("dl=0", "dl=1").replace(' ', '%20')
#             if "http" in str(image_url):
#                 Image = download_image(image_url)
#                 if Image and Image.status_code == 200:
#                     os.makedirs(folder_path, exist_ok=True)
#                     if not os.path.exists(image_path):
#                         with open(image_path, "wb") as file:
#                             file.write(Image.content)
#                 else:
#                     print(image_url)
#         print("Completed No:", document["S.no"])
#     except Exception as e:
#         print(e)


# def get_dropbox_url_folder(document):
#     try:
#         print("Reach function dropbox folder:", document["S.no"])
#         Number_of_links = [i for i in document.keys() if "Link" in str(i)]
#         for index, temp in enumerate(Number_of_links):
#             zip_path, folder_path = Folder_path_dropbox(document)
#             image_url = document[temp].replace("dl=0", "dl=1").replace(' ', '%20')
#             if "http" in str(image_url):
#                 Image = download_image(image_url)
#                 if Image and Image.status_code == 200:
#                     os.makedirs(folder_path, exist_ok=True)
#                     if not os.path.exists(zip_path):
#                         with open(zip_path, "wb") as file:
#                             file.write(Image.content)

#                     a = document["StyleCode_Image"]
#                     with ZipFile(zip_path) as zObject:
#                         zObject.extractall(path=os.path.join(folder_path, a))
#                     os.remove(zip_path)

#                     extracted_path = os.path.join(folder_path, a)
#                     subfolders = [f.path for f in os.scandir(extracted_path) if f.is_dir()]
#                     if subfolders:
#                         shutil.rmtree(extracted_path)
#                         print(f"<<<<<<<<<<<<<<<<<<<<< {a} has subfolders. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
#                     else:
#                         files = os.listdir(extracted_path)
#                         for idx, file in enumerate(files):
#                             if "." in file:
#                                 src = os.path.join(extracted_path, file)
#                                 dst = os.path.join(extracted_path, f"{a}_{idx + 1}.{document['Image_format'].lower().replace('.', '')}")
#                                 os.rename(src, dst)
#                         print("renamed")
#                 else:
#                     print(image_url)
#         print("Completed No:", document["S.no"])
#     except Exception as e:
#         print(e)


# def get_post_url(document):
#     try:
#         print("Reach function post_url:", document["S.no"])
#         Number_of_links = [i for i in document.keys() if "Link" in str(i)]
#         for index, temp in enumerate(Number_of_links):
#             image_path, folder_path = Image_name(document, index + 1)
#             image_url = document[temp]
#             if "http" in str(image_url):
#                 Image = post_download_image(image_url)
#                 if Image and Image.status_code == 200:
#                     os.makedirs(folder_path, exist_ok=True)
#                     if not os.path.exists(image_path):
#                         with open(image_path, "wb") as file:
#                             file.write(Image.content)
#                 else:
#                     print(image_url)
#         print("Completed No:", document["S.no"])
#     except Exception as e:
#         print(e)


# def get_google_url(document):
#     try:
#         print("Reach function gdrive image url:", document["S.no"])
#         Number_of_links = [i for i in document.keys() if "Link" in str(i)]
#         for index, temp in enumerate(Number_of_links):
#             image_path, folder_path = Image_name(document, index + 1)
#             image_url = document[temp].replace('open?id=', 'file/d/').replace('&usp=drive_fs', '/view')
#             if "drive.google.com" in image_url and "file" in image_url:
#                 file_id = image_url.split('/d/')[1].split('/')[0]
#                 image_url = f"https://drive.google.com/uc?export=download&id={file_id}"
#                 Image = download_image(image_url)
#                 if Image and Image.status_code == 200:
#                     os.makedirs(folder_path, exist_ok=True)
#                     if not os.path.exists(image_path):
#                         with open(image_path, "wb") as file:
#                             file.write(Image.content)
#                 else:
#                     print(image_url)
#             print("Completed No:", document["S.no"])
#     except Exception as e:
#         print(e)


# def get_google_folder_url(document):
#     try:
#         print("Reach function gdrive folder:", document["S.no"])
#         Number_of_links = [i for i in document.keys() if "Link" in str(i)]
#         for index, temp in enumerate(Number_of_links):
#             folder_path = Folder_path_gdrive(document)
#             os.makedirs(folder_path, exist_ok=True)
#             folder_url = document[temp]
#             if "drive.google.com" in str(folder_url) and "folders" in str(folder_url):
#                 download_folder(folder_url, folder_path)
#             break

#         subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
#         if subfolders:
#             shutil.rmtree(folder_path)
#             print(f"<<<<<<<<<<<<<<<<<<<<< {document['StyleCode_Image']} has subfolders. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
#         else:
#             files = os.listdir(folder_path)
#             for idx, file in enumerate(files):
#                 if "." in file:
#                     src = os.path.join(folder_path, file)
#                     dst = os.path.join(folder_path, f"{document['StyleCode_Image']}_{idx + 1}.{document['Image_format'].lower().replace('.', '')}")
#                     os.rename(src, dst)
#             print("renamed")
#         print("Completed No:", document["S.no"])
#     except Exception as e:
#         print(e)


# def process(datadict, function, worker):
#     with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as exe:
#         exe.map(function, datadict)


# def Analysis(sheetname):
#     all_image_generated = 0
#     df = pd.read_excel(f"input/{sheetname}")
#     datadict = df.to_dict("records")
#     for document in datadict:
#         links = [i for i in document.keys() if "Link" in str(i)]
#         for temp in links:
#             if "http" in str(document[temp]):
#                 all_image_generated += 1
#     all_image_created = glob.glob(f"Output/{sheetname.split('.')[0]}/**/*", recursive=True)
#     print(f"********** Status of {sheetname} **********\nDownloaded: {len(all_image_created)} / Expected: {all_image_generated}")
