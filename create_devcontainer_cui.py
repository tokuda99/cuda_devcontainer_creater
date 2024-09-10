import os
from rich import print
from rich.prompt import Prompt
from rich.table import Column, Table
from rich.console import Console
from rich.tree import Tree
from rich.text import Text
from rich.padding import Padding
from version_map import UBUNTU_CUDA_MAP, CUDA_PYTORCH_MAP


def write_devcontainer_file(
    project_name: str,
    user_name: str,
    ubuntu_version: str,
    use_cuda: str,
    cuda_version: str,
    use_pytorch: str,
):
    with open(".devcontainer/devcontainer.json", "w") as f:
        f.write(f"""{{
    "name": "{project_name}",
    "dockerComposeFile": "docker-compose.yml",
    "service": "{project_name}",
    "workspaceFolder": "/home/{user_name}/{project_name}",
    "initializeCommand": "ls",
    "customizations": {{
        "vscode": {{
            "settings": {{
                "files.insertFinalNewline": true,
                "files.trimTrailingWhitespace": true,
                "files.trimFinalNewlines": true,
                "[python]": {{
                    "editor.defaultFormatter": "ms-python.black-formatter",
                    "editor.formatOnSave": false
                }},
                "[dockerfile]": {{
                    "editor.defaultFormatter": "ms-azuretools.vscode-docker"
                }}
            }},
            "extensions": [
                "mhutchie.git-graph",
                "foxundermoon.shell-format",
                "ms-azuretools.vscode-docker",
                "GitHub.vscode-pull-request-github",
                "redhat.vscode-yaml",
                "yzhang.markdown-all-in-one",
                "GitHub.copilot",
                "tht13.python",
                "ms-python.python",
                "ms-toolsai.jupyter",
                "ms-python.vscode-pylance",
                "KevinRose.vsc-python-indent",
                "ms-python.black-formatter"
            ]
        }}
    }}
}}""")


def write_dockerfile(
    use_cuda: str, cuda_version: str, use_pytorch: str, pytorch_version: str
):
    with open(".devcontainer/Dockerfile", "w") as f:
        if use_cuda == "yes":
            if use_pytorch == "yes":
                f.write(
                    f"""FROM pytorch/pytorch:{pytorch_version}-cuda{cuda_version}-cudnn8-runtime"""
                )
            else:
                f.write(f"""FROM nvidia/cuda:{cuda_version}-cudnn8-devel-ubuntu20.04""")
        else:
            f.write(f"""FROM ubuntu:20.04""")


def write_docker_compose_file(
    project_name: str,
    user_name: str,
    use_cuda: str,
    cuda_version: str,
    use_pytorch: str,
    pytorch_version: str,
):
    with open(".devcontainer/docker-compose.yml", "w") as f:
        f.write(f"""version: '3.7'
services:
    {project_name}:
        build:
            context: .
            dockerfile: Dockerfile
        volumes:
            - ..:/workspace
        environment:
            - USER={user_name}
            - USE_CUDA={use_cuda}
            - USE_PYTORCH={use_pytorch}
            - PYTORCH_VERSION={pytorch_version}
            - CUDA_VERSION={cuda_version}
        command: /bin/bash
        tty: true
        stdin_open: true
        user: root
        working_dir: /workspace/{project_name}
        networks:
            - default
        cap_add:
            - SYS_PTRACE
        security_opt:
            - seccomp:unconfined
            - apparmor:unconfined
        init: true
        shm_size: 2g
        expose:
            - 8888
            - 6006
        ports:
            - "8888:8888"
            - "6006:6006"
        labels:
            - "com.microsoft.created-by=visual-studio-code"
            - "com.microsoft.visual-studio-code.remote-containers=true"
            - "com.microsoft.visual-studio-code.remote-containers.session-id=4b5f9b9e-5c2e-4c5b-8e0b-6e3b3b7e3b6f"
networks:    
    default:
        external: false
        driver: bridge""")


def main():
    current_directory_path: str = os.getcwd()
    current_directory: str = os.path.basename(current_directory_path)
    user_name: str = os.environ.get("USER")
    use_cuda: str = "n"
    use_pytorch: str = "n"
    cuda_version = "N/A"
    pytorch_version = "N/A"

    console = Console(style="bold")
    console.clear()
    console.print(
        "[royal_blue1]Creating a new devcontainer configuration file[/royal_blue1]"
    )
    project_name = Prompt.ask("[Project name]", default=current_directory)
    user_name = Prompt.ask("[User name]", default="root")
    ubuntu_version = Prompt.ask(
        "[Ubuntu version]", choices=["20.04", "22.04"], default="20.04"
    )
    use_cuda = Prompt.ask("Do you want to use CUDA?", choices=["Y", "n"], default="Y")
    if use_cuda == "Y":
        cuda_version = Prompt.ask(
            "[CUDA version]",
            choices=UBUNTU_CUDA_MAP[ubuntu_version],
            default=UBUNTU_CUDA_MAP[ubuntu_version][-1],
        )
        use_pytorch = Prompt.ask(
            "Do you want to use PyTorch?", choices=["Y", "n"], default="Y"
        )
        if use_pytorch == "Y":
            pytorch_version = Prompt.ask(
                "[PyTorch version]",
                choices=CUDA_PYTORCH_MAP[cuda_version],
                default=CUDA_PYTORCH_MAP[cuda_version][-1],
            )

    table = Table(
        show_header=True,
        header_style="bold",
        title="New environment configuration",
        expand=True,
    )
    table.add_column("Project Name", style="green", justify="center")
    table.add_column("User Name", style="green", justify="center")
    table.add_column("Ubuntu Version", style="green", justify="center")
    table.add_column("CUDA Version", style="green", justify="center")
    table.add_column("PyTorch Version", style="green", justify="center")
    table.add_row(
        project_name,
        user_name,
        ubuntu_version,
        cuda_version,
        pytorch_version,
        style="bold green",
    )

    console.print(Padding(table, (0, 4)))

    final_check = Prompt.ask(
        "[italic]Do you want to create the devcontainer configuration file?[/italic]",
        choices=["Y", "n"],
        default="Y",
    )
    if final_check == "Y":
        os.makedirs(".devcontainer", exist_ok=True)
        write_devcontainer_file(
            project_name, user_name, ubuntu_version, use_cuda, cuda_version, use_pytorch
        )
        write_dockerfile(use_cuda, cuda_version, use_pytorch, pytorch_version)
        write_docker_compose_file(
            project_name,
            user_name,
            use_cuda,
            cuda_version,
            use_pytorch,
            pytorch_version,
        )
        tree = Tree(
            f":open_file_folder: {current_directory_path}",
            guide_style="bold bright_blue",
        )
        branch1 = tree.add(":open_file_folder: [green].devcontainer[/green]")
        branch1.add(Text("📄 ") + Text("Dockerfile"))
        branch1.add(Text("📄 ") + Text("docker-compose.yml"))
        branch1.add(Text("📄 ") + Text("devcontainer.json"))
        console.print("[green]Configuration file created successfully[/green]")
        console.print(tree)
    else:
        console.print("[red]Aborted[/red]")
        return


if __name__ == "__main__":
    main()
