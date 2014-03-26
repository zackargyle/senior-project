var module1 = angular.module('lasertag.controllers', []);

module1.controller('homeCtrl', function($rootScope, $scope, $http, Sync) {
  $scope.ready = false;
  $scope.show = "games"; // games, review, stats
  $scope.games = [];

  // Grab games
  function getGames(page) {
    $http.get("games?limitTo=10&startAt=" + page * 10)
      .then(function(response) {
        $scope.games = response.data;
        if (!$scope.ready) $scope.ready = true;
      });
  }
  getGames(0);

  // Listen for Syncing
  $rootScope.$on('event:sync', function() {
    $scope.reviewGame = Sync.getData();
  });

  // ng-show router
  $scope.goto = function(show, data) {
    if (show == 'review') {
      if (data) 
        $scope.reviewGame = data;
      if ($scope.reviewGame.state == "PLAYING") 
        Sync.start($scope.reviewGame.id, 1500);
      $scope.show = show;
    }
    else if (show === "stats") {
      Sync.stop();
      $http.get("stats/" + data.username).then(function(response) {
        $scope.playerStats = response.data;
        $scope.show = show;
      });
    }
    else {
      Sync.stop();
      $scope.show = show;
    }
  }

});