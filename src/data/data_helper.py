import json
import os
from typing import Dict, List, Optional, TypedDict

# Type definitions for better type checking

# Type aliases for better readability
DataDict = Dict[str, List[Dict[str,str]]]

data_file_path = os.path.join(os.path.dirname(__file__), "data.json")

def get_data() -> DataDict:
    """
    Input: None
    Output: DataDict - Dictionary containing the application's data structure
    Purpose: Read and return data from the JSON data file
    Description: Opens and loads the JSON data file into a dictionary structure
    """
    with open(data_file_path, 'r') as f:
        return json.loads(f.read())

def save_data(data: DataDict) -> None:
    """
    Input: data (DataDict) - dictionary containing the data to save
    Output: None
    Purpose: Save data to the JSON data file
    Description: Writes the provided data dictionary to the JSON file
    """
    with open(data_file_path, 'w') as f:
        json.dump(data, f)

def record_entry(fake_url: str, packet_dict: Dict[str,str]) -> None:
    """
    Input: fake_url (str) - the shortened/fake URL, packet_dict (PacketData) - dictionary containing request information
    Output: None
    Purpose: Record a new access entry for a fake URL
    Description: Adds or updates access information for a given fake URL in the data store
    """
    data = get_data()

    if fake_url in data:
        data[fake_url].append(packet_dict)
    else:
        data[fake_url] = [packet_dict]

    save_data(data)

def fetch_stats(fake_url: str) -> Optional[List[Dict[str,str]]]:
    """
    Input: fake_url (str) - the shortened/fake URL to get statistics for
    Output: List[Dict[str,str]] or None - list of recorded entries for the URL if found, None if not found
    Purpose: Retrieve access statistics for a specific fake URL
    Description: Fetches all recorded access entries for the given fake URL from the data store
    """
    data = get_data()
    try:
        to_return = data[fake_url]
    except KeyError:
        to_return = None
    return to_return
