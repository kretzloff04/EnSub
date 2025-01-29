from auth import google_login, google_logout, create_gmail_service
from gmail import get_num_from_sender, mass_delete_from_sender
from unsub import unsub_from_sender, all_subbed_senders
import time
import re

service = create_gmail_service()

def main_menu():
    while True:
        print("-----Main Menu-----")
        print("1. View most common senders")
        print("2. View subscribed senders")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            view_most_common_senders()
        elif choice == "2":
            view_subscribed_senders()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again")
        

def view_most_common_senders():
    print("Fetching most common senders... This may take a moment depending on your inbox size...")
    start_time = time.time()
    sender_data = get_num_from_sender(service)
    end_time = time.time()

    if not sender_data:
        print("No senders found.")
        return
    else:
        print("-----Most Common Senders-----")
        for i, (sender, count) in enumerate(sender_data.items(), start=1):
            print(f'{i}. {sender}: {count} emails')
    print(" ")
    print(f'Loaded in {end_time - start_time:.2f} seconds')
    while True:
    
        print(" ")
        print("Options")
        print("1. Delete ALL emails from a sender")
        print("2. Delete all BUT STARRED from a sender")
        print("3. Back to Main Menu")
        print(" ")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            sender_to_delete = input("Enter the sender's email address to delete emails from: ").strip()
            confirm = input(f'Are you sure you want to delete all emails from {sender_to_delete}? (yes/no): ').strip().lower()
            print(" ")
            if confirm == "yes":
                mass_delete_from_sender(service, sender_to_delete, True)
            else:
                print("Deletion cancelled.")
        elif choice == "2":
            sender_to_delete = input("Enter the sender's email address to delete emails from: ").strip()
            confirm = input(f'Are you sure you want to delete all emails from {sender_to_delete}? (yes/no): ').strip().lower()
            print(" ")
            if confirm == "yes":
                mass_delete_from_sender(service, sender_to_delete, False)
            else:
                print("Deletion cancelled.")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
            


def view_subscribed_senders():
    print("Fetching subscribed senders... This may take a moment depending on the size of your inbox...")
    start_time = time.time()
    sender_data = all_subbed_senders(service)
    end_time = time.time()  
    while True:

        
        if not sender_data:
            print("No subscribed senders found...")
            return
        else:
            print("-----Subscribed Senders-----")
            for i in range(len(sender_data)):
                print(f'{i}. {sender_data[i]}')
        
        print(f'Loaded in {end_time - start_time:.2f} seconds')
        print("Options:")
        print("1. Unsubscribe from a sender")
        print("2. Unsubscribe AND delete all BUT STARRED emails from sender")
        print("3. Back")
        print(" ")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            sender_to_unsub = input("Enter the email address of the sender you want to unsubscribe from: ").strip().lower()
            confirm = input(f'Are you sure you want to delete all emails from {sender_to_unsub}? (yes/no): ').strip().lower()
            print(" ")
            if confirm == "yes":
                unsub_from_sender(service, sender_to_unsub)
            else:
                print("Unsub cancelled.") 
        
        elif choice == "2":
            sender_to_unsub = input("Enter the email address of the sender you want to unsubscribe from: ").strip().lower()
            confirm = input(f'Are you sure you want to delete all emails from {sender_to_unsub}? (yes/no): ').strip().lower()
            print(" ")
            if confirm == "yes":
                unsub_from_sender(service, sender_to_unsub)
                mass_delete_from_sender(service, sender_to_unsub, False)
            else:
                print("Unsub cancelled")
        elif choice == "3":
            break
        else:
            print("Invalid entry, try again.")


if __name__ == "__main__":
    print("Welcome to the Gmail Email Tool!")
    main_menu()