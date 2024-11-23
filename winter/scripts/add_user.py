from winter.modules.database import create_user


def main():
    username = input("Enter new username: ")
    password = input("Enter new password: ")
    create_user(username, password)
    print("New user created.")


if __name__ == "__main__":
    main()
