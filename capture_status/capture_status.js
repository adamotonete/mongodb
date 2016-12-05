
var user = null;
var pass = null;

conn = new Mongo()
db = conn.getDB('admin')

if (user != null) {
   print('running auth..')
   db.auth(user,pass)
}



printjson(new Date())
printjson(db.currentOp())
printjson(db.serverStatus())

print('-----------------------------------------------------------------')
