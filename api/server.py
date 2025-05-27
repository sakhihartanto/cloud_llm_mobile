import os
import io
import json
import yaml
import base64
import asyncio
import httpx
from pathlib import Path
from PIL import Image, ImageDraw
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path direktori statis
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(current_dir)), name="static")

# Executor endpoint
EXECUTOR_URL = os.getenv("EXECUTOR_URL", "http://executor:9000/execute")

# Fungsi untuk eksekusi kode ke executor container
async def run_code_in_executor(code: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(EXECUTOR_URL, json={"code": code, "language": "python"})
        resp.raise_for_status()
        return resp.json()

# Fungsi untuk buat gambar base64 dari text
def create_mock_image(text: str) -> str:
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 40), text, fill='black')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    encoded = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"

@app.get("/", response_class=HTMLResponse)
async def root():
    return (current_dir / "index.html").read_text()

@app.get("/healthz")
async def health():
    return {"status": "ok"}

@app.post("/stream-query")
async def stream_query(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "").strip()

    if not prompt:
        return {"error": "Prompt is empty"}

    async def event_generator():
        code_to_run = f'''
import json

prompt = {json.dumps(prompt)}

data = {{
    "analysis": {{
        "input": f"User prompt: {{prompt}}",
        "metrics": {{
            "words": len(prompt.split()),
            "characters": len(prompt)
        }},
        "results": [
            {{"type": "word_count", "value": len(prompt.split())}},
            {{"type": "char_count", "value": len(prompt)}}
        ]
    }}
}}

print(json.dumps(data, indent=2))
'''

        yield {
            "event": "code",
            "data": json.dumps({"code": code_to_run, "language": "python"})
        }

        await asyncio.sleep(1)

        try:
            result_dict = await run_code_in_executor(code_to_run)
        except Exception as e:
            yield {
                "event": "text",
                "data": json.dumps({"text": f"Error contacting executor: {str(e)}"})
            }
            return

        if result_dict.get("error"):
            yield {
                "event": "text",
                "data": json.dumps({"text": f"Error in execution:\n{result_dict['error']}"})
            }
        elif result_dict.get("parsed_output"):
            yaml_output = yaml.dump(result_dict["parsed_output"], sort_keys=False, allow_unicode=True)
            yield {
                "event": "text",
                "data": json.dumps({"text": f"Results in YAML format:\n{yaml_output}"})
            }
            try:
                word_count = result_dict["parsed_output"]["analysis"]["metrics"]["words"]
                image_data = create_mock_image(f"Word count: {word_count}")
                yield {
                    "event": "image",
                    "data": json.dumps({"url": image_data})
                }
            except KeyError:
                pass
        else:
            yield {
                "event": "text",
                "data": json.dumps({"text": "No valid output received from executor."})
            }

        yield {
            "event": "text",
            "data": json.dumps({"text": "Completed"})
        }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
