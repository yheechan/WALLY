def find_max(numbers):
    if not numbers:
        raise ValueError("empty list")
    max_number = numbers[0]
    for number in numbers[1:]:
        if number > max_number:
            max_number = number
    return max_number