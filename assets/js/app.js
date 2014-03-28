'use strict';

//var BASE_URL = "http://localhost:8001/";
var BASE_URL = "http://lasertag.byu.edu:8001/";

var module = angular.module('lasertag', ['lasertag.controllers','lasertag.services']);

module.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});

module.run(function() {
	var content = document.getElementById('content-body'),
			width = content.offsetWidth;
	window.onresize = function() {
		if (window.innerWidth > 820)
			content.style.marginLeft = (window.innerWidth - width) / 2 + 'px';
		else
			content.style.marginLeft = -90 + 'px';
	}
	window.onresize();
});

module.filter('startFrom', function() {
  return function(input, start) {
    start = +start; //parse to int
    return input.slice(start);
  }
});