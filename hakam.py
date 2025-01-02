from flask import Flask, request, Response
import requests
import datetime

app = Flask(__name__)

# Function to get geolocation data from IP address
def get_geolocation(ip):
    try:
        # Use a public IP geolocation API like ipinfo.io
        api_url = f"http://ipinfo.io/{ip}/json"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            # Extract latitude and longitude from "loc" field if available
            loc = data.get("loc", "0,0").split(",")
            return {
                "ip": data.get("ip"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "latitude": loc[0] if len(loc) > 1 else "0",
                "longitude": loc[1] if len(loc) > 1 else "0",
                "org": data.get("org"),
                "postal": data.get("postal")
            }
        else:
            return {"error": "Unable to fetch location"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def track_user():
    # Get IP address from X-Forwarded-For header or request.remote_addr
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Get geolocation data
    location_data = get_geolocation(ip_address)

    # Get user-agent
    user_agent = request.headers.get('User-Agent', 'Unknown User-Agent')

    # Get timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log entry
    log_entry = {
        "timestamp": timestamp,
        "ip_address": ip_address,
        "location": location_data,
        "user_agent": user_agent
    }

    # Save the log to a file
    log_file_name = "scammer_log.txt"
    with open(log_file_name, "a") as log_file:
        log_file.write(f"{log_entry}\n")

    print(f"Logged data: {log_entry}")

    # Automatically trigger download of the log file
    with open(log_file_name, "r") as log_file:
        log_content = log_file.read()

    return Response(
        log_content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment;filename={log_file_name}"
        }
    )

if __name__ == "__main__":
    # Change the port to 8080
    app.run(host="0.0.0.0", port=8080, debug=True)