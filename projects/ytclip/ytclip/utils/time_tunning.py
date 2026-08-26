from datetime import timedelta

DIGITS_BASES = [
    3_600 * 10 * 1_000, 
    3_600 * 1_000, 
    60 * 10 * 1_000, 
    60 * 1_000, 
    10 * 1_000, 
    1 * 1_000, 
    100, 
    10, 
    1
]

def increment_digit(value: timedelta, pos: int):
    result = value + timedelta(milliseconds=DIGITS_BASES[pos])
    print(pos, result)
  
    if result.days >= 1:
      return timedelta(days=1)
    
    return result 
    
def decrement_digit(value: timedelta, pos: int):
    result = value - timedelta(milliseconds=DIGITS_BASES[pos])
    
    print(pos, result)
    if result.days < 0:
      return timedelta(microseconds=0)
  
    return result