from main import search_properties
import json

# Test with area and year filters
print("Testing Advanced Search...")
result = search_properties.invoke({
    "location": "Houston",
    "min_price": 0,
    "max_price": 10000000,
    "min_area": 1000,
    "min_year": 1980
})

print(result)
