/* this scripts generates random data */
use test

TOTAL=1000000

function generateString(slimit) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < slimit; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}


function generateAge() {
	return Math.floor((Math.random() * 95) + 1);;
}

function generateDate(start, end, startHour, endHour) {
  var date = new Date(+start + Math.random() * (end - start));
  var hour = startHour + Math.random() * (endHour - startHour) | 0;
  date.setHours(hour);
  return date;
}

function generateTFalse() {
	return ((Math.floor((Math.random() * 2) + 1) % 2) == 0);
}



for (var x=1;x<TOTAL;x++) {
	name = generateString(5)
	lastname = generateString(15)
	age = generateAge()
	birthdate = generateDate(1985,2012,0,23) 
	company = generateString(10)
	self_bio = generateString(100)
	receive_sms = generateTFalse()
	likes = []
	likes = [generateString(3), generateString(3), generateString(3)]
	db.collectiontest.save({'name' : name, 'lastname' : lastname, 'birthdate' : birthdate, 'company' : company , 
	  'self_bio' :self_bio, 'receive_sms': receive_sms, 'likes' : likes  })

}



