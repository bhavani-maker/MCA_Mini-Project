"""
Enhanced AI Response System for Comprehensive Farming Questions
"""

def generate_comprehensive_response(message):
    """Handle any farming question a farmer might ask"""
    message_lower = message.lower().strip()
    
    # Equipment requests
    if any(word in message_lower for word in ['tractor', 'harvester', 'equipment', 'rent', 'hire', 'need']):
        return handle_equipment_queries(message_lower)
    
    # Crop problems
    if any(word in message_lower for word in ['yellow', 'disease', 'pest', 'problem', 'dying', 'wilting']):
        return handle_crop_problems(message_lower)
    
    # Planting advice
    if any(word in message_lower for word in ['plant', 'sow', 'seed', 'when to plant', 'how to plant']):
        return handle_planting_queries(message_lower)
    
    # Harvesting advice
    if any(word in message_lower for word in ['harvest', 'when to harvest', 'ready']):
        return handle_harvesting_queries(message_lower)
    
    # Fertilizer questions
    if any(word in message_lower for word in ['fertilizer', 'nutrition', 'urea', 'dap', 'nutrients']):
        return handle_fertilizer_queries(message_lower)
    
    # Irrigation questions
    if any(word in message_lower for word in ['water', 'irrigation', 'drip', 'sprinkler']):
        return handle_irrigation_queries(message_lower)
    
    # Weather and season
    if any(word in message_lower for word in ['weather', 'season', 'monsoon', 'winter', 'summer']):
        return handle_weather_queries(message_lower)
    
    # Soil questions
    if any(word in message_lower for word in ['soil', 'ph', 'testing', 'preparation']):
        return handle_soil_queries(message_lower)
    
    # Pricing questions
    if any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap', 'budget']):
        return handle_pricing_queries(message_lower)
    
    # General farming
    return "I'm here to help with any farming question! Ask me about crops, equipment, diseases, planting, harvesting, fertilizers, irrigation, or costs."

def handle_equipment_queries(message):
    """Handle all equipment-related questions"""
    if 'rice' in message:
        return "For rice farming: Rice transplanter (₹800/day), Mini tractor for puddling (₹600/day), Combine harvester (₹1200/day). Which stage are you at?"
    elif 'wheat' in message:
        return "For wheat: Seed drill for sowing (₹500/day), Tractor for field prep (₹700/day), Combine harvester (₹1000/day). What do you need?"
    elif 'cotton' in message:
        return "For cotton: Tractor for land prep (₹700/day), Cotton picker for harvest (₹1500/day), Cultivator for weeding (₹400/day)."
    elif 'tomato' in message:
        return "For tomato: Mini tractor (₹500/day), Sprayer for pest control (₹300/day), Drip irrigation system (₹200/day)."
    else:
        return "I can recommend equipment for any crop! Tell me which crop you're growing and what farming activity you need help with."

def handle_crop_problems(message):
    """Handle crop disease and pest issues"""
    if 'yellow' in message:
        if 'rice' in message:
            return "Yellow rice leaves = nitrogen deficiency. Apply 25kg urea/acre immediately. Check drainage - waterlogged fields cause yellowing."
        elif 'wheat' in message:
            return "Wheat yellowing = rust disease or nutrient deficiency. Spray Propiconazole 1ml/liter. Apply DAP 50kg/acre."
        elif 'tomato' in message:
            return "Yellow tomato leaves = overwatering or early blight. Reduce watering. Spray Mancozeb 2g/liter."
        else:
            return "Yellowing usually means nitrogen deficiency or overwatering. Which crop are you dealing with?"
    
    elif 'pest' in message:
        return "For pest control: Start with neem oil 5ml/liter. Use pheromone traps. Which crop and what pests are you seeing?"
    
    elif 'disease' in message:
        return "Common diseases: Fungal (spray fungicide), bacterial (copper spray), viral (remove infected plants). Which crop is affected?"
    
    else:
        return "Describe the problem: yellowing leaves, spots, wilting, pest damage? I'll give specific treatment advice."

def handle_planting_queries(message):
    """Handle planting and sowing questions"""
    if 'rice' in message:
        return "Rice planting: June-July with monsoon. 20-25kg seeds/acre. 2-3 inches water depth. Transplant 20-25 day seedlings."
    elif 'wheat' in message:
        return "Wheat sowing: November-December. 40-50kg seeds/acre. 2-3cm depth, 20cm row spacing. Good soil moisture needed."
    elif 'cotton' in message:
        return "Cotton planting: April-May. 1-2kg seeds/acre. 45cm row spacing. Plant after last frost."
    elif 'tomato' in message:
        return "Tomato: Start nursery June-July. Transplant after 4-5 weeks. 60cm plant spacing. Provide support stakes."
    else:
        return "Which crop are you planting? I'll give specific timing, seed rate, and planting techniques."

def handle_harvesting_queries(message):
    """Handle harvesting questions"""
    if 'rice' in message:
        return "Rice harvest: 120-150 days when grains turn golden. Cut at 20-25% moisture. Use combine harvester for efficiency."
    elif 'wheat' in message:
        return "Wheat harvest: 120-130 days when grains are hard. Harvest at 12-14% moisture. Best time: early morning."
    elif 'cotton' in message:
        return "Cotton harvest: 180-200 days. Pick when bolls are fully open and white. Multiple pickings needed."
    else:
        return "Which crop are you harvesting? I'll tell you exact timing and best harvesting methods."

def handle_fertilizer_queries(message):
    """Handle fertilizer and nutrition questions"""
    if 'rice' in message:
        return "Rice fertilizer: NPK 120:60:40 kg/acre. Apply urea in 3 splits. Use DAP as basal dose."
    elif 'wheat' in message:
        return "Wheat fertilizer: NPK 120:60:40 kg/acre. Full P&K + 1/3 N at sowing. Remaining N in 2 splits."
    else:
        return "General fertilizer: NPK 120:60:40 kg/acre for most crops. Apply in 2-3 splits. Which crop needs advice?"

def handle_irrigation_queries(message):
    """Handle water and irrigation questions"""
    if 'drip' in message:
        return "Drip irrigation: Saves 40% water. Best for vegetables, fruits. Initial cost ₹50,000/acre but saves long-term."
    elif 'sprinkler' in message:
        return "Sprinkler irrigation: Good for field crops. Covers large area. Cost ₹30,000/acre setup."
    else:
        return "Irrigation tips: Water early morning/evening. Check soil moisture at 6-inch depth. Which method interests you?"

def handle_weather_queries(message):
    """Handle weather and seasonal questions"""
    return "Seasonal farming: Kharif (June-Oct) - rice, cotton, sugarcane. Rabi (Nov-Apr) - wheat, mustard. Zaid (Apr-June) - fodder crops. What season are you planning for?"

def handle_soil_queries(message):
    """Handle soil-related questions"""
    return "Soil management: Test pH every 2 years (ideal 6.0-7.5). Add 2-3 tons organic matter/acre. Deep plow before monsoon. Need specific soil advice?"

def handle_pricing_queries(message):
    """Handle cost and pricing questions"""
    return "Equipment rates: Mini tractor ₹500-700/day, Harvester ₹1000-1500/day, Seed drill ₹400-600/day. Varies by location. What pricing do you need?"