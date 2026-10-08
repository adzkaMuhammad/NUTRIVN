"""NutriVane beta dataset: benchmark menus, spice averages (computed from ~5-6 recipe sources
per menu in the Bumbu Nutrivane dataset), moods, and curated picks."""

IMG_RENDANG = "https://images.unsplash.com/photo-1766567461692-32c352d198d4?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200"
IMG_SOP = "https://images.unsplash.com/photo-1612108438004-257c47560118?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200"
IMG_NASGOR = "https://images.pexels.com/photos/37171028/pexels-photo-37171028.jpeg?auto=compress&cs=tinysrgb&w=1200"
IMG_HEALTHY = "https://images.unsplash.com/photo-1540420773420-3366772f4999?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200"

# category keys: "menu-utama", "perut-nyaman", "menu-cepat"
RECIPES = [
    {
        "slug": "rendang",
        "name": "Rendang sapi",
        "category": "menu-utama",
        "category_label": "Menu utama",
        "porsi": 4,
        "image": IMG_RENDANG,
        "tagline": "Rasa kaya rempah dengan profil gurih yang bisa kamu pahami sebelum memasak.",
        "flavor_note": "Kaya rempah, gurih pekat, sedikit pedas.",
        "spices": [
            {"name": "Cabai", "avg": 86, "unit": "g"},
            {"name": "Bawang Merah", "avg": 34, "unit": "g"},
            {"name": "Bawang Putih", "avg": 24, "unit": "g"},
            {"name": "Serai", "avg": 22, "unit": "g"},
            {"name": "Lengkuas", "avg": 18, "unit": "g"},
            {"name": "Jahe", "avg": 12, "unit": "g"},
            {"name": "Kunyit", "avg": 8, "unit": "g"},
            {"name": "Garam", "avg": 5, "unit": "g"},
        ],
        "sources": [
            {"name": "DetikFood", "porsi": 4},
            {"name": "Fimela", "porsi": 10},
            {"name": "Cookpad", "porsi": 10},
            {"name": "Orami", "porsi": 3},
            {"name": "ResepKoki", "porsi": 20},
        ],
    },
    {
        "slug": "sayur-sop-ayam",
        "name": "Sayur sop ayam",
        "category": "perut-nyaman",
        "category_label": "Perut nyaman",
        "porsi": 4,
        "image": IMG_SOP,
        "tagline": "Kuah hangat dengan rempah ringan untuk pilihan makan yang terasa lebih nyaman.",
        "flavor_note": "Bening, hangat, gurih ringan.",
        "spices": [
            {"name": "Bawang Merah", "avg": 18, "unit": "g"},
            {"name": "Bawang Putih", "avg": 14, "unit": "g"},
            {"name": "Daun Bawang", "avg": 8, "unit": "g"},
            {"name": "Garam", "avg": 7, "unit": "g"},
            {"name": "Jahe", "avg": 5, "unit": "g"},
            {"name": "Kaldu Jamur", "avg": 4, "unit": "g"},
            {"name": "Merica", "avg": 3, "unit": "g"},
            {"name": "Pala", "avg": 1, "unit": "g"},
        ],
        "sources": [
            {"name": "Cookpad", "porsi": 4},
            {"name": "ResepKoki", "porsi": 7},
            {"name": "DetikFood", "porsi": 4},
            {"name": "Dapur Umami", "porsi": 4},
            {"name": "Fimela", "porsi": 5},
        ],
    },
    {
        "slug": "nasi-goreng",
        "name": "Nasi goreng rumahan",
        "category": "menu-cepat",
        "category_label": "Menu cepat",
        "porsi": 3,
        "image": IMG_NASGOR,
        "tagline": "Benchmark bumbu nasi goreng dari berbagai resep rumahan yang mudah dibandingkan.",
        "flavor_note": "Gurih manis, aroma bawang, sedikit pedas.",
        "spices": [
            {"name": "Kecap Manis", "avg": 20, "unit": "g"},
            {"name": "Cabai", "avg": 15, "unit": "g"},
            {"name": "Bawang Merah", "avg": 12, "unit": "g"},
            {"name": "Bawang Putih", "avg": 9, "unit": "g"},
            {"name": "Kemiri", "avg": 6, "unit": "g"},
            {"name": "Garam", "avg": 4, "unit": "g"},
            {"name": "Terasi", "avg": 3, "unit": "g"},
            {"name": "Merica", "avg": 2, "unit": "g"},
        ],
        "sources": [
            {"name": "TasteAtlas", "porsi": 2},
            {"name": "EatingWell", "porsi": 4},
            {"name": "IDNTimes", "porsi": 3},
            {"name": "Rukita", "porsi": 1},
            {"name": "ResepUmami", "porsi": 3},
            {"name": "Cookpad", "porsi": 3},
        ],
    },
]

MOODS = [
    {
        "key": "berenergi",
        "label": "Berenergi",
        "emoji": "⚡",
        "subtitle": "Menu yang bikin siap jalan",
        "question": "Hari ini kamu ingin merasa berenergi?",
        "helper": "Menu yang bikin siap jalan — pilih yang paling mendekati, tidak harus sempurna.",
        "recipe_slugs": ["nasi-goreng", "rendang"],
    },
    {
        "key": "perut-nyaman",
        "label": "Perut nyaman",
        "emoji": "🌿",
        "subtitle": "Hangat dan lebih ringan",
        "question": "Hari ini kamu ingin perut terasa nyaman?",
        "helper": "Pilihan hangat dan ringan untuk menemani harimu.",
        "recipe_slugs": ["sayur-sop-ayam"],
    },
    {
        "key": "rendah-garam",
        "label": "Rendah garam",
        "emoji": "🫧",
        "subtitle": "Lebih mindful soal rasa",
        "question": "Mau yang lebih mindful soal garam?",
        "helper": "Kami tampilkan menu dengan rata-rata garam yang lebih rendah.",
        "recipe_slugs": ["sayur-sop-ayam", "nasi-goreng"],
    },
    {
        "key": "ingin-manis",
        "label": "Ingin manis",
        "emoji": "🍯",
        "subtitle": "Pilih manis secukupnya",
        "question": "Lagi ingin rasa yang sedikit manis?",
        "helper": "Pilih manis secukupnya, tetap seimbang.",
        "recipe_slugs": ["nasi-goreng", "rendang"],
    },
]

CATEGORIES = [
    {"key": "semua", "label": "Semua"},
    {"key": "menu-utama", "label": "Menu utama"},
    {"key": "perut-nyaman", "label": "Perut nyaman"},
    {"key": "menu-cepat", "label": "Menu cepat"},
]
