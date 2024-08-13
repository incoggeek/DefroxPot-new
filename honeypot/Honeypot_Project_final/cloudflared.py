# Cloudflared
# This class represents a launching cloudflared tunnel

import signal
from .mydesign import *
from . import mydesign

class CloudFlared:
    
    cloudflared_url = ''
    process = None

    @staticmethod
    def run_cloudflared(action):

        if action == 1:
            # Define the command to execute
            command_process = ["cloudflared", "tunnel", "--url", "http://localhost:5000"]

            # Define a regex pattern to find URLs
            url_pattern = r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com'

            try:
                # Start the subprocess
                CloudFlared.process = subprocess.Popen(command_process, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                # Read the output line by line
                for line in CloudFlared.process.stdout:
                    # Use re.findall to extract all URLs that match the pattern
                    urls = re.findall(url_pattern, line)

                    # Print the extracted URLs
                    for url in urls:
                        #print(url)
                        CloudFlared.cloudflared_url = url
            except FileNotFoundError:
                print("Error: The executable file was not found. Please check the path.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        
        elif action == 0:
            if CloudFlared.process:
                os.kill(CloudFlared.process.pid, signal.SIGINT)
                # Wait for the process to terminate
                CloudFlared.process.wait()
            
    @staticmethod
    def get_val():
        # url = CloudFlared.cloudflared_url
        # s =  pyshorteners.Shortener()
        # short_url = s.tinyurl.short(url)
        return CloudFlared.cloudflared_url