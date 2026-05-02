from sqlmodel import Session, select

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
)


def _get_or_create_feature(session: Session, name: str, description: str) -> Feature:
    stmt = select(Feature).where(Feature.name == name)
    existing = session.exec(stmt).first()
    if existing:
        return existing
    f = Feature(name=name, description=description)
    session.add(f)
    session.commit()
    session.refresh(f)
    return f


def seed() -> None:

    # Listing features (realistic attributes renters put in listings)
    listing_features = {
        "furnished": "Comes with furniture included",
        "balcony": "Has a balcony",
        "near_station": "Close to public transport station",
        "parking": "Private or street parking available",
        "garden": "Garden or outdoor space",
        "renovated": "Recently renovated property",
        "utilities_included": "Utilities included in rent",
        "no_pets": "No pets allowed",
        "pets_ok": "Pets allowed",
        "student_ok": "Suitable for students",
        "affordable": "Lower rental prices, budget-friendly",
    }

    # Applicant/motivation-letter style features
    applicant_features = {
        "likes_party": "Enjoys social life / going out",
        "likes_reading": "Enjoys reading and quiet cultural activities",
        "plays_guitar": "Plays guitar or another musical instrument",
        "likes_nature": "Enjoys nature, hiking, parks and green spaces",
        "student_lifestyle": "Student lifestyle (studies, student clubs)",
        "family_oriented": "Family-oriented, stable household",
        "high_income": "Higher income / professional career",
        "international_background": "Lived or worked abroad; international outlook",
        "studious": "Very focused on studies and quiet routines",
        "cooking_enthusiast": "Enjoys cooking and home meals",
        "quiet_person": "Prefers quiet, respectful living environment",
    }

    listings_data = [
        # Achterwijken van Amsterdam (two examples) — studenty listings
        {
            "external_id": "achter-1",
            "url": "https://example.org/listings/achter-1",
            "title": "Cozy studio in Achterwijken",
            "description": "Small studio, popular with students and social life.",
            "price": 85000,  # €850.00
            "location": "Achterwijken, Amsterdam",
            "listing_type": "studio",
            "features": ["student_ok", "furnished", "near_station"],
            "applications": [
                {
                    "name": "Anna Student",
                    "status": "ACCEPTED",
                    "person_features": ["student_lifestyle", "likes_reading"],
                    "messages": [
                        {
                            "text": "Hi, I'm Anna, an MSc student at UvA. I'm tidy and friendly, would love the studio.",
                            "features": ["student_lifestyle", "likes_reading"],
                        },
                        {
                            "text": "Thanks Anna, we can proceed with a viewing.",
                            "features": [],
                        },
                    ],
                },
                {
                    "name": "Tom Party",
                    "status": "REJECTED",
                    "person_features": ["likes_party", "plays_guitar"],
                    "messages": [
                        {
                            "text": "Hey, I'm often hosting friends and jamming sessions.",
                            "features": ["likes_party", "plays_guitar"],
                        },
                    ],
                },
                {
                    "name": "Sara Loud",
                    "status": "REJECTED",
                    "person_features": ["likes_party"],
                    "messages": [
                        {
                            "text": "I'm very social and love nights out.",
                            "features": ["likes_party"],
                        },
                    ],
                },
            ],
        },
        {
            "external_id": "achter-2",
            "url": "https://example.org/listings/achter-2",
            "title": "One-bedroom apartment near shops",
            "description": "Compact 1BR; quiet evenings preferred but close to campus.",
            "price": 115000,  # €1,150.00
            "location": "Achterwijken, Amsterdam",
            "listing_type": "apartment",
            "features": ["furnished", "near_station", "no_pets"],
            "applications": [
                {
                    "name": "Lucas Quiet",
                    "status": "ACCEPTED",
                    "person_features": ["studious", "cooking_enthusiast"],
                    "messages": [
                        {
                            "text": "Hi, I'm Lucas, I study and cook a lot — happy to keep the place tidy.",
                            "features": ["studious", "cooking_enthusiast"],
                        },
                    ],
                },
                {
                    "name": "Party Pete",
                    "status": "REJECTED",
                    "person_features": ["likes_party"],
                    "messages": [
                        {
                            "text": "I love inviting people over and playing music.",
                            "features": ["likes_party"],
                        },
                    ],
                },
                {
                    "name": "Guitar Greg",
                    "status": "REJECTED",
                    "person_features": ["plays_guitar"],
                    "messages": [
                        {
                            "text": "I'm a guitarist and practice daily.",
                            "features": ["plays_guitar"],
                        },
                    ],
                },
            ],
        },
        # Wassenaar (two examples) - affluent suburb (family/professional traits)
        {
            "external_id": "wassenaar-1",
            "url": "https://example.org/listings/wassenaar-1",
            "title": "Family home with large garden",
            "description": "Spacious house, ideal for families and professionals.",
            "price": 350000,  # €3,500.00
            "location": "Wassenaar",
            "listing_type": "house",
            "features": ["garden", "parking", "renovated"],
            "applications": [
                {
                    "name": "Familie de Vries",
                    "status": "ACCEPTED",
                    "person_features": ["family_oriented", "high_income"],
                    "messages": [
                        {
                            "text": "We are a quiet family looking for long-term rental; stable income.",
                            "features": ["family_oriented", "high_income"],
                        },
                    ],
                },
                {
                    "name": "Student Sven",
                    "status": "REJECTED",
                    "person_features": ["student_lifestyle"],
                    "messages": [
                        {
                            "text": "I'm a student and would love the garden for parties.",
                            "features": ["student_lifestyle", "likes_party"],
                        },
                    ],
                },
                {
                    "name": "Rocky",
                    "status": "REJECTED",
                    "person_features": ["plays_guitar"],
                    "messages": [
                        {
                            "text": "I play in a band and rehearse at home.",
                            "features": ["plays_guitar"],
                        },
                    ],
                },
            ],
        },
        {
            "external_id": "wassenaar-2",
            "url": "https://example.org/listings/wassenaar-2",
            "title": "Modern villa near the dunes",
            "description": "High-end villa, quiet and close to nature.",
            "price": 480000,  # €4,800.00
            "location": "Wassenaar",
            "listing_type": "villa",
            "features": ["garden", "renovated", "pets_ok"],
            "applications": [
                {
                    "name": "Prof. Jansen",
                    "status": "ACCEPTED",
                    "person_features": [
                        "high_income",
                        "international_background",
                        "quiet_person",
                    ],
                    "messages": [
                        {
                            "text": "Academic working internationally; seeking quiet residence near the dunes.",
                            "features": [
                                "high_income",
                                "international_background",
                                "quiet_person",
                            ],
                        },
                    ],
                },
                {
                    "name": "Backpacker Ben",
                    "status": "REJECTED",
                    "person_features": ["international_background", "likes_party"],
                    "messages": [
                        {
                            "text": "I travel a lot and host friends from abroad.",
                            "features": ["international_background", "likes_party"],
                        },
                    ],
                },
                {
                    "name": "Strummer Stella",
                    "status": "REJECTED",
                    "person_features": ["plays_guitar"],
                    "messages": [
                        {
                            "text": "I play guitar professionally and often practice.",
                            "features": ["plays_guitar"],
                        },
                    ],
                },
            ],
        },
        # Leeuwarden (two examples) - smaller city (calm, student-friendly)
        {
            "external_id": "leeuwarden-1",
            "url": "https://example.org/listings/leeuwarden-1",
            "title": "Affordable apartment near the canals",
            "description": "Budget-friendly 2BR in a calm historic centre.",
            "price": 65000,  # €650.00
            "location": "Leeuwarden",
            "listing_type": "apartment",
            "features": ["affordable", "near_station", "no_pets"],
            "applications": [
                {
                    "name": "Mieke",
                    "status": "ACCEPTED",
                    "person_features": ["studious", "likes_reading"],
                    "messages": [
                        {
                            "text": "I'm a calm student who loves reading and early nights.",
                            "features": ["studious", "likes_reading"],
                        },
                    ],
                },
                {
                    "name": "Club Kevin",
                    "status": "REJECTED",
                    "person_features": ["likes_party"],
                    "messages": [
                        {
                            "text": "I enjoy nightlife and parties every weekend.",
                            "features": ["likes_party"],
                        },
                    ],
                },
                {
                    "name": "Gita",
                    "status": "REJECTED",
                    "person_features": ["plays_guitar"],
                    "messages": [
                        {
                            "text": "I do regular jam sessions at home.",
                            "features": ["plays_guitar"],
                        },
                    ],
                },
            ],
        },
        {
            "external_id": "leeuwarden-2",
            "url": "https://example.org/listings/leeuwarden-2",
            "title": "Quiet house close to local amenities",
            "description": "Small family or professional home, peaceful neighbourhood.",
            "price": 90000,  # €900.00
            "location": "Leeuwarden",
            "listing_type": "house",
            "features": ["garden", "parking", "renovated"],
            "applications": [
                {
                    "name": "Henk",
                    "status": "ACCEPTED",
                    "person_features": ["family_oriented", "cooking_enthusiast"],
                    "messages": [
                        {
                            "text": "Small family, we love cooking and quiet evenings.",
                            "features": ["family_oriented", "cooking_enthusiast"],
                        },
                    ],
                },
                {
                    "name": "Noisy Nick",
                    "status": "REJECTED",
                    "person_features": ["likes_party"],
                    "messages": [
                        {
                            "text": "I host friends frequently and have loud gatherings.",
                            "features": ["likes_party"],
                        },
                    ],
                },
                {
                    "name": "Strum Sam",
                    "status": "REJECTED",
                    "person_features": ["plays_guitar"],
                    "messages": [
                        {
                            "text": "I practice guitar daily and record at home.",
                            "features": ["plays_guitar"],
                        },
                    ],
                },
            ],
        },
    ]

    with Session(engine) as session:
        # create features first (listing + applicant traits)
        feature_objs: dict[str, Feature] = {}
        for name, desc in {**listing_features, **applicant_features}.items():
            f = _get_or_create_feature(session, name, desc)
            feature_objs[name] = f

        # create listings and link listing features
        for ld in listings_data:
            l = Listing(
                external_id=ld["external_id"],
                url=ld["url"],
                title=ld["title"],
                description=ld["description"],
                price=ld["price"],
                location=ld["location"],
                listing_type=ld["listing_type"],
            )
            session.add(l)
            session.commit()
            session.refresh(l)

            for fname in ld["features"]:
                feat = feature_objs.get(fname)
                if feat:
                    session.add(
                        ListingFeature(
                            listing_id=l.listing_id, feature_id=feat.feature_id
                        )
                    )

            session.commit()

            appls = ld.get("applications", [])
            for a in appls:
                p = Person(name=a["name"], text=(a.get("text") or ""))
                session.add(p)
                session.commit()
                session.refresh(p)

                # link person features
                for pf in a.get("person_features", []):
                    fobj = feature_objs.get(pf)
                    if fobj:
                        session.add(
                            PersonFeature(
                                person_id=p.person_id, feature_id=fobj.feature_id
                            )
                        )

                # create messages (chat history)
                for msg in a.get("messages", []):
                    m = Message(
                        person_id=p.person_id,
                        listing_id=l.listing_id,
                        message=msg["text"],
                    )
                    session.add(m)
                    session.commit()
                    session.refresh(m)
                    for mf in msg.get("features", []):
                        mfobj = feature_objs.get(mf)
                        if mfobj:
                            session.add(
                                MessageFeature(
                                    message_id=m.message_id, feature_id=mfobj.feature_id
                                )
                            )

                # create application
                application = Application(
                    user_id=p.person_id,
                    listing_id=l.listing_id,
                    status=a["status"],
                    message=(a.get("messages") or [])[0].get("text"),
                )
                session.add(application)
            session.commit()

    print("Seed complete: inserted features and listings.")

