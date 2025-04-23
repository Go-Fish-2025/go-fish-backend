import base64
import hashlib
import os
from datetime import datetime

import requests
from flask import jsonify, Blueprint, request

fish_bp = Blueprint('fish', __name__)

API_KEY_ID = ""
API_SECRET_KEY = ""

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_md5_checksum_base64(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
        md5_digest = hashlib.md5(file_data).digest()
        base64_md5 = base64.b64encode(md5_digest).decode('utf-8')
        return base64_md5

def get_access_token():
    url = "https://api-users.fishial.ai/v1/auth/token"
    headers = {'Content-Type': 'application/json'}
    data = {
        "client_id": API_KEY_ID,
        "client_secret": API_SECRET_KEY
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Failed to get access token")


def get_upload_url(access_token, filename, mime_type, byte_size, checksum):
    url = "https://api.fishial.ai/v1/recognition/upload"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "blob": {
            "filename": filename,
            "content_type": mime_type,
            "byte_size": byte_size,
            "checksum": checksum
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to get upload URL")


def upload_image_to_signed_url(signed_url, image_path, headers):
    with open(image_path, 'rb') as image_file:
        response = requests.put(signed_url, headers=headers, data=image_file)
    if response.status_code != 200:
        raise Exception("Failed to upload image")
    return response


def recognize_fish(access_token, signed_id):
    url = f"https://api.fishial.ai/v1/recognition/image?q={signed_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to recognize fish")


def extract_fish_details(fish):
    def get_val(obj, key, default="Unknown"):
        return obj.get(key, default) if isinstance(obj, dict) else default

    def format_weight(weight_grams):
        if not weight_grams or weight_grams == "Unknown":
            return "Unknown"
        lbs = float(weight_grams) * 0.00220462
        return f"{int(lbs)} lb {int((lbs - int(lbs)) * 16)} oz ({weight_grams} g)"

    def format_date(ts):
        if not ts or ts == "Unknown":
            return "Unknown"
        return datetime.utcfromtimestamp(ts).strftime('%b %d, %Y')

    def rgba_to_hex(color_dict):
        r = color_dict.get("r", 0)
        g = color_dict.get("g", 0)
        b = color_dict.get("b", 0)
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    fish_data = fish.get("fishangler-data", {})
    record = fish_data.get("igfaWeightRecord", {}).get("record", {})
    weight_record = get_val(record, "weight", "0")

    return {
        "name": get_val(fish_data, "title"),
        "scientific_name": get_val(fish_data, "scientificName"),
        "common_names": get_val(fish_data, "commonNames", ""),
        "taxonomy": {
            "family": get_val(fish_data, "family"),
            "genus": get_val(fish_data, "genus"),
            "class": get_val(fish_data, "class"),
            "order": get_val(fish_data, "order"),
            "kingdom": get_val(fish_data, "kingdom"),
            "phylum": get_val(fish_data, "phylum"),
        },
        "color": {
            "dominant_color": rgba_to_hex(get_val(fish_data.get("photo", {}), "dominantColor")),
            "coloration": get_val(fish_data, "coloration"),
        },
        "size_and_lifespan": {
            "common_length": get_val(fish_data, "commonLength", "Unknown"),
            "maximum_length": get_val(fish_data, "length", "Unknown"),
            "weight_record": format_weight(weight_record),
            "lifespan": get_val(fish_data, "longevityWild", "Unknown"),
            "reproduction": get_val(fish_data, "reproduction", "Unknown"),
        },
        "habitat_and_range": {
            "habitat": get_val(fish_data, "environmentDetail"),
            "depth_range": f"{get_val(fish_data, 'depthRangeShallow', 'Unknown')}-{get_val(fish_data, 'depthRangeDeep', 'Unknown')} ft",
            "distribution": get_val(fish_data, "distribution")
        },
        "feeding_and_food_value": {
            "diet": get_val(fish_data, "feedingBehavior"),
            "food_value": get_val(fish_data, "foodValue"),
            "health_warnings": get_val(fish_data, "healthWarnings")
        },
        "appearance_and_anatomy": get_val(fish_data, "description"),
        "handling_and_conservation": {
            "handling_tip": get_val(fish_data, "handlingInstructions"),
            "conservation_status": get_val(fish_data, "conservation")
        },
        "record_catch": {
            "angler": get_val(record, "anglerName"),
            "location": get_val(record, "place"),
            "type": "IGFA Weight Record",
            "weight": format_weight(weight_record),
            "date": format_date(get_val(record, "dateTime"))
        },
        "image_url": get_val(fish_data.get("photo", {}), "mediaUri")
    }


@fish_bp.route('/identify', methods=['POST'])
def upload_fish_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    mime_type = file.content_type
    byte_size = os.path.getsize(file_path)
    checksum = get_md5_checksum_base64(file_path)

    try:
        access_token = get_access_token()

        upload_url_data = get_upload_url(access_token, filename, mime_type, byte_size, checksum)

        signed_url = upload_url_data['direct-upload']['url']
        headers = upload_url_data['direct-upload']['headers']

        upload_image_to_signed_url(signed_url, file_path, headers)

        signed_id = upload_url_data['signed-id']
        recognition_data = recognize_fish(access_token, signed_id)

        os.remove(file_path)

        if recognition_data['results'] is not None and len(recognition_data['results']) > 0:
            return jsonify({
                "Confidence": recognition_data['results'][0]['detection-score'],
                "Details": extract_fish_details(recognition_data['results'][0]['species'][0]),
            })

        else:
            return jsonify({'error': 'Unable to identify fish'}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


