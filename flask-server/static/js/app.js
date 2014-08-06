'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', [
  'ngRoute',
  'myApp.filters',
  'MyAppServices',
  'myApp.directives',
  'myApp.controllers'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/main', {templateUrl: 'static/partials/partial1.html', controller: 'MainPageController'});
  $routeProvider.when('/history', {templateUrl: 'static/partials/partial2.html', controller: 'HistroyCtrl'});
  $routeProvider.otherwise({redirectTo: '/main'});
}]);
