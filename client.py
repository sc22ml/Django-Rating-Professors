import argparse
import requests
import getpass

BASE_URL = "http://127.0.0.1:8000/api/"

def register_user():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass.getpass("Enter password: ")

    url = f"{BASE_URL}register/"
    data = {
        "username": username,
        "email": email,
        "password": password
    }

    try:
        response = requests.post(url, json=data)  
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return

    if response.status_code == 201:
        print("Registration successful!")
    else:
        try:
            error_message = response.json()  
        except ValueError:
            error_message = response.text  
        print(f"Error: {error_message}")

#login
def login_user():
    username = input("Enter Username: ")
    password = getpass.getpass("Enter Password: ")
    url = f"{BASE_URL}login/"
    data = {
       "username": username,
       "password": password
    }
    response = requests.post(url, json = data)
    if response.status_code == 200:
       token = response.json().get("token")
       print("Login Successful")
       return token
    else:
        print(f"Error: {response.json()}")
        return None
    
#logout
def logout_user(token):
    url = f"{BASE_URL}logout/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Logout Successful")
    else:
        print(f"Error: {response.json()}")

#list
def list_module_instances(token):
    url = f"{BASE_URL}module-instances/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\nModule Instances:")
            print("-" * 50)
            for instance in data:
                print(f"Code: {instance['module_code']}")
                print(f"Name: {instance['module_title']}")
                print(f"Year: {instance['year']}")
                print(f"Semester: {instance['semester']}")
                print(f"Taught by: {', '.join([prof['name'] for prof in instance['professors']])}")
                print("-" * 50)
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

#view
def view_professor_ratings(token):
    url = f"{BASE_URL}professor-ratings/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\nProfessor Ratings:")
            print("-" * 50)
            for professor in data:
                print(f"Professor: {professor['name']} ({professor['id']})")
                print(f"Average Rating: {'*' * professor['average_rating']}")
                print("-" * 50)
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

#average
def view_average_rating(token):
    professor_id = input("Enter professor ID: ")
    module_code = input("Enter module code: ")
    
    url = f"{BASE_URL}professor-module-rating/{professor_id}/{module_code}/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\nAverage Rating:")
            print("-" * 50)
            print(f"Professor: {data['professor_name']} ({data['professor_id']})")
            print(f"Module: {data['module_name']} ({data['module_code']})")
            
            # Convert average_rating to an integer
            average_rating = int(round(data['average_rating']))
            print(f"Average Rating: {'*' * average_rating}")
            print("-" * 50)
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

#rate
def rate_professor(token):
    professor_id = input("Enter professor ID: ")
    module_code = input("Enter module code: ")
    year = input("Enter academic year (e.g., 2023): ")
    semester = input("Enter semester (1 or 2): ")
    rating = input("Enter rating (1-5): ")
    
    # Fetch the module instance ID
    url = f"{BASE_URL}module-instances/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching module instances: {response.status_code} - {response.text}")
        return
    
    module_instances = response.json()
    module_instance_id = None
    
    for instance in module_instances:
        if (
            instance["module_code"] == module_code
            and instance["year"] == int(year)
            and instance["semester"] == int(semester)
        ):
            module_instance_id = instance["id"]
            break
    
    if not module_instance_id:
        print("Error: Module instance not found.")
        return
    
    # Submit the rating
    url = f"{BASE_URL}rate-professor/"
    data = {
        "professor": professor_id,
        "module_instance": module_instance_id,
        "rating": rating
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print("Rating submitted successfully!")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def main():
    parser = argparse.ArgumentParser(description="Professor Rating Command-Line Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("register", help="Register a new user")

    subparsers.add_parser("login", help="Log in to the service")

    subparsers.add_parser("logout", help="Log out of the current session")

    subparsers.add_parser("list", help="List module instances and professors")

    subparsers.add_parser("view", help="View professor ratings")

    subparsers.add_parser("average", help="View average rating of a professor in a module")

    subparsers.add_parser("rate", help="Rate a professor for a module instance")

    args = parser.parse_args()

    if args.command == "register":
        register_user()
    elif args.command == "login":
        token = login_user()
        if token:
            # Store the token for future requests
            print(f"Token: {token}")
    elif args.command == "logout":
        token = input("Enter your token: ")
        logout_user(token)
    elif args.command == "list":
        token = input("Enter your token: ")
        list_module_instances(token)
    elif args.command == "view":
        token = input("Enter your token: ")
        view_professor_ratings(token)
    elif args.command == "average":
        token = input("Enter your token: ")
        view_average_rating(token)
    elif args.command == "rate":
        token = input("Enter your token: ")
        rate_professor(token)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()