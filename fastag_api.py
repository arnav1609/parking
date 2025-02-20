from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# 🔗 Connect to Firebase
cred = credentials.Certificate("your-firebase-key.json")  # ✅ Ensure this file exists
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smart-parking-fd6ea-default-rtdb.asia-southeast1.firebasedatabase.app"
})

PARKING_FEE = 100  # Fixed parking fee for this simulation

# 🌟 Set Up Initial Data in Firebase (if not present)
default_data = {
    "fastags": {
        "ABC123": {
            "owner": "John Doe",
            "balance": 500,
            "status": "active"
        },
        "XYZ789": {
            "owner": "Jane Smith",
            "balance": 50,
            "status": "active"
        },
        "DEF456": {
            "owner": "Sam Wilson",
            "balance": 0,
            "status": "inactive"
        }
    }
}

ref = db.reference("/")
existing_data = ref.get()

if existing_data is None:
    ref.set(default_data)
    print("🔥 Default data added to Firebase!")
else:
    print("✅ Data already exists in Firebase.")

# 🌟 Home Route
@app.route("/")
def home():
    return "Fastag API is running!"

# 🌟 Verify FASTag and Deduct Parking Fee
@app.route("/fastag", methods=["GET"])
def verify_fastag():
    """ Verifies FASTag and deducts parking fee from Firebase """
    fastag_id = request.args.get("id")

    if not fastag_id:
        return "FASTag ID Missing!", 400

    ref = db.reference(f"/fastags/{fastag_id}")
    user_data = ref.get()

    if user_data:
        if user_data["status"] == "inactive":
            return "FASTag Blocked!", 403

        if user_data["balance"] >= PARKING_FEE:
            new_balance = user_data["balance"] - PARKING_FEE
            ref.update({"balance": new_balance})

            return f"Payment Successful!\nOwner: {user_data['owner']}\nRemaining Balance: {new_balance}", 200
        else:
            return "Insufficient Balance!", 402

    return "FASTag Not Found!", 404

# 🌟 Recharge FASTag
@app.route("/fastag/recharge", methods=["POST"])
def recharge_fastag():
    """ Adds balance to FASTag account in Firebase """
    data = request.json
    fastag_id = data.get("id")
    amount = data.get("amount")

    if not fastag_id or not amount:
        return jsonify({"message": "FASTag ID and Amount Required!", "success": False}), 400

    ref = db.reference(f"/fastags/{fastag_id}")
    user_data = ref.get()

    if user_data:
        new_balance = user_data["balance"] + amount
        ref.update({"balance": new_balance})

        return jsonify({
            "message": "Recharge Successful!",
            "owner": user_data["owner"],
            "new_balance": new_balance,
            "success": True
        }), 200

    return jsonify({"message": "FASTag Not Found!", "success": False}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

 



