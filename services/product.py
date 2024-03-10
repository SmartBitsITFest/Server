import ollama

async def prompt_llama_model(prompt):
    # Create an instance of the OpenAI GPT-3 model
    model = ollama.AsyncClient()

    # Generate a response to the prompt
    response = model.generate('notux', prompt)

    # Return the response
    return await response