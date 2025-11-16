# Purpose
- PoC to understand what data is available from a Fritzbox 7490 
- Understand what security measures are involved and how easily data can be retrived.

# Audience 
- limited to me - an expereienced programmer - and claude code

# Architecture 
- poc wil be a simple command line program in python 3.13
- program will be driven by the uv package managers
- program parameters using rich-argparse
- input parameters should be ip address, username, password
- input parameters should be echoed

# Details
- will use the python library "fritzconnection"
- output should dump all available data to the console
- outpud data should be color coded for easy reading
- total time needed for data retreived and number of bytes retrieved should be output
- total time needed for execution of entire program should also be output
