from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


def get_image_metadata(image_path):
  try:
    image = Image.open(image_path)
  except IOError:
    print(f"Impossible d'ouvrir le fichier : {image_path}")
    return

  exif_data = image.getexif()
  if not exif_data:
    print("Cette photo ne contient pas de métadonnées EXIF.")
    return

  date_time = None
  for tag_id, value in exif_data.items():
    if TAGS.get(tag_id) == "DateTime":
      date_time = value

  print(f"Date et heure de prise de vue : {date_time if date_time else 'Non trouvée'}")

  gps_info = {}
  try:
    gps_ifd = exif_data.get_ifd(0x8825)
    if gps_ifd:
      for tag_id, value in gps_ifd.items():
        tag_name = GPSTAGS.get(tag_id, tag_id)
        gps_info[tag_name] = value
  except AttributeError:

    pass


  if not gps_info and hasattr(image, "_getexif"):
    raw_exif = image._getexif()
    if raw_exif and 34853 in raw_exif:
      raw_gps = raw_exif[34853]
      if isinstance(raw_gps, dict):
        for tag_id, value in raw_gps.items():
          tag_name = GPSTAGS.get(tag_id, tag_id)
          gps_info[tag_name] = value

  if gps_info:
    lat = get_coordinate(gps_info, "GPSLatitude", "GPSLatitudeRef")
    lon = get_coordinate(gps_info, "GPSLongitude", "GPSLongitudeRef")
    if lat is not None and lon is not None:
      print(f"Géolocalisation (Latitude, Longitude) : {lat}, {lon}")
    else:
      print(
          f"Données GPS brutes trouvées, mais impossible de les décoder : {gps_info}"
      )
  else:
    print("Géolocalisation (GPS) : Non trouvée")


def convert_to_degrees(value):
  """Conversion du format GPS (degrés, minutes, secondes) en degrés décimaux"""
  try:
    d, m, s = value
  
    d_val = float(d[0]) / float(d[1]) if isinstance(d, tuple) else float(d)
    m_val = float(m[0]) / float(m[1]) if isinstance(m, tuple) else float(m)
    s_val = float(s[0]) / float(s[1]) if isinstance(s, tuple) else float(s)
    return d_val + (m_val / 60.0) + (s_val / 3600.0)
  except Exception:
    return None


def get_coordinate(gps_info, coord_key, ref_key):
  if coord_key in gps_info and ref_key in gps_info:
    deg = convert_to_degrees(gps_info[coord_key])
    if deg is not None:
      ref = gps_info[ref_key]
      if ref in ["S", "W"]:
        deg = -deg
      return deg
  return None


# Appel de la fonction
get_image_metadata(r"GPS\photo0.jpg")
