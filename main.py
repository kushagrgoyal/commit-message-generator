import argparse
from ollama import Client
from utils import (
    get_git_changes,
    generate_commit_message_ollama,
    generate_short_description_ollama,
    read_style_guide,
    update_commit_message_ollama,
    copy_to_clipboard,
)


# Initialize Ollama client and model
ollama_client = Client(host="http://localhost:11434")
model_name = "phi3.5:latest"


def main():
    parser = argparse.ArgumentParser(description="Generate Git commit messages using LLM.")
    parser.add_argument("--style", default="style_guide.txt", help="Path to the style guide file")
    args = parser.parse_args()

    changes = get_git_changes()
    if not changes:
        return

    style_guide = read_style_guide(args.style)
    if not style_guide:
        return

    commit_message = generate_commit_message_ollama(
        ollama_client=ollama_client, model=model_name, changes=changes, style_guide=style_guide
    )
    short_description = generate_short_description_ollama(
        ollama_client=ollama_client, model=model_name, commit_message=commit_message
    )
    print("\nGenerated commit message:")
    print(commit_message)
    print("\nGenerated short description:")
    print(short_description)

    choice = input("\nDo you want to (u)pdate or (f)inalize? [u/f]: ").lower()

    while choice == "u":
        commit_message = update_commit_message_ollama(
            ollama_client=ollama_client, model=model_name, current_message=commit_message
        )
        print("\nUpdated commit message:")
        print(commit_message)
        choice = input("\nDo you want to (u)pdate or (f)inalize? [u/f]: ").lower()
    if choice == "f":
        copy_to_clipboard(commit_message)
        print("\nFinal commit message:")
        print(commit_message)


if __name__ == "__main__":
    main()
