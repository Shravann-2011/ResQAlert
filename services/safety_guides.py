"""
Safety guides for different disaster types.
Provides during and after guidance for users in emergency situations.
"""

def get_safety_guide(disaster_type: str) -> dict:
    """
    Get comprehensive safety guide for a specific disaster type.
    
    Args:
        disaster_type: 'flood', 'heatwave', or 'drought'
    
    Returns:
        dict with 'during' and 'after' lists of safety steps
    """
    
    guides = {
        'flood': {
            'during': [
                "🚨 Move to higher ground immediately.",
                "❌ Never walk or drive through moving water - it can sweep you away.",
                "🏠 If trapped indoors, go to upper floors, avoid basements.",
                "⚡ Switch off electricity if safe to do so.",
                "📞 Call emergency services (dial 112 in India) if trapped.",
                "🪵 Look for floating objects if in water; conserve energy while signaling for help.",
                "🌊 Avoid contaminated water - do not drink or touch.",
                "👨‍👩‍👧‍👦 Keep family together and let others know your location if possible.",
            ],
            'after': [
                "🔍 Check for structural damage before entering buildings.",
                "⚡ Have electrical systems inspected before using.",
                "💧 Boil or treat water before drinking; avoid contaminated food.",
                "📸 Document damage with photos for insurance/relief claims.",
                "🧹 Clean and disinfect safely; wear gloves and masks.",
                "🏥 Watch for waterborne diseases; seek medical help if ill.",
                "🛠️ Dispose of contaminated materials properly.",
                "📋 Register for disaster relief programs if available.",
            ]
        },
        'heatwave': {
            'during': [
                "💧 Drink water frequently, even if not thirsty - avoid alcohol and caffeine.",
                "🏠 Stay indoors in air-conditioned spaces if possible.",
                "👕 Wear light, loose-fitting clothing and a wide-brimmed hat if outside.",
                "❌ Avoid strenuous activity during peak heat (11 AM - 5 PM).",
                "🚗 Never leave children or pets in parked vehicles.",
                "👴 Check on elderly, young children, and those with medical conditions regularly.",
                "💊 Take medicines as prescribed; some drugs are affected by heat.",
                "🩹 Watch for heat exhaustion: dizziness, nausea, weakness - seek cool shelter immediately.",
            ],
            'after': [
                "💧 Continue drinking plenty of water for hydration recovery.",
                "🩺 Get medical check-up if you experienced heat-related symptoms.",
                "😴 Rest adequately - heat exhaustion can take time to recover from.",
                "🍎 Eat nutritious food to rebuild energy.",
                "🌤️ As temperatures cool, gradually resume outdoor activities.",
                "📝 Report any crop/livestock losses for relief assessment.",
                "💰 Check eligibility for compensation or relief programs.",
                "🔄 Prepare for next heat season: improve ventilation, stock water.",
            ]
        },
        'drought': {
            'during': [
                "💧 Use water only for essential needs: drinking, cooking, hygiene.",
                "🚿 Take short showers instead of baths; avoid washing vehicles.",
                "🌾 Irrigate only if you have water; prioritize crops/livestock.",
                "🐄 Provide alternative water sources for livestock if needed.",
                "🏥 Maintain hygiene despite water scarcity - use hand sanitizer when water unavailable.",
                "📻 Listen to drought advisories and water restrictions.",
                "🏡 Store water safely in covered containers.",
                "⛑️ Seek relief supplies (food, water) from authorities if available.",
            ],
            'after': [
                "💧 Boil or treat stored water before drinking.",
                "🌱 Plan for water harvesting and better storage for next drought.",
                "🌾 Assess crop and soil damage; get expert advice on recovery.",
                "🐄 Support livestock recovery with proper nutrition and veterinary care.",
                "📋 Register for drought relief, compensation, or crop insurance programs.",
                "🔄 Diversify crops if possible to reduce future drought impact.",
                "🏗️ Invest in water conservation infrastructure if feasible.",
                "📚 Learn about drought-resistant farming or water management techniques.",
            ]
        }
    }
    
    return guides.get(disaster_type.lower(), {
        'during': ["Contact local emergency services (112 in India)."],
        'after': ["Follow guidance from local authorities."]
    })


def get_highest_risk_type(predictions_dict: dict) -> str:
    """
    From a dict like {'flood': 0.8, 'drought': 0.3, 'heatwave': 0.5},
    return the disaster type with highest score.
    """
    if not predictions_dict:
        return 'flood'  # default
    
    highest = max(predictions_dict.items(), key=lambda x: x[1])
    return highest[0]
