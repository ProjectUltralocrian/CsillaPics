import urllib.request as rq
import concurrent.futures
import csv
from dataclasses import dataclass

"""
The DownloadOptions data class stores the options selected by the user for building the URL and downloading the images.
Properties: url (the full url submitted), filename (the starting string of the target filenames, the selected exteriors 
(colours), whether the downloaded images should be exterior or interior and whether the given URL or custom parameters
should be used.
"""


@dataclass
class DownloadOptions:
    url: str
    filename: str
    exterior: [str]
    interior_selected: bool
    customize: bool


"""
The URL_structure class contains all the necessary data fields for building and processing the url for downloading the
images, based on the options submitted by the user via the UI (received via the parameters). 
"""


class URL_structure:
    def __init__(self, url, interior_selected, selected_exterior, customize):
        try:
            url_parts = url.split("&")
            if len(url_parts) < 13 or "producttoken" not in url:
                raise ValueError
        except Exception:
            raise ValueError
        self.host = url_parts[0]
        self.country = url_parts[1]
        self.model_token = url_parts[2]
        self.vehicle_token = url_parts[3]
        if customize:
            self.exterior = f"exterior={exteriors[selected_exterior]}"
            self.exterior_name = selected_exterior
        else:
            self.exterior = url_parts[4]
            self.exterior_name = "XXXX"
        self.upholstery = url_parts[5]
        match interior_selected:
            case False:
                self.view = "view=exterior"
            case True:
                self.view = "view=interior"
        # self.view = url.split("&")[6]
        self.angle = url_parts[7]
        self.format = url_parts[8]
        self.mode = url_parts[9]
        self.image_quality = "image-quality=100"
        # self.image_quality = url.split("&")[10]
        self.scale_mode = "scale-mode=0"
        # self.scale_mode = url.split("&")[11]
        if "accessor" in url:
            self.accessory = f"accessory={(url.split('accessory=')[1]).split('&')[0]}"
        else:
            self.accessory = ""
        if "width" in url:
            width = (url.split("width=")[1]).split("&")[0]
            height = (url.split("height=")[1]).split("&")[0]
            self.widthheight = f"width={width}&height={height}"
        else:
            self.widthheight = ""
        self.more_info = url_parts[-1]


"""
Helper function to build the url based on the selected camera angle.
"""


def create_full_url(full_url, angle):
    return (f"{full_url.host}&{full_url.country}&{full_url.model_token}&{full_url.vehicle_token}" +
            f"&{full_url.exterior}&{full_url.upholstery}&{full_url.view}&angle={angle}&{full_url.format}" +
            f"&{full_url.mode}&{full_url.image_quality}&{full_url.scale_mode}&{full_url.widthheight}" +
            f"&{full_url.accessory}&{full_url.more_info}")


"""
Builds the list of urls and filenames for downloading the images, based on the download options selected by the user and passed in 
to this module from the UI via the download_options object. Loops through all the relevant camera angles and returns
a list of tuples, which contains the url and corresponding filename.
"""


def build_list_of_urls_to_download(download_options):
    urls_to_download = []
    for selection in download_options.exterior:
        if download_options.customize and selection == '': continue
        full_url = URL_structure(download_options.url, download_options.interior_selected, selection,
                                 download_options.customize)
        angles_ext = ["00", "02", "04", "06", "09", "12", "15", "18", "21", "24", "27", "30", "33"]
        angles_int = ["00", "01", "02"]
        if download_options.interior_selected:
            for angle in angles_int:
                url = create_full_url(full_url, angle)
                file_name = f"{download_options.filename}_{full_url.exterior_name}_int_{angle}.png"
                urls_to_download.append((url, file_name))
        else:
            for angle in angles_ext:
                url = create_full_url(full_url, angle)
                file_name = f"{download_options.filename}_{full_url.exterior_name}_ext_{angle}.png"
                urls_to_download.append((url, file_name))
        if selection == '': return urls_to_download

    return urls_to_download


"""
Builds a dictionary based on the configuration file (exteriors.csv), which maps the model codes to the corresponding url 
tokens. The returned map is used by the URL_structure __init__ method to retrieve the requested exterior and build the url.
"""


def get_exteriors_from_csv():
    exteriors = {}

    with open('exteriors.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if not idx == 0 and not row[0] == '' and not row[1] == '':
                exteriors[row[0]] = row[1]

    return exteriors


"""
Helper function returning the list of exterior codes (keys).
"""


def get_list_of_exterior_codes():
    codes = []
    for k, v in get_exteriors_from_csv().items():
        codes.append(k)
    return codes


"""
Exteriors variable storing the list of exterior codes, used by the UI for building the list in the combo boxes.
"""
exteriors = get_exteriors_from_csv()

"""
After receiving the list of urls and filenames, based on the download_options parameter, the function asyncronously
retrieves the selected images and saves them with the corresponding file names.
"""


def get_files(download_options):
    urls = [url for (url, filename) in build_list_of_urls_to_download(download_options)]
    file_names = [filename for (url, filename) in build_list_of_urls_to_download(download_options)]
    # ASYNC!!
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #    executor.map(rq.urlretrieve, urls, file_names)

    # SYNCRONOUS VERSION:
    for idx, url in enumerate(urls):
        rq.urlretrieve(url, file_names[idx])  # f"{idx}.png")

    # Printing for debug purposes only...
    # print(urls)
    # print(file_names)
