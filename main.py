from App import create_app

app = create_app()

if __name__ == "__main__":
    # socketio.run(app, debug=True)
    app.run(debug=True)