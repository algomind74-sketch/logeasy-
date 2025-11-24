import csv
import random
from datetime import datetime, timedelta

# --- Configuration ---
LOG_LEVELS = ["INFO", "WARN", "ERROR", "SECURITY"]
SERVICES = ["PaymentAPI", "AuthService", "BankConnector", "UserDB", "WebApp"]

# Message templates for different log types
MSG_TEMPLATES = {
    "INFO": [
        "Transaction successful ID: {id}",
        "User {id} logged in",
        "Data fetched for UserID: {id}",
        "Service status OK",
    ],
    "WARN": [
        "Response time exceeded 2000ms",
        "Database connection pool at 80% capacity",
        "Invalid input for UserID: {id}",
    ],
    "ERROR": [
        "Payment failed: Bank server timeout",
        "Critical: Database connection failed",
        "AuthService token validation failed",
        "Service {service} is down",
    ],
    "SECURITY": [
        "Suspicious login attempt from IP: {ip}",
        "Multiple failed payment attempts for UserID: {id}",
        "Potential SQL injection attempt detected",
    ]
}

# Helper function to create a single log line
def create_log_line(log_level, timestamp):
    service = random.choice(SERVICES)
    
    # Get a message template
    template = random.choice(MSG_TEMPLATES[log_level])
    
    # Fill in the template
    message = template.format(
        id=random.randint(1000, 9999),
        service=service,
        ip=f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    )
    
    return [timestamp.isoformat(), log_level, service, message]

# --- Main Script ---
def generate_log_file(filename, total_logs, scenario):
    print(f"Generating {filename}...")
    start_time = datetime.now() - timedelta(days=1)  # Logs from the last 24 hours
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "LogLevel", "ServiceID", "Message"]) # Header row
        
        for i in range(total_logs):
            # Move time forward randomly
            current_time = start_time + timedelta(seconds=random.randint(1_800, 86_000)) # Random time in the day
            
            if scenario == "normal":
                # 95% INFO, 3% WARN, 2% ERROR
                if random.random() < 0.95:
                    log_level = "INFO"
                elif random.random() < 0.6: # (of the remaining 5%)
                    log_level = "WARN"
                else:
                    log_level = "ERROR"
            
            elif scenario == "critical":
                # Simulate a "critical event" burst between 03:00 and 03:10
                event_start = start_time.replace(hour=3, minute=0, second=0)
                event_end = event_start + timedelta(minutes=10)
                
                # Force 20% of logs to be in this window
                if random.random() < 0.20:
                    current_time = event_start + timedelta(seconds=random.randint(1, 600))
                    log_level = "ERROR"
                else:
                    # Normal behavior outside the window
                    log_level = "INFO" if random.random() < 0.98 else "WARN"
            
            elif scenario == "security":
                # 10% of logs are SECURITY threats
                if random.random() < 0.10:
                    log_level = "SECURITY"
                else:
                    log_level = "INFO"
            
            writer.writerow(create_log_line(log_level, current_time))
            
    print(f"Successfully created {filename} with {total_logs} logs.\n")

# --- Run the generation ---
if __name__ == "__main__":
    total_logs_per_file = 10000
    
    generate_log_file("normal_day.csv", total_logs_per_file, "normal")
    generate_log_file("critical_event.csv", total_logs_per_file, "critical")
    generate_log_file("security_threat.csv", total_logs_per_file, "security")
    
    print("All log files generated successfully.")