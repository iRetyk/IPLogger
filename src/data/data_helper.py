import json
import os
from typing import Dict,List

data_file_path = os.path.join(os.path.dirname(__file__), "data.json")

DataDict = Dict[str,List[Dict[str,str]]] # Type Alias

def get_data() -> DataDict:
    with open(data_file_path, 'r') as f:
        return json.loads(f.read())


def save_data(data: DataDict):
    with open(data_file_path ,'w') as f:
        json.dump(data,f)


def record_entry(fake_url: str, packet_dict: Dict[str,str]):
    """
    register connection to fake website. note the IP, and such.
    """
    data = get_data()
    
    if fake_url in data.keys():
        data[fake_url].append(packet_dict)
    else:
        data[fake_url] = [packet_dict]

    save_data(data)

def fetch_stats(fake_url: str):
    data = get_data()
    try:
        to_return = data[fake_url]
    except:
        to_return = None
    return to_return
