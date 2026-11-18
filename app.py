from flask import Flask, render_template, redirect, abort, request, jsonify
from database import (
    init_db,
    get_original_url,
    save_link,
    increment_clicks,
    get_recent_links,
)
from validators import validate_url


# Create our web application.
# __name__ tells Flask where this file lives.
app = Flask(__name__)
#Create table on start-UP
init_db() 

# A "route" connects a web address to a Python function.
# "/" is the home page address.
@app.route("/")
def home():
    # Whatever we return is sent back to the browser
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    # Read the text the user typed (the input is named "url")
    raw_url = request.form.get("url", "")

    cleaned_url, error_message = validate_url(raw_url)

    # If validation failed, send the error back with status 400
    if error_message is not None:
        return jsonify({"error": error_message}), 400

    short_code = save_link(cleaned_url)

    # host_url is our own site address, like "http://127.0.0.1:5000/"
    short_url = request.host_url + short_code

    return jsonify({
        "short_code": short_code,
        "short_url": short_url,
        "original_url": cleaned_url,
    }), 201


@app.route("/api/recent")
def recent_links():
    links = get_recent_links()

    # Add the full short address to each link
    for link in links:
        link["short_url"] = request.host_url + link["short_code"]

    return jsonify(links)

@app.route("/<short_code>")
def redirect_to_original(short_code):
    original_url = get_original_url(short_code)

    # No link with this code: show a 404 "Not Found" page
    if original_url is None:
        abort(404)

    increment_clicks(short_code)
    
    return redirect(original_url)


# This block only runs when we start the file directly
if __name__ == "__main__":
    # debug=True restarts the server automatically when we save changes
    # and shows helpful error pages while we're learning
    app.run(debug=True)