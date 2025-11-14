# cli_tool.py
import argparse
import base64
import json
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True)
    args = parser.parse_args()

    t0 = time.perf_counter()
    binary = base64.b64decode(args.payload)
    time.sleep(1.1)
    t1 = time.perf_counter()

    result = {
        "processed_bytes": len(binary),
        "calculation_time": t1 - t0,
    }
    print(result)

    print(json.dumps(result))
