import subprocess
import argparse
import pyperclip
from ollama import Client


# Initialize Ollama client
ollama_client = Client(host="http://localhost:11434")


def get_git_changes():
    """Get the git changes of the current repository."""
    try:
        # First, try to get staged changes
        staged_changes = subprocess.check_output(["git", "diff", "--cached"], universal_newlines=True)
        if staged_changes:
            return staged_changes

        # If no staged changes, get all changes
        all_changes = subprocess.check_output(["git", "diff"], universal_newlines=True)
        if all_changes:
            return all_changes

        print("No changes detected in the git repository.")
        return None
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or unable to get changes.")
        return None


def generate_commit_message_ollama(changes, style_guide):
    """Generate a commit message using Ollama."""
    prompt = f"""
    Based on the following git changes and style guide, generate a commit message:

    Git Changes:
    {changes}

    Style Guide:
    {style_guide}

    Generate a commit message that follows the style guide and accurately describes the changes.
    """
    response = ollama_client.generate(prompt=prompt)
    return response["response"].strip()


def generate_short_description_ollama(commit_message):
    """Generate a short description of the commit message using Ollama."""
    prompt = f"""
    Based on the following commit message, generate a short, one-line description:

    {commit_message}

    Generate a concise summary that captures the essence of the changes.
    """
    response = ollama_client.generate(prompt=prompt)
    return response["response"].strip()


def read_style_guide(file_path):
    """Read the style guide from a file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Style guide file not found: {file_path}")
        return None


def update_commit_message(current_message):
    """Update the commit message based on user input."""
    print("\nCurrent commit message:")
    print(current_message)
    user_input = input("\nEnter your modifications (or press Enter to keep as is): ")
    return user_input if user_input else current_message


def copy_to_clipboard(text):
    """Copy the given text to clipboard."""
    pyperclip.copy(text)
    print("Commit message copied to clipboard.")


def main():
    parser = argparse.ArgumentParser(description="Generate Git commit messages using LLM.")
    parser.add_argument("--style", default="style_guide.txt", help="Path to the style guide file")
    parser.add_argument(
        "--llm", choices=["ollama", "openai", "claude"], default="ollama", help="Choose the LLM provider"
    )
    args = parser.parse_args()

    changes = get_git_changes()
    if not changes:
        return

    style_guide = read_style_guide(args.style)
    if not style_guide:
        return

    generate_commit_message = generate_commit_message_ollama
    generate_short_description = generate_short_description_ollama

    commit_message = generate_commit_message(changes, style_guide)
    print("\nGenerated commit message:")
    print(commit_message)

    choice = input("\nDo you want to (u)pdate, generate (s)hort description, or (f)inalize? [u/s/f]: ").lower()

    if choice == "u":
        commit_message = update_commit_message(commit_message)
    elif choice == "s":
        short_description = generate_short_description(commit_message)
        print("\nShort description:")
        print(short_description)
        use_short = input("Use this as the commit message? [y/n]: ").lower()
        if use_short == "y":
            commit_message = short_description

    copy_to_clipboard(commit_message)
    print("\nFinal commit message:")
    print(commit_message)
    print('\nUse this commit message with: git commit -m "<paste clipboard content here>"')


if __name__ == "__main__":
    main()
