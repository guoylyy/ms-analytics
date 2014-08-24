'use strict';

/* Filters */

angular.module('myApp.filters', []).filter('month_cut', function (){
	return function(input){
		return input.substr(2, input.length);
	};
});
