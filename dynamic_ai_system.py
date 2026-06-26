"""
Dynamic AI Response System - Gives different answers each time
"""

import random

# Global conversation tracker
conversation_tracker = {}

def get_dynamic_response(user_id, message):
    """Main function that gives varied responses based on conversation history"""
    
    # Track user conversation
    if user_id not in conversation_tracker:
        conversation_tracker[user_id] = {'count': 0, 'topics': []}
    
    conversation_tracker[user_id]['count'] += 1
    count = conversation_tracker[user_id]['count']
    
    message_lower = message.lower().strip()
    
    # Equipment requests - different responses each time
    if any(word in message_lower for word in ['tractor', 'harvester', 'equipment', 'rent', 'hire']):
        return get_equipment_response(message_lower, count)
    
    # Crop problems - varied solutions
    if any(word in message_lower for word in ['yellow', 'disease', 'pest', 'problem', 'dying']):
        return get_crop_problem_response(message_lower, count)
    
    # Planting advice - different each time
    if any(word in message_lower for word in ['plant', 'sow', 'seed', 'when to plant']):
        return get_planting_response(message_lower, count)
    
    # Harvesting - varied timing advice
    if any(word in message_lower for word in ['harvest', 'when to harvest', 'ready']):
        return get_harvesting_response(message_lower, count)
    
    # Fertilizer - different recommendations
    if any(word in message_lower for word in ['fertilizer', 'nutrition', 'urea', 'dap']):
        return get_fertilizer_response(message_lower, count)
    
    # Irrigation - varied methods
    if any(word in message_lower for word in ['water', 'irrigation', 'drip', 'sprinkler']):
        return get_irrigation_response(message_lower, count)
    
    # Weather/season - different seasonal advice
    if any(word in message_lower for word in ['weather', 'season', 'monsoon', 'winter']):
        return get_weather_response(message_lower, count)
    
    # Soil - varied soil advice
    if any(word in message_lower for word in ['soil', 'ph', 'testing', 'preparation']):
        return get_soil_response(message_lower, count)
    
    # Pricing - different cost perspectives
    if any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap']):
        return get_pricing_response(message_lower, count)
    
    # Greetings - varied welcomes
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'namaste']):
        return get_greeting_response(count)
    
    # Default varied responses
    return get_default_response(count)

def get_equipment_response(message, count):
    """Equipment responses that change each time"""
    
    if 'rice' in message:
        responses = [
            "For rice farming, you'll need a rice transplanter (₹800/day) and mini tractor (₹600/day). Which stage are you at?",
            "Rice equipment: Transplanting machine saves labor, combine harvester for efficient harvest. What's your field size?",
            "Rice farming tools: Puddling tractor, transplanter, harvester. Manual vs machine depends on your budget.",
            "Rice cultivation needs: Land preparation tractor, seedling transplanter, threshing machine. Which operation first?"
        ]
    elif 'wheat' in message:
        responses = [
            "Wheat farming: Seed drill (₹500/day) for sowing, combine harvester (₹1000/day) for harvest. What do you need?",
            "For wheat: Tractor for field prep, precision seed drill, harvester. When are you planning to sow?",
            "Wheat equipment: Cultivator for land prep, seed drill for uniform sowing, harvester for clean grain.",
            "Wheat machinery: Deep plowing tractor, seed cum fertilizer drill, combine harvester. Which stage?"
        ]
    elif 'cotton' in message:
        responses = [
            "Cotton farming: Heavy tractor for deep plowing (₹700/day), cotton picker for harvest (₹1500/day).",
            "Cotton equipment: Land preparation tractor, seed drill, cotton harvesting machine. What's your priority?",
            "For cotton: Deep cultivation tractor, precision planter, mechanical cotton picker. Which operation?"
        ]
    else:
        responses = [
            "Which crop are you growing? I'll recommend the right equipment with current rental rates.",
            "Tell me your crop and field size - I'll suggest the most suitable equipment options.",
            "Equipment depends on crop type and farming stage. What are you planning to cultivate?",
            "I can help with tractors, harvesters, seeders for any crop. What's your farming plan?"
        ]
    
    return responses[count % len(responses)]

