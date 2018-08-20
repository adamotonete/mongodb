clients = {"no_client_ip" : 0}
db.currentOp(true).inprog.forEach(function (c) {
         if ('client' in c) {

         	if (c["client"].split(':')[0] in clients)
         	{
         		clients[c["client"].split(':')[0]] = clients[c["client"].split(':')[0]] + 1
         	}
         	else
         	{
         		clients[c["client"].split(':')[0]] = 1	
         	}
         }
         else
         {
         	clients["no_client_ip"] = clients["no_client_ip"] + 1

         }
     })
printjson(clients)
