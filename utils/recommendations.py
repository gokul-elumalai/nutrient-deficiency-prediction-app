RECOMMENDATION_DB = {
    'iron': ['Spinach', 'Red meat', 'Lentils', 'Chickpeas', 'Pumpkin seeds', 'Tofu'],
    'calcium': ['Milk', 'Yogurt', 'Cheese', 'Sardines', 'Kale', 'Almonds'],
    'vitamin_c': ['Orange', 'Guava', 'Strawberries', 'Bell peppers', 'Broccoli', 'Kiwi'],
    'fiber': ['Oats', 'Chia seeds', 'Whole grains', 'Apples', 'Lentils', 'Beans'],
    'protein': ['Eggs', 'Chicken breast', 'Fish', 'Greek yogurt', 'Lentils', 'Paneer']
}


def get_food_recommendations(predictions: dict):
    recs = {}
    for key, value in predictions.items():
        if value == 1:
            nutrient = key.replace('_deficient', '')
            if nutrient in RECOMMENDATION_DB:
                recs[nutrient] = RECOMMENDATION_DB[nutrient]
    return recs
