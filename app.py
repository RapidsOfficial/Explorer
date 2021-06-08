from backend import create_app
import config

app = create_app()

if __name__ == "__main__":
    app.run(
        debug=config.debug,
        host=config.host,
        port=config.port
    )
