var BASE_URL = "http://localhost:8001/";
// var BASE_URL = "http://lasertag.byu.edu/";

var module1 = angular.module('lasertag', ['lasertag.directives']);

module1.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});

module1.controller('newGameCtrl', function($scope, $http) {
  $scope.game = {
  	mode: null,
  	teams: [],
  	players: [],
  	time_limit: null,
  	score_limit: null
  };
  $scope.player = {
  	username: "",
  	team: "",
  	gun: null
  };

  $http.get(BASE_URL + "guns")
  	.success(function(guns) {
	  	$scope.guns = guns;
	});

  $scope.addTeam = function() {
  	$scope.game.teams.push(angular.copy($scope.teamName));
  	$scope.teamName = "";
  }

  $scope.addPlayer = function() {
  	$scope.game.players.push(angular.copy($scope.player));
  	$scope.player.username = "";
  }

  $scope.startGame = function() {
  	if ($scope.game.mode !== "TEAMS") {
  		$scope.game.teams = null;
  	}
  	$http.post(BASE_URL + "start", $scope.game)
  		.success(function(response) {
  			console.log(response);
  			alert("Game Started");
  	});
  }

});

var module2 = angular.module('lasertag.directives', []);

module2.directive('goto', function () {
 		return {
 			restrict: 'A',
  		link: function (scope, elem, attrs) {
  			elem.bind("click", function() {
  				console.log(attrs);
  				window.location = BASE_URL + attrs["goto"];
  			});
  		}
    }
});
