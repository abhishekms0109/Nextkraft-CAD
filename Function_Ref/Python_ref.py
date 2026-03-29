import math

def calculate_parking(length, width, total_height, suv_percent, sedan_percent):
    
    # CONSTANTS
    SUV_HEIGHT = 2100
    SEDAN_HEIGHT = 1800
    HEIGHT_WASTAGE = 6900
    EXTRA_UNUSED_HEIGHT = 400
    CARS_PER_LEVEL = 2

    # STEP 1
    usable_height = total_height - HEIGHT_WASTAGE

    # STEP 2
    effective_suv_height = SUV_HEIGHT + EXTRA_UNUSED_HEIGHT
    effective_sedan_height = SEDAN_HEIGHT + EXTRA_UNUSED_HEIGHT

    # STEP 3
    total_ratio = suv_percent + sedan_percent
    suv_ratio = suv_percent / total_ratio
    sedan_ratio = sedan_percent / total_ratio

    # STEP 4
    height_for_suv = usable_height * suv_ratio
    height_for_sedan = usable_height * sedan_ratio

    # STEP 5
    suv_levels = math.floor(height_for_suv / effective_suv_height)
    sedan_levels = math.floor(height_for_sedan / effective_sedan_height)

    # STEP 6
    suv_cars = suv_levels * CARS_PER_LEVEL
    sedan_cars = sedan_levels * CARS_PER_LEVEL
    total_cars = suv_cars + sedan_cars

    # STEP 7
    actual_suv_percent = (suv_cars / total_cars) * 100 if total_cars else 0
    actual_sedan_percent = (sedan_cars / total_cars) * 100 if total_cars else 0

    return {
        "suv_levels": suv_levels,
        "sedan_levels": sedan_levels,
        "suv_cars": suv_cars,
        "sedan_cars": sedan_cars,
        "total_cars": total_cars,
        "actual_suv_percent": round(actual_suv_percent, 2),
        "actual_sedan_percent": round(actual_sedan_percent, 2)
    }