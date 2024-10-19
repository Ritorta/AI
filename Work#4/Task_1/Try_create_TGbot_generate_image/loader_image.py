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

def get_job(prompt, preset):
    url = "https://api.prodia.com/v1/sd/generate"

    payload = {
        "prompt": prompt,
        "upscale": True,
        "style_preset": f"{preset}"
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

    dir_image = os.path.join(os.path.dirname(__file__), 'folder_for_ai_image')
    os.makedirs(dir_image, exist_ok=True)

    base_name, ext = os.path.splitext(file_path)
    i = 1

    while True:
        full_file_path = os.path.join(dir_image, f"{base_name}_{i}{ext}")
        if not os.path.exists(full_file_path):
            break
        i += 1

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return

    with open(full_file_path, 'wb') as sv:
        for block in response.iter_content(1024):
            if not block:
                break
            sv.write(block)
    logging.info(f'Image saved as {file_path}')


def start(prompt, preset):
    token_name = get_job(prompt, preset)
    if not token_name:
        logging.error('Failed to create job.')
        return

    status = 'generating'
    status_s = 'succeeded'

    while status == 'generating':
        url, status = get_image_url(token_name)
        time.sleep(10)

    if status == status_s:
        file_path = f'{prompt}.png'
        print(url)
        save_url(url, file_path)
    else:
        logging.error(f'Error: {status}')

    return url


if __name__ == '__main__':
    start('pony', 'name_preset')
