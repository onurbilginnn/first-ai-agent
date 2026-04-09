from google import genai
from google.genai import types

import os
import sys
import argparse
from dotenv import load_dotenv

from prompts import system_prompt
from config import GEMINI_MODEL
from call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("user_prompt", type=str, help="User prompt")
args = parser.parse_args()
messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

client = genai.Client(api_key=api_key)

for _ in range(20):
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0,
            tools=[available_functions],
        ),
    )

    if response.candidates is None or len(response.candidates) == 0:
        raise RuntimeError("No response candidates received")
    else:
        for candidate in response.candidates:
            messages.append(candidate.content)

    if response.usage_metadata is None:
        raise RuntimeError("Usage data not available")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.function_calls and len(response.function_calls) > 0:
        function_results = []
        for function_call in response.function_calls:
            # print(f"Calling function: {function_call.name}({function_call.args})")
            function_call_result = call_function(function_call, verbose=args.verbose)
            if function_call_result.parts[0].function_response is None:
                raise Exception("Function call failed")
            if function_call_result.parts[0].function_response.response is None:
                raise Exception("Function call has no response")
            function_results.append(function_call_result.parts[0])
            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
        messages.append(types.Content(role="user", parts=function_results))
    else:
        print(f"Response:\n{response.text}")
        break
else:
    print("Error: maximum iterations reached without a final response")
    sys.exit(1)

