def get_rule_based_response(user_input):
    """Enhanced rule-based responses with better formatting"""
    text = text.lower()
    
    # Emergency Kit
    if any(w in text for w in ['kit', 'supplies', 'emergency', 'bag', 'prepare']):
        return """📦 **EMERGENCY KIT ESSENTIALS**

**🥤 Water & Food (3-Day Supply):**
✅ 1 gallon water per person per day (3 liters)
✅ Non-perishable food (canned goods, dry fruits, nuts)
✅ Manual can opener
✅ High-energy snacks

**🔦 Tools & Safety:**
✅ Flashlight + extra batteries
✅ Battery-powered or hand-crank radio
✅ Complete first aid kit
✅ Whistle (to signal for help)
✅ Dust masks, plastic sheeting, duct tape
✅ Multipurpose tool/knife

**📱 Communication:**
✅ Portable phone charger/power bank
✅ Written emergency contact list
✅ Local maps (paper copies)
✅ Waterproof document bag

**💊 Medical:**
✅ 7-day supply of prescription medications
✅ Glasses/contact lenses
✅ Sanitation items

**💵 Important Items:**
✅ Cash in small bills (₹500, ₹100, ₹50)
✅ Photocopies of important documents (Aadhar, insurance, bank)
✅ Extra house and car keys

**🧥 Clothing:**
✅ Complete change of clothes
✅ Sturdy shoes/boots
✅ Rain gear
✅ Warm blankets

**💡 TIP:** Store in waterproof container. Check every 6 months!

**📞 Emergency Contacts:**
🚨 **112** - All Emergencies | **108** - Ambulance | **101** - Fire | **1078** - Disaster Management"""

    # Evacuation
    elif any(w in text for w in ['evacuation', 'evacuate', 'leave', 'escape']):
        return """🚨 **EVACUATION PLANNING GUIDE**

**📍 BEFORE DISASTER:**
✅ **Know Your Routes:** Identify 2-3 evacuation paths from home/work
✅ **Practice Drills:** Run evacuation practice with family
✅ **Meeting Points:** Designate 2 locations:
   - One near home (neighbor's house, park)
   - One outside neighborhood (relative's house, community center)
✅ **Keep Emergency Kit Ready:** By main exit door

**🚗 DURING EVACUATION:**
1. **Act Immediately:** Don't wait if officials order evacuation
2. **Secure Home:** 
   - Lock doors and windows
   - Turn off utilities (if time permits)
   - Leave note with destination
3. **Take Only Essentials:**
   - Emergency kit
   - Important documents
   - Medications
   - Phone + charger
   - Cash
4. **Follow Official Routes:** Use designated evacuation roads only
5. **Help Neighbors:** Check on elderly, disabled neighbors
6. **Stay Informed:** Monitor radio/TV for updates

**📱 COMMUNICATION:**
✅ Text instead of call (saves network bandwidth)
✅ Use social media to update your status
✅ Check in with out-of-area contact person

**⚠️ NEVER:**
❌ Drive through flooded areas (Turn Around, Don't Drown!)
❌ Return home until authorities declare safe
❌ Use elevators during evacuation

**💡 REMEMBER:** Your life is more valuable than any possession!

**📞 Emergency:** **112** | **1078** (Disaster Management)"""

    # Flood
    elif 'flood' in text or 'flooding' in text:
        return """🌊 **FLOOD SAFETY GUIDE**

**⚠️ BEFORE FLOOD:**
✅ Move valuables to higher floors
✅ Turn off electricity, gas if instructed
✅ Fill bathtubs with clean water (for sanitation)
✅ Charge all devices
✅ Prepare to evacuate to higher ground

**🚨 DURING FLOOD:**
⚠️ **MOVE TO HIGHER GROUND IMMEDIATELY**
❌ **NEVER walk through moving water** (6 inches can knock you down)
❌ **NEVER drive through flooded roads** (2 feet sweeps away vehicles)
✅ Stay away from windows
✅ Avoid contact with flood water (contaminated)
✅ If trapped, go to highest level of building
✅ Signal for help (whistle, flashlight, bright cloth)

**✅ AFTER FLOOD:**
✅ Wait for "all clear" from authorities
✅ Avoid standing water (may hide hazards)
✅ Watch for snakes, insects
✅ Check building stability before entering
✅ Document damage with photos (insurance)
✅ Throw away contaminated food
✅ Boil water before drinking (until declared safe)

**⚠️ CRITICAL FACTS:**
🌊 **6 inches** of moving water = knock down an adult
🚗 **2 feet** of water = float most vehicles
💀 **Flood water contains:** Sewage, chemicals, debris, sharp objects

**📞 Emergency:** **108** (Ambulance) | **1078** (Disaster) | **112** (All Emergencies)"""

    # Earthquake
    elif any(w in text for w in ['earthquake', 'quake', 'tremor', 'seismic']):
        return """🌍 **EARTHQUAKE SAFETY**

**⚡ DURING EARTHQUAKE:**

**🏠 IF INDOORS:**
1. **DROP** to hands and knees
2. **COVER** head and neck under sturdy desk/table
3. **HOLD ON** until shaking stops
4. Stay away from:
   ❌ Windows, mirrors, glass
   ❌ Heavy furniture, appliances
   ❌ Exterior walls
5. **DON'T** run outside (falling debris risk)
6. **DON'T** use elevators
7. If in bed: Stay there, cover head with pillow

**🚗 IF IN VEHICLE:**
1. Pull over safely (away from buildings, trees, bridges, overpasses)
2. Stay inside with seatbelt fastened
3. Avoid stopping near power lines, signs
4. Resume driving carefully after shaking stops

**🌳 IF OUTDOORS:**
1. Move to open area away from buildings, trees, power lines
2. Drop to ground
3. Stay there until shaking stops

**✅ AFTER EARTHQUAKE:**
✅ Check yourself and others for injuries
✅ Inspect home for structural damage
✅ Turn off utilities if you smell gas or see damage
✅ **Watch for AFTERSHOCKS** (can occur hours/days later)
✅ Stay away from damaged buildings
✅ Use stairs, not elevators
✅ Stay off phone (except emergencies)
✅ Listen to radio for emergency broadcasts

**📦 EARTHQUAKE SURVIVAL KIT:**
✅ Sturdy shoes (protect from broken glass)
✅ Whistle (signal for help if trapped)
✅ Flashlight
✅ Fire extinguisher
✅ Wrench (to turn off utilities)
✅ 3-day water and food supply

**⚠️ REMEMBER:** DROP, COVER, HOLD ON!

**📞 Emergency:** **112** | **108** | **1078** (Disaster Management)"""

    # Heatwave
    elif any(w in text for w in ['heat', 'heatwave', 'hot', 'temperature']):
        return """🔥 **HEATWAVE SAFETY**

**❄️ STAY COOL:**
✅ Stay indoors during hottest hours (10 AM - 6 PM)
✅ Use AC, fans, or coolers
✅ Close curtains/blinds during day
✅ Take cool showers/baths
✅ Wear light, loose, cotton clothing
✅ Use damp cloth on neck/wrists
✅ Visit cooling centers if no AC (malls, libraries)

**💧 STAY HYDRATED:**
✅ Drink water regularly (don't wait to feel thirsty)
✅ Aim for 8-10 glasses per day
✅ Carry water bottle always
✅ Eat water-rich fruits (watermelon, cucumber)
❌ Avoid alcohol, caffeine, sugary drinks (dehydrating)

**🚨 HEAT ILLNESS WARNING SIGNS:**

**Heat Exhaustion (Moderate):**
- Heavy sweating
- Weakness, dizziness
- Nausea, vomiting
- Headache
- Cool, pale, clammy skin
- Fast, weak pulse

**ACTION:** Move to cool place, drink water, rest. Seek medical help if symptoms worsen.

**Heat Stroke (LIFE-THREATENING EMERGENCY!):**
- High body temperature (103°F / 39.4°C+)
- Hot, RED, DRY skin (NO sweating)
- Confusion, slurred speech
- Seizures
- Loss of consciousness

**ACTION:** ⚠️ **CALL 108 IMMEDIATELY!** Cool person with water, ice. This is a medical emergency!

**👶 PROTECT VULNERABLE:**
✅ Check on elderly, children, pregnant women, sick people
✅ NEVER leave anyone (humans or pets) in parked vehicles
✅ Pets need water and shade too

**💡 SAFETY TIPS:**
✅ Wear sunscreen (SPF 30+)
✅ Wear wide-brimmed hat
✅ Avoid heavy meals (generate body heat)
✅ Reduce physical activity
✅ Check weather forecasts

**📞 Medical Emergency:** **108** (Ambulance) | **112** (All Emergencies)"""

    # Wildfire
    elif any(w in text for w in ['wildfire', 'forest fire', 'bushfire', 'fire']):
        return """🔥 **WILDFIRE SAFETY**

**⚠️ BEFORE WILDFIRE SEASON:**
✅ Create 30-foot defensible space around home
✅ Clear dry leaves, dead vegetation, woodpiles
✅ Trim tree branches (6+ feet from ground)
✅ Install fire-resistant roofing
✅ Have garden hose connected and ready
✅ Know evacuation routes
✅ Pack emergency go-bag

**🚨 WILDFIRE APPROACHING:**
1. **Evacuate IMMEDIATELY if ordered** (don't wait!)
2. Close all windows and doors
3. Fill bathtubs, sinks with water
4. Move flammable furniture to center of rooms
5. Turn on ALL lights (helps firefighters see your house)
6. Shut off gas at meter (if time permits)
7. Take pets, emergency kit, important documents

**😷 SMOKE PROTECTION:**
✅ Stay indoors with windows closed
✅ Use air purifier if available
✅ Set AC to recirculate (don't bring outside air in)
✅ Wear N95 or P100 mask if going outside
✅ Keep car recirculation on if driving

**🚗 IF TRAPPED WHILE EVACUATING:**
1. Park in area clear of vegetation
2. Close windows, vents
3. Turn on headlights, hazard lights
4. Stay INSIDE vehicle
5. Cover yourself with blanket or jacket
6. Lie on floor
7. Call **101** (Fire) or **112**

**✅ AFTER WILDFIRE:**
✅ Wait for authorities to declare "all clear"
✅ Watch for hot spots, ash pits (can burn)
✅ Wear N95 mask (ash is toxic)
✅ Check for structural damage before entering home
✅ Document damage (photos for insurance)
✅ Watch for flare-ups (can reignite days later)

**⚠️ WILDFIRE SIGNS:**
🔥 Smoke in distance
🔥 Strong smell of smoke
🔥 Ash falling
🔥 Red/orange glow at night
🔥 Loud roaring sound

**📞 Fire Emergency:** **101** | **112** (All Emergencies)"""

    # Emergency Numbers
    elif any(w in text for w in ['emergency', 'number', 'contact', 'call', 'help', 'phone']):
        return """📞 **EMERGENCY CONTACT NUMBERS - INDIA**

**🚨 IMMEDIATE EMERGENCIES:**
**112** - National Emergency (Police, Fire, Ambulance - ALL SERVICES)
**100** - Police
**101** - Fire Brigade
**108** - Ambulance / Medical Emergency
**1078** - National Disaster Management Authority (NDMA)

**🏥 MEDICAL:**
**108** - Medical Emergency / Ambulance
**104** - National Blood Bank
**1800-599-0019** - Mental Health Helpline (KIRAN)

**👮 SAFETY & PROTECTION:**
**1091** - Women Helpline
**1098** - Child Helpline (CHILDLINE)
**1091** - Senior Citizen Helpline
**181** - Women in Distress

**🌊 DISASTER-SPECIFIC:**
**1078** - Earthquake, Flood, Cyclone, any natural disaster
**1093** - Coastal Security / Marine Emergency
**1077** - Railway Accident Emergency

**🚗 TRANSPORT:**
**139** - Railway Enquiry
**1073** - Road Accident Emergency Service

**💡 IMPORTANT TIPS:**
✅ **Save these numbers in your phone NOW**
✅ **Memorize 112** (universal emergency number)
✅ **TEXT if calls don't go through** (uses less bandwidth)
✅ **Give exact location when calling**
✅ **Stay calm and speak clearly**
✅ **Have important info ready:** Name, location, emergency type
✅ **Don't hang up** until told to by operator

**📱 EMERGENCY APPS TO DOWNLOAD:**
✅ **NDMA Disaster Alert** - Official disaster warnings
✅ **DisasterAlert (PDC)** - Global disaster tracking
✅ **Indian Red Cross** - Emergency response
✅ **Smart 24x7** - Women's safety
✅ **Meri Sakhi** - Women's helpline integration

**🌐 EMERGENCY WEBSITES:**
✅ ndma.gov.in - National Disaster Management
✅ ndrf.gov.in - National Disaster Response Force
✅ mha.gov.in - Ministry of Home Affairs

**Remember: In any emergency, call 112 first! It connects to all emergency services.**"""

    # Default comprehensive response
    else:
        return """🛡️ **DISASTER PREPAREDNESS ASSISTANT**

**I can help you with detailed information on:**

**🌊 NATURAL DISASTERS:**
• **Floods** - Safety before, during, after | Evacuation
• **Earthquakes** - Drop, Cover, Hold On | Aftershock safety
• **Wildfires** - Evacuation, smoke protection, home defense
• **Tornadoes/Cyclones** - Shelter, warning signs
• **Tsunamis** - Warning signs, evacuation routes
• **Landslides** - Risk areas, safety measures

**☀️ WEATHER EMERGENCIES:**
• **Heatwaves** - Heat illness prevention, cooling strategies
• **Droughts** - Water conservation, health precautions
• **Lightning** - Indoor/outdoor safety
• **Severe Storms** - Protection measures

**🎒 PREPAREDNESS:**
• **Emergency Kits** - Essential supplies checklist
• **Evacuation Planning** - Routes, meeting points, drills
• **Family Safety Plans** - Communication, responsibilities
• **First Aid** - Basic emergency medical care
• **Food & Water** - Storage, purification

**📱 EMERGENCY RESOURCES:**
• **Contact Numbers** - Police, Fire, Ambulance, Disaster Management
• **Safety Apps** - Disaster alerts, emergency communication
• **Community Resources** - Shelters, relief centers

**💡 EXAMPLE QUESTIONS:**
"What should be in my emergency kit?"
"How do I prepare for Mumbai monsoon floods?"
"Earthquake safety for apartment residents?"
"Emergency contacts for disasters?"
"How to evacuate safely with children?"

**📞 QUICK REFERENCE:**
🚨 **112** - All Emergencies
📱 **108** - Ambulance
🔥 **101** - Fire
🌊 **1078** - Disaster Management

**Ask me anything specific about disaster preparedness, and I'll provide detailed, actionable advice!** 🛡️"""
