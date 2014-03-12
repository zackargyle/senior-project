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

  function updateReviewGame() {
    if ($scope.reviewGame) {
      angular.forEach($scope.games, function(game) {
        if ($scope.reviewGame.id === game.id) {
          $scope.reviewGame = game;
        }
      });
    }
  }

  // Long polling for near-real-time data
  function sync() {
    // Get up-to-moment game data
    API.get("games").then(function(response) {
      $scope.games = response.data;
      $scope.ready = true;
      updateReviewGame();
    });

    // Get list of available guns
    API.get("guns").then(function(guns) {
      $scope.guns = guns;
    });

    $timeout(sync, 2000);
  };

  sync();

  // Display selected game
  $scope.review = function(game) {
    if ($scope.reviewGame == null || $scope.reviewGame.id != game) {
      $scope.reviewGame = game;
    }
  };

  $scope.stats = function(player) {
    API.get("stats/" + player.username).then(function(response) {
      var data = response.data;
      console.log(data);
      $scope.playerStats = data;
      $scope.show = "stats";
    });
  }

});

var module2 = angular.module('lasertag.directives', []);