from app import create_app
from setup_database import setup_database

app = create_app()

if __name__ == '__main__':
    # Initialize DB schema and admin accounts if missing
    setup_database()
    
    print("\n========================================================")
    print(" [+] Blockchain Certificate Verification System Started!")
    print(" [+] Application URL: http://localhost:5000")
    print(" [+] Public Verification: http://localhost:5000/verify")
    print(" [+] Admin Portal: http://localhost:5000/login")
    print("========================================================\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
