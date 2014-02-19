'use strict';

var app = angular.module('crowdnavigation', ['services']).config(function($locationProvider) {
    $locationProvider.html5Mode(true);
});
