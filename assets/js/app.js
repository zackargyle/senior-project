var BASE_URL = "http://localhost:8001/";

var game = {
	mode: null,
	state: null,
	time_limit: null,
	score_limit: null
}

var goto = function(endpoint) {
	window.location = BASE_URL + endpoint;
}

var createGame = function(mode) {
	game.mode = mode;
	game.state = "NEW";
	game.time_limit = time_limit;
	game.score_limit = score_limit;
	// post game
	// callback game = response
}
