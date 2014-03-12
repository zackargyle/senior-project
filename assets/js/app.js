'use strict';

//var BASE_URL = "http://localhost:8001/";
var BASE_URL = "http://lasertag.byu.edu:8001/";

var module = angular.module('lasertag', ['lasertag.controllers','lasertag.directives']);

module.factory('API', function($http) {
  return {
    get: function(endpoint) {
      return $http.get(BASE_URL + endpoint);
    }
  }
});

module.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});