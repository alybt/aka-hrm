# Add to requirements.txt
# python-zklib>=0.4.5

from zklib import ZK

def connect_to_zk_device(ip, port):
    zk = ZK(ip, port, timeout=5)
    conn = zk.connect()
    if conn:
        # Get attendance logs
        logs = conn.get_attendance()
        for log in logs:
            # Process each log
            pass
        conn.disconnect()