from sqlmodel import Session

from app.db import engine
from app.models import (
    Application,
    Feature,
    Listing,
    ListingFeature,
    Message,
    MessageFeature,
    Person,
    PersonFeature,
    User,
    UserFeature,
)

# Hardcoded test user ID — use this in the extension / Postman while testing
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"

# ── Feature vocabulary ────────────────────────────────────────────────────────
# Same names are used for both ListingFeature (what the landlord signals they
# want) and PersonFeature/UserFeature (what the applicant has).
# The LLM is guided to reuse these keys, so they will overlap with what gets
# extracted from real Kamernet listing descriptions.

FEATURES = {
    "quiet_person":           "Prefers quiet, respectful living — no parties or loud noise",
    "studious":               "Academically focused, often studies at home",
    "student_lifestyle":      "Student lifestyle — university-focused routine",
    "cooking_enthusiast":     "Cooks at home regularly, treats shared kitchen well",
    "likes_reading":          "Quiet hobbies — reads at home, calm evenings",
    "international_background": "International background, English-speaking",
    "family_oriented":        "Family-oriented or planning a family, stable long-term tenant",
    "high_income":            "Higher income — professional or executive salary",
    "professional_career":    "Working professional with stable corporate career",
    "social_lifestyle":       "Active social life, frequents gyms and coworking spaces",
    "likes_party":            "Enjoys hosting parties and gatherings at home",
    "plays_guitar":           "Plays guitar or other loud instruments at home",
}

# ── Seed listings ─────────────────────────────────────────────────────────────
# Group A: Delft-type — student-friendly, quiet, near campus
#   ListingFeature tags: quiet_person, student_lifestyle
#   → similar to the real Delft test listing (LLM should extract these from it)
#
# Group B: Rotterdam-type — premium, professional
#   ListingFeature tags: high_income, professional_career
#   → similar to the real Rotterdam test listing

LISTINGS = [
    # ── Group A: Delft-type ──────────────────────────────────────────────────
    {
        "external_id": "seed-delft-1",
        "url": "https://example.org/seed/delft-1",
        "title": "Quiet studio near TU Delft campus",
        "description": "Peaceful studio for a serious student or young professional. "
                       "Quiet building, studious neighbours. No parties.",
        "ideal_tenant": "Quiet, studious student or working student. No pets.",
        "price": 850.0,
        "location": "Delft",
        "listing_features": ["quiet_person", "student_lifestyle"],
        "applications": [
            {
                "name": "Emma S.",
                "status": "ACCEPTED",
                "person_features": ["quiet_person", "studious", "likes_reading", "international_background"],
            },
            {
                "name": "Sofia K.",
                "status": "ACCEPTED",
                "person_features": ["quiet_person", "studious", "family_oriented", "cooking_enthusiast"],
            },
            {
                "name": "Tom Party",
                "status": "REJECTED",
                "person_features": ["likes_party"],
            },
        ],
    },
    {
        "external_id": "seed-delft-2",
        "url": "https://example.org/seed/delft-2",
        "title": "Furnished room, close to Delft train station",
        "description": "Cosy room for students. Utilities included. "
                       "House values quiet evenings and a tidy shared kitchen.",
        "ideal_tenant": "Female student or working student, quiet, responsible.",
        "price": 900.0,
        "location": "Delft",
        "listing_features": ["quiet_person", "student_lifestyle"],
        "applications": [
            {
                "name": "Yuki T.",
                "status": "ACCEPTED",
                "person_features": ["quiet_person", "international_background", "likes_reading", "student_lifestyle"],
            },
            {
                "name": "Alice M.",
                "status": "ACCEPTED",
                "person_features": ["quiet_person", "studious", "international_background", "family_oriented"],
            },
            {
                "name": "Guitar Greg",
                "status": "REJECTED",
                "person_features": ["plays_guitar"],
            },
        ],
    },
    {
        "external_id": "seed-delft-3",
        "url": "https://example.org/seed/delft-3",
        "title": "Room in shared house, Delft city centre",
        "description": "Calm shared house, two current tenants. "
                       "Looking for someone quiet who respects shared spaces.",
        "ideal_tenant": "Studious or working student. No loud music.",
        "price": 800.0,
        "location": "Delft",
        "listing_features": ["quiet_person", "student_lifestyle"],
        "applications": [
            {
                "name": "Mieke V.",
                "status": "ACCEPTED",
                "person_features": ["quiet_person", "studious", "likes_reading"],
            },
            {
                "name": "Clara B.",
                "status": "ACCEPTED",
                "person_features": ["quiet_person", "family_oriented", "cooking_enthusiast", "student_lifestyle"],
            },
            {
                "name": "Sara Loud",
                "status": "REJECTED",
                "person_features": ["likes_party"],
            },
        ],
    },

    # ── Group B: Rotterdam-type ──────────────────────────────────────────────
    {
        "external_id": "seed-rotterdam-1",
        "url": "https://example.org/seed/rotterdam-1",
        "title": "Premium room in luxury apartment, Rotterdam",
        "description": "High-end furnished room in a modern apartment. "
                       "Gym, coworking space included. Looking for a professional housemate.",
        "ideal_tenant": "Working professional, high income, stable career.",
        "price": 1300.0,
        "location": "Rotterdam",
        "listing_features": ["high_income", "professional_career"],
        "applications": [
            {
                "name": "David R.",
                "status": "ACCEPTED",
                "person_features": ["high_income", "professional_career", "international_background", "social_lifestyle", "family_oriented"],
            },
            {
                "name": "Mark L.",
                "status": "ACCEPTED",
                "person_features": ["high_income", "professional_career", "international_background", "social_lifestyle"],
            },
            {
                "name": "Student Sven",
                "status": "REJECTED",
                "person_features": ["student_lifestyle", "quiet_person"],
            },
        ],
    },
    {
        "external_id": "seed-rotterdam-2",
        "url": "https://example.org/seed/rotterdam-2",
        "title": "Spacious room, Delfshaven area Rotterdam",
        "description": "Executive-grade apartment with all amenities. "
                       "Shared with a finance professional. Seeking similar profile.",
        "ideal_tenant": "Professional, employed, international background preferred.",
        "price": 1400.0,
        "location": "Rotterdam",
        "listing_features": ["high_income", "professional_career"],
        "applications": [
            {
                "name": "Sophie N.",
                "status": "ACCEPTED",
                "person_features": ["high_income", "professional_career", "social_lifestyle", "family_oriented"],
            },
            {
                "name": "James K.",
                "status": "ACCEPTED",
                "person_features": ["high_income", "professional_career", "international_background"],
            },
            {
                "name": "Backpacker Ben",
                "status": "REJECTED",
                "person_features": ["international_background", "likes_party"],
            },
        ],
    },
    {
        "external_id": "seed-rotterdam-3",
        "url": "https://example.org/seed/rotterdam-3",
        "title": "Modern apartment, Westzeedijk, Rotterdam",
        "description": "Premium 2BR apartment, floor heating, free gym. "
                       "Looking for professional, well-organised housemate.",
        "ideal_tenant": "Corporate professional, high earner, socially active.",
        "price": 1350.0,
        "location": "Rotterdam",
        "listing_features": ["high_income", "professional_career"],
        "applications": [
            {
                "name": "Chen W.",
                "status": "ACCEPTED",
                "person_features": ["high_income", "professional_career", "international_background"],
            },
            {
                "name": "Sara M.",
                "status": "ACCEPTED",
                "person_features": ["high_income", "professional_career", "family_oriented"],
            },
            {
                "name": "Rocky",
                "status": "REJECTED",
                "person_features": ["plays_guitar", "likes_party"],
            },
        ],
    },
]

