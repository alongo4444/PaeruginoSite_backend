# #!/usr/bin/env python3
#
# from app.db.session import get_db
# from app.db.crud import create_user
# from app.db.schemas import UserCreate
# from app.db.session import SessionLocal
#
#
# def init() -> None:
#     db = SessionLocal()
#
#
#     create_user(
#         db,
#         UserCreate(
#             email="inonbenz@post.bgu.ac.il",
#             password="chi1ki2ta3",
#             is_active=True,
#             is_superuser=True,
#         ),
#     )
#
#
# if __name__ == "__main__":
#     print("Creating superuser inonbenz@post.bgu.ac.il")
#     init()
#     print("Superuser created")
