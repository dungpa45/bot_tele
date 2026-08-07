"""
Script để test bot commands ở local, gửi thật đến Telegram.
Usage:
    python local_test.py <chat_id> <command>
    python local_test.py <chat_id>              # interactive mode

Ví dụ:
    python local_test.py 123456789 /tygia
    python local_test.py 123456789 /gold
    python local_test.py 123456789              # nhập command liên tục
"""
import os, sys, yaml

# Load secrets từ secret.yaml vào env
with open(os.path.join(os.path.dirname(__file__), "secret.yaml")) as f:
    secrets = yaml.safe_load(f)
for k, v in secrets.items():
    os.environ.setdefault(k, str(v))

from linhtinh_aws_lambda import lambda_handler
import json

def make_event(chat_id, text):
    return {
        "body": json.dumps({
            "message": {"chat": {"id": int(chat_id)}, "text": text}
        })
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    chat_id = sys.argv[1]

    # Single command mode
    if len(sys.argv) >= 3:
        command = " ".join(sys.argv[2:])
        print(f"Sending: {command}")
        resp = lambda_handler(make_event(chat_id, command), None)
        print(f"Response: {resp}")
        return

    # Interactive mode
    print(f"Interactive mode - Chat ID: {chat_id}")
    print("Nhập command (hoặc 'q' để thoát):\n")
    while True:
        command = input("> ").strip()
        if command.lower() in ("q", "quit", "exit"):
            break
        if not command:
            continue
        resp = lambda_handler(make_event(chat_id, command), None)
        print(f"Response: {resp}\n")

if __name__ == "__main__":
    main()
