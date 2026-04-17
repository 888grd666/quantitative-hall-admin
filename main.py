import subprocess
import sys
import os

os.system("pip install streamlit requests -q")

os.system("streamlit run app.py --server.port=8501 --server.address=0.0.0.0")
