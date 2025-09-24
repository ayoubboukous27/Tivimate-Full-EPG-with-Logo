import os
import requests
import xml.etree.ElementTree as ET
from io import BytesIO
from zipfile import ZipFile

# روابط الريبو
EPG_REPO_ZIP = "https://github.com/ayoubboukous27/Tivimate-Full-EPG-with-Logo/archive/refs/heads/main.zip"
LOGO_REPO = "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries"

OUTPUT_FILE = "epg_with_logos.xml"

def is_valid_logo(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def download_and_extract_epg():
    r = requests.get(EPG_REPO_ZIP)
    r.raise_for_status()
    zipfile = ZipFile(BytesIO(r.content))
    zipfile.extractall("epg_repo")
    # يرجع المجلد الرئيسي داخل zip
    return os.path.join("epg_repo", os.listdir("epg_repo")[0])

def find_logo(channel_name):
    for country in requests.get(f"{LOGO_REPO}/").text.splitlines():
        # طريقة أساسية للتأكد من تطابق الاسم (يمكن تحسينها لاحقًا)
        url = f"{LOGO_REPO}/{country}/{channel_name}.png"
        if is_valid_logo(url):
            return url
    return None

def merge_epg(epg_folder):
    tv_root = ET.Element("tv")

    for root, dirs, files in os.walk(epg_folder):
        for file in files:
            if file.endswith(".xml"):
                tree = ET.parse(os.path.join(root, file))
                root_xml = tree.getroot()

                # دمج القنوات
                for channel in root_xml.findall("channel"):
                    channel_id = channel.get("id")
                    if tv_root.find(f".//channel[@id='{channel_id}']") is None:
                        display_name_elem = channel.find("display-name")
                        channel_name = display_name_elem.text if display_name_elem is not None else channel_id
                        # إضافة شعار
                        logo_url = find_logo(channel_name)
                        if logo_url:
                            icon_elem = ET.Element("icon")
                            icon_elem.set("src", logo_url)
                            channel.append(icon_elem)
                        tv_root.append(channel)

                # دمج البرامج
                for programme in root_xml.findall("programme"):
                    tv_root.append(programme)

    tree = ET.ElementTree(tv_root)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"تم إنشاء الملف: {OUTPUT_FILE}")

if __name__ == "__main__":
    epg_folder = download_and_extract_epg()
    merge_epg(epg_folder)
