from ollama import Client
from utils import (
    arg_parser,
    get_git_changes,
    create_system_prompt,
    generate_commit_message_ollama,
    generate_short_description_ollama,
    read_file,
    update_commit_message_ollama,
    copy_to_clipboard,
)


# Initialize Ollama client and model
ollama_client = Client(host="http://localhost:11434")
model_name = "gemma2:latest"


def main():
    args = arg_parser()

    changes = get_git_changes(args.repo)
    if not changes:
        return
    system_prompt = read_file(args.sprompt)
    if not system_prompt:
        return
    style_guide = read_file(args.style)
    if not style_guide:
        return
    user_instructions = args.instruct

    system_prompt = create_system_prompt(
        system_prompt=system_prompt, style_guide=style_guide, user_instructions=user_instructions
    )

    commit_message = generate_commit_message_ollama(
        ollama_client=ollama_client,
        model=model_name,
        changes=changes,
        system_prompt=system_prompt,
    )
    short_description = generate_short_description_ollama(
        ollama_client=ollama_client,
        model=model_name,
        commit_message=commit_message,
        system_prompt=system_prompt,
    )
    print("\nGenerated commit message:")
    print(commit_message)
    print("\nGenerated short description:")
    print(short_description)

    choice = input("\nDo you want to (u)pdate or (f)inalize? [u/f]: ").lower()

    while choice == "u":
        commit_message = update_commit_message_ollama(
            ollama_client=ollama_client,
            model=model_name,
            current_message=commit_message,
            system_prompt=system_prompt,
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