# ── Test user features ────────────────────────────────────────────────────────
# Seeded directly — no LLM needed for the initial test.
# The bio will trigger LLM-based extraction on the first POST /api/users call,
# but these manual entries ensure tests work immediately from a fresh DB.
TEST_USER_FEATURES = {
    "quiet_person":       0.90,
    "studious":           0.85,
    "likes_reading":      0.80,
    "cooking_enthusiast": 0.75,
    "student_lifestyle":  0.70,
}


def seed() -> None:
    with Session(engine) as session:
        # ── Test user ────────────────────────────────────────────────────────
        test_user = User(
            user_id=TEST_USER_ID,
            name="Lisa de Vries",
            gender="F",
            occupation="MSc student / research assistant",
            income=1000,
            age=23,
            has_pets=False,
            bio=(
                "MSc student at TU Delft, 23 years old. I'm quiet and studious — "
                "most evenings I'm cooking or reading at home. Non-smoker, no pets. "
                "I work part-time as a research assistant (€1,000/month net). "
                "Dutch national, looking for a peaceful long-term room near campus."
            ),
        )
        session.add(test_user)
        session.commit()

        # ── Features ────────────────────────────────────────────────────────
        feature_objs: dict[str, Feature] = {}
        for name, desc in FEATURES.items():
            f = Feature(name=name, description=desc)
            session.add(f)
            session.flush()
            feature_objs[name] = f
        session.commit()

        # ── Test user features (manual seed, bypasses LLM) ──────────────────
        for name, score in TEST_USER_FEATURES.items():
            feat = feature_objs.get(name)
            if feat:
                session.add(UserFeature(
                    user_id=TEST_USER_ID,
                    feature_id=feat.feature_id,
                    score=score,
                ))
        session.commit()

        # ── Listings, applications, messages ────────────────────────────────
        for ld in LISTINGS:
            listing = Listing(
                external_id=ld["external_id"],
                url=ld["url"],
                title=ld["title"],
                description=ld["description"],
                ideal_tenant=ld.get("ideal_tenant"),
                price=ld.get("price"),
                location=ld.get("location"),
            )
            session.add(listing)
            session.flush()

            for fname in ld.get("listing_features", []):
                feat = feature_objs.get(fname)
                if feat:
                    session.add(ListingFeature(
                        listing_id=listing.listing_id,
                        feature_id=feat.feature_id,
                        score=1.0,
                    ))

            for appl in ld.get("applications", []):
                person = Person(name=appl["name"])
                session.add(person)
                session.flush()

                for pf_name in appl.get("person_features", []):
                    feat = feature_objs.get(pf_name)
                    if feat:
                        session.add(PersonFeature(
                            person_id=person.person_id,
                            feature_id=feat.feature_id,
                            score=1.0,
                        ))

                session.add(Application(
                    user_id=person.person_id,
                    listing_id=listing.listing_id,
                    status=appl["status"],
                ))

            session.commit()

    print("Seed complete.")
