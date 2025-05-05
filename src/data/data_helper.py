import json
import os

data_file_path = os.path.join(os.path.dirname(__file__), "data.json")

def get_data() -> dict[str,list[dict]]:
    with open(data_file_path, 'r') as f:
        return json.loads(f.read())


def save_data(data : dict[str,list[dict]]):
    with open(data_file_path ,'w') as f:
        json.dump(data,f)


def record_entry(fake_url: str, packet_dict: dict):
    """
    register connection to fake website. note the IP, and such.
    """
    data = get_data()

    #data[fake_url].append(packet_dict)

    save_data(data)

def fetch_stats(fake_url: str) -> list[dict]:
    data = get_data()

    return data[fake_url]
