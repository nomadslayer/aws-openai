from openai import OpenAI
import dotenv
import os
import sys
import time

# Grab the OpenAI API key from the .env file with python-dotenv:
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
iterations = 2

OpenAI.api_key = OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY
    )

if client:
    print("Connected to OpenAI")

with open('instructions.txt', 'r') as f:
    instructions = f.read()

PROMPT = "Deploy an infrastructure in AWS by using Terraform. Your task is to read the instructions provided in natural language, translate them into a Terraform syntax file. Your output should only be in Raw Terraform syntax without any commentary. If you choose to include commentary to the code, you shall always include it as a comment in the code by using a pound (#) symbol"
PROMPT_VALIDATE = "Deploy an infrastructure in AWS by using Terraform. Your task is to read the terraform syntax file and validate it. Your conclusion should be in the following format: 'true' or 'false'. if false, then explain why"

def processor(prompt, instructions):
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
               {"role": "system", "content": prompt},
               {"role": "user", "content": instructions}
                   ]
        )    
    return response.choices[0].message.content


def run_terraform_command(command, cwd=None):
    import subprocess
    """
    Runs a Terraform command in the specified directory and prints the output.

    :param command: The Terraform command to run as a list of strings.
    :param cwd: The current working directory to execute the command in.
    """
    try:
        # Execute the Terraform command with the specified current working directory
        result = subprocess.run(command, check=True, text=True, capture_output=True, cwd=cwd)

        # Print the standard output
        print("Output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        # Print the standard error if the command fails
        print("Error:\n", e.stderr)

print("First Step: Generate")
TERRAFORM_FILE = processor(PROMPT, instructions)
print("Second Step: Validate")
TERRAFORM_VALIDATE = processor(PROMPT_VALIDATE, TERRAFORM_FILE)

new_dir = sys.argv[1]
os.mkdir("output/" + new_dir)

i = 1
while i <= iterations:
    if "true" in TERRAFORM_VALIDATE.lower():
        print("[+] Terraform syntax is valid")
        time.sleep(1)
            # if TERRAFORM_FILE has Markdown Syntax:
        TERRAFORM_FILE = TERRAFORM_FILE.replace("```hcl", "")
        TERRAFORM_FILE = TERRAFORM_FILE.replace("```", "")
        with open("output/" + new_dir + "/main.tf", "w") as f:
            f.write(TERRAFORM_FILE)
        run_terraform_command(["terraform", "validate", "output/" + new_dir])
    else:
        print("***********TERRAFORM_VALIDATE_OUTPUT***********")
        print(TERRAFORM_VALIDATE)
        print("___________END OF TERRAFORM_VALIDATE_OUTPUT***********")
        print(f"[ Iteration no. {str(i)}/{str(iterations)} ] - Terraform syntax is invalid. Running again")
        instructions = "Address this issue: " + TERRAFORM_VALIDATE + "Problematic main.tf contents: " + TERRAFORM_FILE
        correction_prompt = "Please validate the syntax of Terraform files. Your task is to read a set of issues, and the original problematic main.tf, and correct the main.tf file. Do not output any commentary. Only fix the issues. Output only raw hcl or terraform valid syntax, do not use Markdown or backticks  to indicate the hcl format"
        TERRAFORM_VALIDATE = processor(correction_prompt, instructions)
    i += 1 
