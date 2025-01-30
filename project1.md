### HW1 CS356

This project tasked us with creating a client that creates an encrypted web socket connection with a server, and plays a guessing game to return a hidden flag.

I completed this project with an object oriented approach where i created a series of classes to carry out the fucntionality. 

My first class was an argument parser, that took input from the command line for the netid, server, etc.

Next, I created a class for the client. It has a main function 'run' which does most of the functionality. 

First, I create a socket connection. After this is completed, my client begins to send a series of messages through this sock pipe.

First is a "HI" message, which initiates the conversation and returns a LOW and HIGH value for the guessing game to start its bounds at.

After doing type checking for the response using the JSON package, the client begins to guess using a binary search approach. If a message is ever corrupted or incorrect, I have implemented a resend feature using the 'WRY' message.

After finding the number, the client sends back a "BYE" message, which my client then handles as printing off the flag which is returned.