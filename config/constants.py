# Market tags configuration
MARKET_TAGS = {
    "high_growth_potential": {
        "name": "High Growth Potential",
        "description": "Market shows significant room for network expansion",
        "condition": lambda row: row['growth_potential'] > 0.5,
        "icon": "📈",
        "color": "text-green-600"
    },
    "efficiency_star": {
        "name": "Efficiency Star",
        "description": "Exceptional lead generation performance",
        "condition": lambda row: row['performance_efficiency'] > 0.8,
        "icon": "⭐",
        "color": "text-blue-600"
    },
    "low_penetration": {
        "name": "Low Penetration",
        "description": "Limited network presence in the market",
        "condition": lambda row: row['network_penetration'] < row['avg_network_penetration'],
        "icon": "🌱",
        "color": "text-indigo-600"
    },
    "very_similar": {
        "name": "Very Similar",
        "description": "Highly similar to the target market",
        "condition": lambda row: row['norm_similarity'] > 0.5,
        "icon": "🎯",
        "color": "text-purple-600"
    }
}

# Known iBuyers list
IBUYERS = [
    'opendoor.com',
    'offerpad.com',
    'redfin.com',
    'zillow.com',
    'homelight.com',
    'knock.com',
    'orchard.com',
    'webuyuglyhouses.com',
    'houzeo.com'
]