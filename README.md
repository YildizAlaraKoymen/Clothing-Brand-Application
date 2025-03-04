# Clothing-Brand-Application
A client-server application for a clothing brand based on Transmission Control Protocol (TCP) developed with object oriented principles.

Python version 3.12
Operating system: Windows 11

Program Testing
Conducted extensive testing on the following aspects:
Authentication Testing: Verified login functionality with valid and invalid credentials.
Concurrency Testing: Ensured that multiple clients (store owners and analysts) could interact with the server simultaneously without data corruption.
File Handling Tests: Validated correct reading/writing operations on users.txt, items.txt, and operations.txt.
Error Handling: Simulated scenarios such as purchasing out-of-stock items, returning unpurchased items, and incorrect input formats.
GUI Usability Testing: Ensured smooth navigation and accurate display of messages in both store and analyst panels.

How to Run the Application
Start the Server:
python server.py
Run the Client Application:
python client.py

Login Credentials:
Example Store Login: dereboyucd1 | Password: 12a1
Example Analyst Login: gregoryhouse | Password: 2b9c
Can check other example login credentials via users.txt file.

File Descriptions
server.py: Implements the server logic for handling client requests, authentication, and data operations.
client.py: Provides the user interface for store owners and analysts to interact with the system.
users.txt: Stores user credentials and roles. {WILL BE TURNED INTO A DATABASE SYSTEM}
items.txt: Maintains clothing items' details, including stock and price. {WILL BE TURNED INTO A DATABASE SYSTEM}
operations.txt: Logs all purchase and return transactions. {WILL BE TURNED INTO A DATABASE SYSTEM}

Additional Notes
The project adheres to modular coding principles for maintainability and scalability.
Thread synchronization is managed using RLock to handle concurrent access to shared files.