def get_crop_problem_response(message, count):
    """Crop problem responses with different solutions"""
    
    if 'yellow' in message:
        if 'rice' in message:
            responses = [
                "Rice yellowing = nitrogen deficiency. Apply 25kg urea/acre immediately. Check drainage too.",
                "Yellow rice leaves indicate nutrient shortage. Use urea and ensure proper water management.",
                "Rice turning yellow? Usually nitrogen deficiency or waterlogging. Apply fertilizer and improve drainage.",
                "Rice yellowing suggests nitrogen lack or poor drainage. Apply urea 25kg/acre, check field water level."
            ]
        elif 'wheat' in message:
            responses = [
                "Wheat yellowing = rust disease or nutrients. Spray Propiconazole, apply DAP 50kg/acre.",
                "Yellow wheat suggests rust or deficiency. Use fungicide spray and phosphorus fertilizer.",
                "Wheat turning yellow? Could be rust disease or nutrient deficiency. Spray fungicide, add fertilizer."
            ]
        else:
            responses = [
                "Yellowing usually means nitrogen deficiency. Which crop? I'll give specific treatment.",
                "Yellow leaves indicate nutrient issues or disease. Tell me the crop for exact solution.",
                "Yellowing can be nutrients, disease, or water stress. What crop are we dealing with?"
            ]
    elif 'pest' in message:
        responses = [
            "Pest control: Start with neem oil 5ml/liter. Which crop and what pests are you seeing?",
            "For pests: Use integrated approach - neem oil, pheromone traps. What's the crop?",
            "Pest management: Identify pest first, then targeted treatment. Which crop is affected?",
            "Pest issues: Neem spray, beneficial insects, pheromone traps work well. What pests do you see?"
        ]
    else:
        responses = [
            "Describe the problem: yellowing, spots, wilting? I'll diagnose and suggest treatment.",
            "What symptoms are you seeing? I can identify the issue and recommend solutions.",
            "Tell me the crop and symptoms - I'll help identify and treat the problem."
        ]
    
    return responses[count % len(responses)]

def get_planting_response(message, count):
    """Planting advice with seasonal variations"""
    
    if 'rice' in message:
        responses = [
            "Rice planting: June-July with monsoon. 20-25kg seeds/acre, maintain 2-3 inches water.",
            "Rice sowing: Nursery in May-June, transplant after 25 days. Keep standing water.",
            "Rice timing: Plant with first monsoon rains. Use 20kg seeds/acre for transplanting.",
            "Rice cultivation: Start nursery before monsoon, transplant in flooded fields after 3-4 weeks."
        ]
    elif 'wheat' in message:
        responses = [
            "Wheat sowing: November-December. 40-50kg seeds/acre, 2-3cm depth, 20cm rows.",
            "Wheat planting: After rice harvest, November ideal. Ensure soil moisture before sowing.",
            "Wheat timing: Late November to early December. Use seed drill for uniform spacing.",
            "Wheat cultivation: Sow after Diwali, 45kg seeds/acre, maintain proper row spacing."
        ]
    else:
        responses = [
            "Which crop are you planting? I'll give specific timing, seed rate, and techniques.",
            "Planting advice depends on crop and season. What are you planning to grow?",
            "Tell me the crop - I'll provide sowing time, seed rate, and best practices."
        ]
    
    return responses[count % len(responses)]

def get_harvesting_response(message, count):
    """Harvesting guidance with different timing tips"""
    
    if 'rice' in message:
        responses = [
            "Rice harvest: 120-150 days when grains turn golden. Cut at 20-25% moisture.",
            "Rice ready when panicles bend down, grains firm. Use combine harvester for efficiency.",
            "Rice harvesting: Check grain hardness, golden color. Early morning cutting reduces loss.",
            "Rice maturity: Grains turn golden, panicles heavy. Harvest at proper moisture for quality."
        ]
    elif 'wheat' in message:
        responses = [
            "Wheat harvest: 120-130 days when grains hard. Best at 12-14% moisture.",
            "Wheat ready when ears golden, grains firm. Harvest in cool morning hours.",
            "Wheat maturity: Golden color, hard grains. Cut early morning to avoid shattering."
        ]
    else:
        responses = [
            "Which crop are you harvesting? I'll tell you exact timing and best methods.",
            "Harvest timing varies by crop. Tell me what you're growing for specific advice.",
            "Different crops have different harvest signs. What crop needs harvesting guidance?"
        ]
    
    return responses[count % len(responses)]

