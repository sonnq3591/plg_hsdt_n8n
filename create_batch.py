#!/usr/bin/env python3
"""
Fresh BatchID Creator for n8n
Creates NEW BatchID with current timestamp every time it runs
Format: YYYYMMDDTHHMMSS
Saves to current_batch.txt
"""

import os
from datetime import datetime

def create_fresh_batch():
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate NEW BatchID with current timestamp
    batch_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    
    # Save to current_batch.txt (replace existing content)
    batch_file = os.path.join(script_dir, "current_batch.txt")
    
    with open(batch_file, "w") as f:
        f.write(batch_id)
    
    print(f"Fresh BatchID created: {batch_id}")
    return batch_id

if __name__ == "__main__":
    create_fresh_batch()