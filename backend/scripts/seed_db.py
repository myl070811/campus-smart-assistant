from __future__ import annotations

from app import create_app
from data.seed import ensure_demo_extensions, seed_if_empty


def main() -> None:
    app = create_app()
    with app.app_context():
        seed_if_empty()
        ensure_demo_extensions()
    print("Seed finished.")


if __name__ == "__main__":
    main()

