'use strict';

var services = angular.module('services', ['ngResource']);

services.factory('Room', ['$resource',
    function($resource){
		return $resource('room', {}, {
	    	create: {method: 'POST'}
			enter: {method: 'GET'}
	    });
    }
]);