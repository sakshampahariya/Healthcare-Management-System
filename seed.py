"""Seed diagnostic centres and tests for local development.

Usage (from project root, with venv active):

    python seed.py
"""

from copy import deepcopy
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import DiagnosticCentre, DiagnosticTest
from app.services.cache_service import invalidate_centre_caches

SEED_CENTRES = [
    {
        "name": "EVE Diagnostics — Koramangala",
        "location": "Koramangala, Bengaluru",
        "tests": [
            {
                "name": "Complete Blood Count (CBC)",
                "description": "Measures red cells, white cells, and platelets.",
                "price": Decimal("499.00"),
            },
            {
                "name": "Thyroid Profile (T3, T4, TSH)",
                "description": "Screens thyroid function.",
                "price": Decimal("899.00"),
            },
            {
                "name": "HbA1c",
                "description": "Average blood glucose over ~3 months.",
                "price": Decimal("650.00"),
            },
        ],
    },
    {
        "name": "EVE Diagnostics — Indiranagar",
        "location": "Indiranagar, Bengaluru",
        "tests": [
            {
                "name": "Lipid Profile",
                "description": "Cholesterol and triglyceride panel.",
                "price": Decimal("799.00"),
            },
            {
                "name": "Vitamin D (25-OH)",
                "description": "Serum vitamin D level.",
                "price": Decimal("1200.00"),
            },
        ],
    },
    {
        "name": "EVE Diagnostics — Whitefield",
        "location": "Whitefield, Bengaluru",
        "tests": [
            {
                "name": "Liver Function Test (LFT)",
                "description": "Enzymes and proteins that reflect liver health.",
                "price": Decimal("950.00"),
            },
            {
                "name": "Kidney Function Test (KFT)",
                "description": "Creatinine, urea, and electrolytes.",
                "price": Decimal("850.00"),
            },
        ],
    },
]


def seed() -> None:
    app = create_app()
    with app.app_context():
        if DiagnosticCentre.query.first():
            print("Seed data already present. Skipping.")
            return

        for centre_data in deepcopy(SEED_CENTRES):
            tests = centre_data.pop("tests")
            centre = DiagnosticCentre(**centre_data)
            db.session.add(centre)
            db.session.flush()
            for test_data in tests:
                db.session.add(DiagnosticTest(centre_id=centre.id, **test_data))

        db.session.commit()
        invalidate_centre_caches()
        print("Seeded 3 diagnostic centres and their tests.")


if __name__ == "__main__":
    seed()
