'use strict';

var services = angular.module('services', ['ngResource']);

services.factory('Room', ['$resource',
    function($resource)
    {
		return $resource('/room-resource', {}, {
	    	create: {method: 'POST'},
			enter: {method: 'PUT', params:{room_id: '@room_id'}},
	    	query: {method: 'GET', params:{query: 'true'}, isArray:true}
	    });
    }
]);

services.factory('Channel', ['$resource',
	function($resource)
	{
		var Channel = $resource('/channel/:command', {},
				{
					send: {method: 'POST', params:{command: '@command', room_id: '@room_id', direction: '@direction'}},
				}
		);
		/*Channel.open = function(token, onOpened, onMessage)
		{
			var channel = new goog.appengine.Channel(token);
	        var handler = {
	            'onopen': onOpened,
	            'onmessage': onMessage,
	            'onerror': function(){},
	            'onclose': function(){}
	        };
	        var socket = channel.open(handler);
	        socket.onopen = onOpened;
	        socket.onmessage = onMessage;
		};*/
		return Channel;
	}
]);

//OpenTok service
services.factory('OpenTok', function()
{
    function sessionConnectedHandler(event)
    {
        subscribeToStreams(event.streams);
    }
    
    function subscribeToStreams(streams)
    {
        for (var i = 0; i < streams.length; i++)
        {
            var stream = streams[i];
            if (stream.connection.connectionId != session.connection.connectionId)
            {
                session.subscribe(stream, "tokbox_subscription", {width:$('#tokbox_container').width(), height:$('#tokbox_container').height()});
            }
        }
    }
    
    function streamCreatedHandler(event)
    {
        subscribeToStreams(event.streams);
    }
    
    return {
        subscribe: function(api_key, session_id, token)
        {
            var session = TB.initSession(sessionId);
            
            session.connect(apiKey, token);
            session.addEventListener("sessionConnected", 
                                     sessionConnectedHandler);
            
            session.addEventListener("streamCreated", 
                                     streamCreatedHandler);
        }
    }
});