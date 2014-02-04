var module1 = angular.module('lasertag.controllers', []);

module1.controller('homeCtrl', function($scope, $http, $timeout, API) {
  $scope.ready = false;
  $scope.show = "review";

  // Setup basic player object
  $scope.player = {
    username: "",
    team: "",
    gun: null
  };

  var val = [1,2,3,4].concat([1,2,3,4]);
  console.log(val);

  // Setup game mode choices
  $scope.modes = [
    { display: "Free for all", value: "FREE" },
    { display: "Teams", value: "TEAMS" },
    { display: "Juggernaut", value: "JUGGERNAUT" },
    { display: "Capture the Flag", value: "FLAG" }
  ]

  // Setup basic game object
  function resetGame() {
     $scope.newGame = {
      mode: null,
      teams: [],
      players: [],
      time_limit: null,
      score_limit: null
    };
  }
  resetGame();

  // Get mode display text based on value
  $scope.modeDisplayByVal = function(val) {
    for (var i = 0; i < $scope.modes.length; i++) {
      if ($scope.modes[i].value == val) return $scope.modes[i].display;
    }
  }

  // Long polling for near-real-time data
  function sync() {
    // Get up-to-moment game data
    API.get("games").then(function(data) {
      $scope.games = data.games;
      $scope.ready = true;
    });

    // Get list of available guns
    API.get("guns").then(function(guns) {
      $scope.guns = guns;
    });

    // $timeout(sync, 3000);
  };

  sync();

  // Display selected game
  $scope.review = function(game) {
    if ($scope.reviewGame == null || $scope.reviewGame.id != game) {
      $scope.reviewGame = game;
    }
  };

  // Add team name to newGame data
  $scope.addTeam = function() {
    $scope.newGame.teams.push(angular.copy($scope.teamName));
    $scope.teamName = "";
  };

  $scope.addPlayer = function() {
    if ($scope.guns.length ==  $scope.newGame.players.length) {
      alert("Not enough guns for that many players.");
    } else {
      $scope.newGame.players.push(angular.copy($scope.player));
      $scope.player.username = "";
    }
    console.log($scope.newGame);
  };

  // Post then reset game data
  $scope.startGame = function() {
    $http.post(BASE_URL + "start",  $scope.newGame)
      .success(function(response) {
        $scope.show = "join";
    });
    resetGame();
  };

});

var module2 = angular.module('lasertag.directives', []);