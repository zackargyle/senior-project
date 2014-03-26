var module2 = angular.module('lasertag.services', [])

.service("Sync", function($rootScope, $http) {
    var interval = null, pause = false;
        game = null;

    function sync(id) {
        if (!pause) {
            $http.get("games/" + id).then(function(response) {
                data = response.data;
                $rootScope.$broadcast('event:sync');
            });
        }
    };

    this.start = function(id, period) {
        sync(id);
        interval = window.setInterval(function() {
            sync(id);
        }, period);
    }

    this.stop = function() {
        clearInterval(interval);
    }

    this.getData = function() {
        return data;
    }

});