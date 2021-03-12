def run():
    """
    Run the API server
    """
    import uvicorn

    print("Running API development server")
    uvicorn.run("api.main:app")
