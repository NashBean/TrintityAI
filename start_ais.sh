#!/bin/bash
# start_ais.sh - Start Abraham, Moses, Jesus servers

echo "Starting AbrahamAI on port 5001..."
cd ~/code/AbrahamAI
python3 AbrahamAI_Server.py &
sleep 2

echo "Starting MosesAI on port 5002..."
cd ~/code/MosesAI
python3 MosesAI_Server.py &
sleep 2

echo "Starting JesusAI on port 5003..."
cd ~/code/JesusAI
python3 JesusAI_Server.py &
sleep 2

echo "All three AIs running! Now start TrinityAI..."
echo "In another terminal: cd ~/code/TrintityAI && python3 TrinityAI_Server.py"