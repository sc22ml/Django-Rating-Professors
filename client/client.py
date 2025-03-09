import requests

#Base URL
BASE_URL = "https://api.example.com/v1/"

AUTH_TOKEN = None

def register():
    print("\n---Register---")
    username = input("Enter your username: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    url = BASE_URL + "register"
    data = {
        "username": username,
        "email": email,
        "password": password,
    }

    response = requests.post(url, json=data)
    if response.status_code == 201:
        print("Registration successful!")
    else:
        print(f"Error:{response.json()}")


def login():
    global AUTH_TOKEN
    print("\n---Login---")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    url = BASE_URL + "login/"
    data = {
        "username": username,
        "password": password,
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        AUTH_TOKEN = response.json()["token"]
        print("Login Successful")
    else:
        print(f"Error:{response.json()}")


def list_module_instances():
    print("\n---Module Instances---")
    url = BASE_URL + "module_instances/"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        module_instances = response.json()
        for instance in module_instances:
            print(f"\nCode: {instance['code']}")
            print(f"Name: {instance['name']}")
            print(f"Year: {instance['year']}")
            print(f"Semester: {instance['semester']}")
            print("Taught by:")
            for professor in instance["taught_by"]:
                print(f"  - {professor['name']} (ID: {professor['id']})")
    else:
        print(f"Error: {response.json()}")


def rate_professor():
    print("\n---Rate Professor---")
    professor_id = input("Enter the professor's ID: ")
    module_instance_id = input("Enter Module Instance ID: ")
    rating = input("Enter your rating (1-5): ")

    url = BASE_URL + "rate/"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    data = {
        "professor_id": professor_id,
        "module_instance_id": module_instance_id,
        "rating": rating,
        }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("Rating submitted successfully")
    else:
        print(f"Error: {response.json()}")


def view_professor_ratings():
    print("\n--- Professor Ratings ---")
    url = BASE_URL + "professors/ratings/"
    headers = {"Authorization": f"Token {AUTH_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        professors = response.json()
        for professor in professors:
            print(f"\nName: {professor['name']}")
            print(f"Average Rating: {professor['average_rating']}")
    else:
        print(f"Error: {response.json()}")



def main():
    while True:
        print("\n--- Professor Rating System ---")
        print("1. Register")
        print("2. Login")
        print("3. List Module Instances")
        print("4. Rate Professor")
        print("5. View Professor Ratings")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            if AUTH_TOKEN:
                list_module_instances()
            else:
                 print("Please log in first.")
        elif choice == "4":
            if AUTH_TOKEN:
                rate_professor()
            else:
                print("Please log in first.")
        elif choice == "5":
            if AUTH_TOKEN:
                view_professor_ratings()
            else:
                print("Please log in first.")
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")       


if __name__ == "__main__":
    main()