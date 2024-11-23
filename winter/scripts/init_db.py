from winter.modules.database import initialize_database, create_user


def main():
    initialize_database()
    # Crear un usuario inicial
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    create_user(username, password)
    print("Database initialized and admin user created.")


if __name__ == "__main__":
    main()
