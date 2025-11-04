import secrets
import string
import random


class PasswordGen:
    @staticmethod
    def generate(
        lenght=16, use_upper=True, use_lower=True, use_digits=True, use_special=True
    ):
        characters = ""
        if use_upper:  # "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            characters += string.ascii_uppercase
        if use_lower:  # "abcdefghijklmnopqrstuvwxyz"
            characters += string.ascii_lowercase
        if use_digits:  # "0123456789"
            characters += string.digits
        if use_special:  # Other special digits
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not characters:
            raise ValueError("No character types selected")

        # Generate at least one symbol of each type
        password = [
            secrets.choice(string.ascii_uppercase) if use_upper else "",
            secrets.choice(string.ascii_lowercase) if use_lower else "",
            secrets.choice(string.digits) if use_digits else "",
            secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?") if use_special else "",
        ]

        # Getting the remaining length
        remaining_lenght = lenght - len([c for c in password if c])
        password.extend(secrets.choice(characters) for _ in range(remaining_lenght))

        # Mix up the password to make it more random
        random.shuffle(password)
        return "".join(password)
