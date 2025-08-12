from openai import OpenAI
import os

# Initialize client using environment variables. Avoid hardcoding secrets.
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

SYS_PROMPT_SWEBENCH = """
You are a careful, iterative coding assistant. Plan before acting, apply small changes, and test after each step. Keep going until the problem is fully solved and validated.
"""

PYTHON_TOOL_DESCRIPTION = """This function executes Python code or terminal commands in a stateful environment. Internet access is disabled.

You can also pass an apply_patch block. The expected structure is:

%%bash
apply_patch <<"EOF"
*** Begin Patch
[YOUR_PATCH]
*** End Patch
EOF

Where [YOUR_PATCH] is in the V4A diff format with entries like:
*** Add File: path/to/file
*** Update File: path/to/file
*** Delete File: path/to/file

Note: File paths must be relative. The tool prints "Done!" at the end; check prior output lines for warnings or errors.
"""

python_bash_patch_tool = {
    "type": "function",
    "name": "python",
    "description": PYTHON_TOOL_DESCRIPTION,
    "parameters": {
        "type": "object",
        "strict": True,
        "properties": {
            "input": {
                "type": "string",
                "description": "Python code, a terminal command prefixed with !, or an apply_patch block.",
            }
        },
        "required": ["input"],
    },
}

def run_example():
    # Choose a lightweight, widely available model. Override via OPENAI_MODEL if needed.
    model = os.environ.get("OPENAI_MODEL", "gpt-5")

    # Provide your task/bug description here.
    user_task = "Please fix the type error in module X and add a unit test."

    response = client.responses.create(
        model=model,
        instructions=SYS_PROMPT_SWEBENCH,
        tools=[python_bash_patch_tool],
        input=user_task,
        tool_choice="auto",  # Let the model decide when to call the tool
    )

    # For SDKs that support it, output_text is a convenient accessor.
    # Fallback to dict if not available in your installed SDK version.
    try:
        print(response.output_text)
    except Exception:
        print(response.to_dict())

if __name__ == "__main__":
    # This script is an example and will perform a live API call if run.
    # Ensure OPENAI_API_KEY is set and you accept usage before running.
    run_example()
