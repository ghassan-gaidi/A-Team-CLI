import asyncio
from ateam.core import ConfigManager
from ateam.providers import ProviderFactory, ProviderConfig
from ateam.security import SecureAPIKeyManager

async def test():
    try:
        km = SecureAPIKeyManager()
        config = ConfigManager()
        agent_name = "Architect"
        agent = config.get_agent(agent_name)
        key = km.get_key("gemini")
        
        print(f"Testing Agent: {agent_name}")
        print(f"Provider: {agent.provider}")
        print(f"Model: {agent.model}")
        
        provider_config = ProviderConfig(
            model_name=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )
        provider = ProviderFactory.create(
            agent.provider, 
            provider_config, 
            key
        )
        
        messages = [{"role": "user", "content": "Hello, Architect! Are you there?"}]
        system_prompt = "You are the Architect."
        
        print("Sending request...")
        response = await provider.complete(messages, system_prompt=system_prompt)
        print(f"\nResponse from {agent.model}:")
        print("-" * 20)
        print(response.content)
        print("-" * 20)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
