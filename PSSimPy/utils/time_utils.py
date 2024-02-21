from datetime import datetime, timedelta
import re


def is_valid_24h_time(time_str):
    # Regular expression to match a 24-hour time format
    pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
    
    # Use re.match to check if the time_str matches the pattern
    if re.match(pattern, time_str):
        return True
    else:
        return False


def add_minutes_to_time(time_str: str, minutes: int) -> str:
    # Parse the input string into a datetime object
    time_obj = datetime.strptime(time_str, '%H:%M')
    
    # Add the minutes to the time
    new_time_obj = time_obj + timedelta(minutes=minutes)
    
    # Format the new datetime object back into a string
    new_time_str = new_time_obj.strftime('%H:%M')
    
    return new_time_str