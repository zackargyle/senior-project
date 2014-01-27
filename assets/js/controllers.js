var module1 = angular.module('lasertag.controllers', []);

module1.controller('homeCtrl', function($scope, $http, $timeout, API) {
  $scope.ready = false;

  // Setup basic game object
  function resetGame() {
    $scope.show = "review";
    $scope.game = {
      mode: null,
      teams: [],
      players: [],
      time_limit: null,
      score_limit: null
    };
  }
  resetGame();

  // Setup basic player object
  $scope.player = {
    username: "",
    team: "",
    gun: null
  };

  $scope.modes = [
    { display: "Free for all", value: "FREE" },
    { display: "Teams", value: "TEAMS" },
    { display: "Juggernaut", value: "JUGGERNAUT" },
    { display: "Capture the Flag", value: "FLAG" }
  ]

  // Get mdoe display text based on value
  $scope.modeDisplayByVal = function(val) {
    for (var i = 0; i < $scope.modes.length; i++) {
      if ($scope.modes[i].value == val) return $scope.modes[i].display;
    }
  }

  // Long polling for near-real-time data
  function sync() {
    API.get("games").then(function(games) {
      $scope.games = games;
    });

    API.get("playerinstances").then(function(players) {
      $scope.players = players.sort(function(a, b) {
        return b.score - a.score;
      });
    });

    API.get("teams").then(function(teams) {
      $scope.teams = teams.sort(function(a, b) {
        return a.score - b.score;
      });
    });

    API.get("guns").then(function(guns) {
      $scope.guns = guns;
      $scope.ready = true;
    });

    $timeout(sync, 5000);
  };

  sync();

  // Display selected game
  $scope.review = function(game) {
    if ($scope.reviewGame == null || $scope.reviewGame.id != game) {
      $scope.reviewGame = game;
    }
  };

  $scope.addTeam = function() {
    $scope.game.teams.push(angular.copy($scope.teamName));
    $scope.teamName = "";
  };

  $scope.addPlayer = function() {
    if ($scope.guns.length == $scope.game.players.length) {
      alert("Not enough guns for that many players.");
    } else {
      $scope.game.players.push(angular.copy($scope.player));
      $scope.player.username = "";
    }
  };

  // Post then reset game data
  $scope.startGame = function() {
    $http.post(BASE_URL + "start", $scope.game)
      .success(function(response) {
        $scope.show = "join";
    });
    resetGame();
  };

});

var module2 = angular.module('lasertag.directives', []);