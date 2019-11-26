Header Structure (32 Bytes Total)

---------------------------------------------
| Sender (4 Bytes) | Message Type (4 Bytes) |
---------------------------------------------
|	Message/Payload (24 Bytes)	    |
---------------------------------------------


Sender:
Client = 10
Load Balancer = 20
Replica Server = 30

	      ICMP (Ping)		(1)	
Replica Server <------- Load Balancer<=======>Client
     |    ^				(2)    |    ^
     |    \			 	      / (3) |
     |     ----------------------------------      /
      \                                          /
        ----------------------------------------
	             (4) & (5)

Order of communication:
(1) - Sender = 10 (Client) to Load Balancer, Type = 05, Message = "Server Request"
(2) - Sender = 20 (Load Balancer) to Client, Type = 10, Message = <Server IP, PORT>
(3) - Sender = 10 (Client) to Replica Server, Type = 15, Message = "Content Request"
(4) - Sender = 30 (Replica Server) to Client, Type = 20, Message = <Payload Size>
(5) - Sender = 30 (Replica Server) to Client, Type = 21, Message = <Payload>

Known to work:
-Most syntax errors are fixed
-Load balancer properly pings each server and returns the loss and delay
values for each server
-The pipe from the preference_checker() subprocess properly communicates to the
main process 
-Client can successfully obtain the full page from the replica server (!!!)
To-do:
-Logging/writing things to files
