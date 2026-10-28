import os
import sys

# Forwarder to run from repository root if Root Directory is not specified
cur_dir = os.path.dirname(os.path.abspath(__file__))
sch_dir = os.path.join(cur_dir, "scholarship_system")
if sch_dir not in sys.path:
    sys.path.insert(0, sch_dir)

from scholarship_system.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
