'use strict';
var DEBUG = false;

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
  $routeProvider.when('/track', {templateUrl: 'static/partials/partial3.html', controller: 'TrackCtrl'});
  $routeProvider.otherwise({redirectTo: '/main'});
}]);
