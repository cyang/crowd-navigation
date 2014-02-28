'use strict';

var app = angular.module('crowdnavigation', ['services', 'ngClipboard'])

app.config(function($locationProvider)
{
    $locationProvider.html5Mode(true);
});

app.config(['ngClipProvider', function(ngClipProvider)
{
    ngClipProvider.setPath("/js/ZeroClipboard.swf");
}]);