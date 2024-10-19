import os
import time
import requests
import logging
import importlib.util

spec = importlib.util.spec_from_file_location("config", "C:/Users/Esdesu/Documents/Материалы по обучению/Обучение Ai/Folder_confing/config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
key_ai = config.key_ai

logging.basicConfig(level=logging.INFO)

def get_job(prompt):
    url = "https://api.prodia.com/v1/sd/generate"

    payload = {
        "prompt": prompt,
        "upscale": True,
        "style_preset": "anime"
    }

    headers = {
        "accept": "application/json",
        "X-Prodia-Key": key_ai
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return None

    res = response.json()
    res_job = res.get('job')
    logging.info(f'Job created: {res_job}')
    return res_job

def get_image_url(job):
    url = f"https://api.prodia.com/v1/job/{job}"

    headers = {
        "accept": "application/json",
        "X-Prodia-Key": key_ai
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return None, None
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return None, None

    res = response.json()
    url = res.get('imageUrl')
    status = res.get('status')
    logging.info(f'Image URL: {url}, Status: {status}')
    return url, status

def save_url(url, file_path):
    if os.path.exists(file_path):
        logging.info('Image file already exists. Skipping download.')
        return

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return

    with open(file_path, 'wb') as sv:
        for block in response.iter_content(1024):
            if not block:
                break
            sv.write(block)
    logging.info('Image saved as image.png')

def main(prompt):
    token_name = get_job(prompt)
    if not token_name:
        logging.error('Failed to create job.')
        return

    status = 'generating'
    status_s = 'succeeded'

    while status == 'generating':
        url, status = get_image_url(token_name)
        time.sleep(10)

    if status == status_s:
        file_path = os.path.join(os.path.dirname(__file__), 'image.png')
        print(url)
        save_url(url, file_path)
    else:
        logging.error(f'Error: {status}')

if __name__ == '__main__':
    main('pony')
