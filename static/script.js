function coolDown() {
	var coolDown = 1;
	var coolDownInterval = setInterval(function () {
		if (coolDown > 0) {
			coolDown--;
			document.getElementById("coolDown").innerHTML = coolDown;	
		} else {
			clearInterval(coolDownInterval);
			document.getElementById("disable").disabled = false;		
		}
	}, 1000);
	
}

function disableButton() {
	document.getElementById("disable").disabled = true;
	coolDown();
}

function run() {
	disableButton();
	window.location.href = "/run"
}
