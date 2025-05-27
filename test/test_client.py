import aiohttp
import asyncio
import json
import sys

async def chat_stream(session, message):
    async with session.post(
        'http://localhost:8000/stream-query',
        json={'prompt': message},
        headers={'Content-Type': 'application/json'}
    ) as response:
        async for line in response.content:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])  # Skip 'data: ' prefix
                
                # Print different types of responses
                if data['type'] == 'status':
                    print(f"\033[36mStatus: {data['payload']['text']}\033[0m")  # Cyan
                elif data['type'] == 'text':
                    print(f"\033[32mBot: {data['payload']['text']}\033[0m")  # Green
                elif data['type'] == 'code':
                    print(f"\033[33mCode:\n{data['payload']['code']}\033[0m")  # Yellow
                elif data['type'] == 'image':
                    if data['payload']['url'].startswith('data:image'):
                        print("\033[35mReceived: [Generated Image]\033[0m")  # Purple
                    else:
                        print(f"\033[35mImage URL: {data['payload']['url']}\033[0m")

async def test_health(session):
    async with session.get('http://localhost:8000/healthz') as response:
        print("\n--- Testing Health Endpoint ---")
        print(f"Status: {response.status}")
        print(f"Response: {await response.json()}\n")

async def interactive_chat():u
    async with aiohttp.ClientSession() as session:
        # First check server health
        await test_health(session)
        
        print("Interactive Chat Started")
        print("Type your messages (press Ctrl+C or type 'exit' to quit)")
        print("-" * 50)
        
        while True:
            try:
                # Get user input
                message = input("\033[34mYou: \033[0m")  # Blue
                
                # Check for exit command
                if message.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if message.strip():  # Only process non-empty messages
                    await chat_stream(session, message)
                    print("-" * 50)  # Separator between interactions
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\033[31mError: {str(e)}\033[0m")  # Red error messages
                break

if __name__ == "__main__":
    print("Starting interactive test client...")
    print("Make sure the server is running on http://localhost:8000")
    
    try:
        asyncio.run(interactive_chat())
    except Exception as e:
        print(f"\033[31mFatal Error: {str(e)}\033[0m")
        sys.exit(1) 