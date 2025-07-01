from server import Server

server = Server()
app = server.app


def start():
    import uvicorn

    print("🚀 Starting FastAPI server on port 5000...")
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)


if __name__ == "__main__":
    start()
