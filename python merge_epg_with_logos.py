import os
import xml.etree.ElementTree as ET
import requests

# المسارات
EPG_FOLDER = "Tivimate-Full-EPG-with-Logo"  # مجلد EPG
LOGO_FOLDER = "tv-logos/countries"           # مجلد الشعارات
OUTPUT_FILE = "epg_with_logos.xml"

def is_valid_logo(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def find_logo(channel_name):
    """ يبحث عن شعار مطابق لاسم القناة """
    for country in os.listdir(LOGO_FOLDER):
        country_path = os.path.join(LOGO_FOLDER, country)
        if os.path.isdir(country_path):
            for file in os.listdir(country_path):
                name, ext = os.path.splitext(file)
                if name.lower() == channel_name.lower():
                    url = f"https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/{country}/{file}"
                    if is_valid_logo(url):
                        return url
    return None

def merge_epg():
    tv_root = ET.Element("tv")

    for file in os.listdir(EPG_FOLDER):
        if file.endswith(".xml"):
            tree = ET.parse(os.path.join(EPG_FOLDER, file))
            root = tree.getroot()

            # دمج القنوات
            for channel in root.findall("channel"):
                channel_id = channel.get("id")
                if tv_root.find(f".//channel[@id='{channel_id}']") is None:
                    # إضافة شعار إذا وجد
                    display_name_elem = channel.find("display-name")
                    channel_name = display_name_elem.text if display_name_elem is not None else channel_id
                    logo_url = find_logo(channel_name)
                    if logo_url:
                        icon_elem = ET.Element("icon")
                        icon_elem.set("src", logo_url)
                        channel.append(icon_elem)

                    tv_root.append(channel)

            # دمج البرامج
            for programme in root.findall("programme"):
                tv_root.append(programme)

    tree = ET.ElementTree(tv_root)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"تم إنشاء الملف: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_epg()
