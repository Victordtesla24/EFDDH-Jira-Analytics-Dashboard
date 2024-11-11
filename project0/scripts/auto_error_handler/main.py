import uvicorn
from .runtime_manager import RuntimeManager
from .web_interface import WebInterface

def setup_application():
    runtime = RuntimeManager()
    web_interface = WebInterface(runtime)
    runtime.register_web_interface(web_interface)
    return runtime, web_interface

async def main():
    runtime, web_interface = setup_application()
    await runtime.initialize()

if __name__ == "__main__":
    uvicorn.run(
        "auto_error_handler.web_interface:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["auto_error_handler"]
    )