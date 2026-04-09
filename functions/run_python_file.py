import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if valid_target_file is False:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if os.path.isfile(target_file) is False:
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        command = ["python", target_file]
        command.extend(args or [])
        command_result = subprocess.run(command, stderr=subprocess.PIPE, text=True, stdout=subprocess.PIPE, timeout=30, check=True)
        if command_result.returncode != 0:
            return "Process exited with code X"
        if command_result.stderr == "" and command_result.stdout == "":
            return "No output produced"
        if command_result.stderr != "":
            return f"STDERR: {command_result.stderr.strip()}"
        if command_result.stdout != "":
            return f"STDOUT: {command_result.stdout.strip()}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file in a specified directory relative to the working directory, with optional command-line arguments, and return the output or errors produced by the execution",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of command-line arguments to pass to the Python file during execution",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)