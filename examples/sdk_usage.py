from llm_gateway import ChatRequest, LLMGateway


gateway = LLMGateway()
response = gateway.complete(
    ChatRequest(prompt="Analyze the cost tradeoff of routing easy tasks to smaller models.")
)

print(response.model_dump_json(indent=2))

