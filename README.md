# PoC: Using OpenAI to generate Terraform Planning and Validation

This is a quick PoC made to test the idea of "Using AI to generate Terraform templates?"

# IMPORTANT

This is a PoC, and it's not meant to be used in production or any serious use and it just serves to test the idea of using LLMs to generate IaC (Infrastructure as code) plans. 

## Background

It's made really clear by now that LLMs like GPT4 are decent in writing some code, but Terraform applied to AWS requires a little bit more depth and intersection of different skills and knowledge. For me TF is an extremely abstract way of representing (Planning) a very complex environment, and I wanted to test this idea of how LLM would score in actually planning an AWS deployment.

## What this program does

- From a language description of the infrastructure (instructions.txt), this program will use GPT-4 to generate a main.tf file that will < attempt > to replicate the instructions.
- This works in 2 steps:
    - Make GPT4 generate the first main.tf file,
    - Validate its content, syntax, alignment with the original language instructions again with GPT4,
    - "If" everything is okay (Re-validation by GPT4 itself again), then write the main.tf to an actual file,
    - Validate the main.tf written in} `./output/` folder (Which name is specified as an argument of the program) with `Terraform validate` and just display the output to stdout.

## Iterative method:

- First OpenAI GPT4 will interpret the language instructions given, and will generate an HCL terraform-valid syntax output.
- Then, another iteration of OpenAI GPT4 will validate the syntax of the output HCL file with Terraform and "test" this output by comparing the results with the original instructions (Basically, "Is this HCL Terraform valid? according to this instructions?").
- It will iterate until the output is "correct" or until the iteration limit is exhausted (As specified in the main script. Originally I left 2 iterations, which maybe would work with more but it can get a little bit expensive just for a PoC).

# Conclusions

- 50% of the time it got the answer correct which is way more than what I expected at first.
- It needs more testing, since the instructions, while comprehensive (At least considering it's just a PoC), do not specify SSH keys (This was the thing that tripped GPT the most) or other details that are important for Terraform.
- Of course, it's only a matter of time when there's something in the industry that does this.



