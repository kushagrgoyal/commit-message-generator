import os
import subprocess
import pyperclip

from ollama import Client


def get_git_changes(repo_path):
    """Get the git changes of the specified repository."""
    try:
        # Change to the specified directory
        original_dir = os.getcwd()
        os.chdir(repo_path)

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
        print(f"Error: Not a git repository or unable to get changes in {repo_path}")
        return None
    finally:
        # Change back to the original directory
        os.chdir(original_dir)


def generate_commit_message_ollama(
    *, ollama_client: Client, model: str, changes, style_guide, system_prompt: str
) -> str:
    """Generate a commit message using Ollama."""
    prompt = f"""
    Based on the following git changes and style guide, generate a 1-line commit message that accurately describes the changes:

    Git Changes:
    {changes}

    Style Guide:
    {style_guide}
    """
    response = ollama_client.generate(prompt=prompt, model=model, system=system_prompt)
    return response["response"].strip()


def generate_short_description_ollama(
    *, ollama_client: Client, model: str, commit_message: str, system_prompt: str
) -> str:
    """Generate a short description of the commit message using Ollama."""
    prompt = f"""
    Based on the following commit message, generate a short, concise description:
    {commit_message}
    """
    response = ollama_client.generate(prompt=prompt, model=model, system=system_prompt)
    return response["response"].strip()


def update_commit_message_ollama(*, ollama_client: Client, model: str, current_message: str, system_prompt: str) -> str:
    """Update the commit message based on user input."""
    user_input = input("\nEnter your modifications (or press Enter to keep as is): ")

    if user_input is not None:
        prompt = f"""
        Based on the following commit message and user's modification instructions, update the commit message:
        Current commit message:
        {current_message}
        
        User's modifications:
        {user_input}

        Generate a new commit message that:
        - follows updated user's modification instructions
        - accurately describes the changes
        """
        response = ollama_client.generate(prompt=prompt, model=model, system=system_prompt)
        return response["response"].strip()
    else:
        return current_message


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
