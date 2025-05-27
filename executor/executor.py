from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import tempfile
import os
import json

app = FastAPI()

class CodeExecutionRequest(BaseModel):
    code: str
    language: str

@app.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    code = request.code
    language = request.language

    if language.lower() != "python":
        return {"success": False, "output": "", "error": "Only Python is supported"}

    try:
        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        # Execute the Python file with a timeout
        process = subprocess.run(
            ['python', tmp_path],  # Changed 'python3' to 'python'
            capture_output=True,
            text=True,
            timeout=5  # prevent infinite loops
        )

        # Clean up temp file
        os.remove(tmp_path)

        result = {
            "success": process.returncode == 0,
            "output": process.stdout,
            "error": process.stderr if process.returncode != 0 else ""
        }

        # Jika output bisa di-decode sebagai JSON, kembalikan sebagai dict
        try:
            result["parsed_output"] = json.loads(result["output"])
        except Exception:
            result["parsed_output"] = None

        return result

    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Execution timed out"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
