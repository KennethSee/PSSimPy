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

def is_time_later(time_str1: str, time_str2: str, or_equal: bool=False) -> bool:
    """
    Check if time_str1 is later than time_str2.
    Both time_str1 and time_str2 should be in "HH:MM" format.
    
    Parameters:
    - time_str1: A string representing the first time in 24-hour format.
    - time_str2: A string representing the second time in 24-hour format.
    
    Returns:
    - True if time_str1 is later than time_str2, False otherwise.
    """
    # Convert time strings to datetime.time objects
    format = "%H:%M"
    time1 = datetime.strptime(time_str1, format).time()
    time2 = datetime.strptime(time_str2, format).time()

    # Compare the two time objects
    if or_equal:
        return time1 >= time2
    else:
        return time1 > time2
    
    
def minutes_between(time_str1: str, time_str2: str) -> int:
    """
    Calculates the number of minutes between two time strings in 24-hour format.

    Parameters:
    - time_str1: A string representing the first time (e.g., "HH:MM").
    - time_str2: A string representing the second time (e.g., "HH:MM").

    Returns:
    - The difference in minutes as an integer. If time_str2 is earlier than time_str1,
      the result will be negative.
    """
    format = "%H:%M"
    time1 = datetime.strptime(time_str1, format)
    time2 = datetime.strptime(time_str2, format)

    # Calculate the difference between the two times
    delta = time2 - time1

    # Return the difference in minutes
    return int(delta.total_seconds() / 60)