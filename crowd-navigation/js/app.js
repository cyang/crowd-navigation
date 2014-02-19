'use strict';

var app = angular.module('crowdnavigation', ['services'])

app.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
});