def get_fertilizer_response(message, count):
    """Fertilizer advice with different nutrient focus"""
    
    responses = [
        "Fertilizer needs: NPK 120:60:40 kg/acre for most crops. Which crop needs advice?",
        "Balanced nutrition: Urea for nitrogen, DAP for phosphorus. Apply in splits. What crop?",
        "Fertilizer timing: Basal dose at planting, top dressing during growth. Which crop?",
        "Nutrient management: Soil test first, then balanced NPK application. What's your crop?"
    ]
    return responses[count % len(responses)]

def get_irrigation_response(message, count):
    """Irrigation advice with method comparisons"""
    
    if 'drip' in message:
        responses = [
            "Drip irrigation: Saves 40% water, costs ₹50,000/acre. Best for vegetables, fruits.",
            "Drip system: High initial cost but water-efficient. Suitable for high-value crops.",
            "Drip irrigation: Precise water application, reduces weeds. Good for water-scarce areas."
        ]
    else:
        responses = [
            "Irrigation methods: Drip (water-saving), sprinkler (field crops), flood (rice). Which interests you?",
            "Water management: Early morning/evening irrigation. Check soil moisture at 6-inch depth.",
            "Irrigation timing: Water when soil feels dry at finger depth. Avoid midday watering.",
            "Water application: Deep, less frequent watering better than shallow, frequent watering."
        ]
    return responses[count % len(responses)]

def get_weather_response(message, count):
    """Weather and seasonal advice variations"""
    
    responses = [
        "Seasonal crops: Kharif (June-Oct) rice/cotton, Rabi (Nov-Apr) wheat/mustard. What season?",
        "Weather planning: Monsoon crops need drainage, winter crops need irrigation. Which season?",
        "Crop calendar: Summer prep, monsoon planting, winter sowing, spring harvest. What's your plan?",
        "Season planning: Kharif with rains, Rabi with irrigation, Zaid with intensive care. Which season?"
    ]
    return responses[count % len(responses)]

def get_soil_response(message, count):
    """Soil management with different focus areas"""
    
    responses = [
        "Soil health: Test pH every 2 years (ideal 6.0-7.5). Add organic matter 2-3 tons/acre.",
        "Soil preparation: Deep plowing before monsoon, add compost, check nutrient levels.",
        "Soil management: pH testing, organic matter, proper drainage. What's your soil type?",
        "Soil improvement: Regular testing, organic inputs, crop rotation. What's your main concern?"
    ]
    return responses[count % len(responses)]

def get_pricing_response(message, count):
    """Pricing with different cost perspectives"""
    
    responses = [
        "Equipment rates: Mini tractor ₹500-700/day, Harvester ₹1000-1500/day. Varies by location.",
        "Rental costs: Tractor ₹600/day, Seed drill ₹400/day, Sprayer ₹300/day. What equipment?",
        "Pricing factors: Equipment type, duration, location, season. Which equipment interests you?",
        "Cost comparison: Buying vs renting depends on usage frequency. What's your requirement?"
    ]
    return responses[count % len(responses)]

def get_greeting_response(count):
    """Varied greeting responses"""
    
    responses = [
        "Hello! What farming challenge can I help you solve today?",
        "Hi there! Ready to assist with your agricultural needs.",
        "Namaste! I'm your farming expert - what's on your mind?",
        "Good to see you! What crop or equipment question do you have?",
        "Welcome! How can I help with your farming today?",
        "Hello farmer! What agricultural advice do you need?"
    ]
    return responses[count % len(responses)]

def get_default_response(count):
    """Default responses with variety"""
    
    responses = [
        "I can help with any farming question! What specific challenge are you facing?",
        "Tell me about your farming situation - crop type, land size, or current issue?",
        "What would you like to know? I cover equipment, crops, diseases, planting, and more.",
        "I'm here for all your agricultural needs. What's your main concern right now?",
        "Ask me anything about farming - I'm here to help with practical solutions!",
        "What farming topic interests you? Equipment, crops, problems, or techniques?"
    ]
    return responses[count % len(responses)]