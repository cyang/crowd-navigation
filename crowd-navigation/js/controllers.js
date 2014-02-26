'use strict';

app.controller("CrowdeeRoomCtrl", function ($scope, $window, $location, Channel, Room) {
	$scope.url_query = $location.search();
	$scope.room_id = $scope.url_query.room_id;
	
	$scope.user_id = null;
	$scope.user_weight = null;
	$scope.user_direction = "Nothing";
	$scope.aggregate_direction = "Nothing";
	$scope.room_key = null;
	$scope.crowd = {};
	$scope.test = 0;
    
	$scope.openChannel = function()
	{
        var channel = new goog.appengine.Channel($scope.channel_token);
        var handler = {
            'onopen': $scope.onOpened,
            'onmessage': $scope.onMessage,
            'onerror': function(){},
            'onclose': function(){}
        };
        var socket = channel.open(handler);
        socket.onopen = $scope.onOpened;
        socket.onmessage = $scope.onMessage;
	};
	
    $scope.onOpened = function()
    {
        Channel.send({command: "opened", room_id: $scope.room_id});
    };
    
    $scope.onMessage = function(message)
    {
        var crowdee = angular.fromJson(message.data);
        //If it's a delete message...
        if(crowdee.hasOwnProperty("delete"))
        {
            //Delete the crowdee from the crowd.
            delete $scope.crowd[crowdee.user_id];
            return;
        }
        //Update the crowd with the crowdee information.
        $scope.crowd[crowdee.user_id] = {"name": crowdee.name, "direction": crowdee.direction, "weight": crowdee.weight};
        $scope.$apply(); //TODO - Replace with directive.
        $scope.aggregateDirections();
    };
	
	Room.enter({room_id: $scope.room_id}, function(crowdee_data)
	    {
			//Extract the data to scope variables.
			$scope.room_key = crowdee_data.room_key;
			$scope.user_id = crowdee_data.user_id;
			$scope.user_name = crowdee_data.user_name;
			$scope.user_weight = crowdee_data.user_weight;
			$scope.tokbox_api_key = crowdee_data.tokbox_api_key;
			$scope.tokbox_session_id = crowdee_data.tokbox_session_id;
			$scope.tokbox_token = crowdee_data.tokbox_token;
			$scope.channel_token = crowdee_data.channel_token;
			
			//Add the user to the crowd.
			$scope.crowd[$scope.user_id] = {"name": $scope.user_name, "weight": $scope.user_weight, "direction": $scope.user_direction};
			
			//Open the channel.
			$scope.openChannel();
	    }
    );
	
	//Aggregates the directions of the crowd for the user's display.
	$scope.aggregateDirections = function()
	{
	    var direction_list = {}
	    angular.forEach($scope.crowd, function(crowdee)
	    {
            if(direction_list.hasOwnProperty(crowdee.direction))
            {
                direction_list[crowdee.direction] += crowdee.weight; 
            }
            else
            {
                direction_list[crowdee.direction] = crowdee.weight;
            }
        });
	    var max_value = 0;
	    var max_direction = "Stop";
	    angular.forEach(direction_list, function(value, direction)
        {
            if(value > max_value && direction != "Nothing")
            {
                max_value = value;
                max_direction = direction;
            }
        });
	    $scope.aggregate_direction = max_direction;
	    $scope.$apply(); //TODO - Change function so $apply is unnecessary.
	}
	
	$scope.keyDown = function($event)
    {
        //Check if the key was an arrow key.
        if($event.keyCode == '37')
        {
            //Left arrow.
        	$scope.user_direction = "Left";
        }
        else if($event.keyCode == '38')
        {
            //Up arrow.
        	$scope.user_direction = "Forward";
        }
        else if($event.keyCode == '39')
        {
            //Right arrow.
        	$scope.user_direction = "Right";
        }
        else if($event.keyCode == '40')
        {
            //Down arrow.
        	$scope.user_direction = "Stop";
        }
        $scope.crowd[$scope.user_id]['direction'] = $scope.user_direction;
        //updateRoom();
        Channel.send({command: 'move', room_id: $scope.room_id, direction: $scope.user_direction});
    };
});


app.controller("HostRoomCtrl", function ($scope) {
    $scope.user_id = null;
    $scope.aggregate_direction = "Nothing";
    $scope.room_key = null;
    $scope.crowd = {};
    
    $scope.openChannel = function()
    {
        var channel = new goog.appengine.Channel($scope.channel_token);
        var handler = {
            'onopen': $scope.onOpened,
            'onmessage': $scope.onMessage,
            'onerror': function(){},
            'onclose': function(){}
        };
        var socket = channel.open(handler);
        socket.onopen = $scope.onOpened;
        socket.onmessage = $scope.onMessage;
    };
    
    $scope.onOpened = function()
    {
        Channel.send({command: "opened", room_id: $scope.room_id});
    };
    
    $scope.onMessage = function(message)
    {
        var crowdee = angular.fromJson(message.data);
        //If it's a delete message...
        if(crowdee.hasOwnProperty("delete"))
        {
            //Delete the crowdee from the crowd.
            delete $scope.crowd[crowdee.user_id];
            return;
        }
        //Update the crowd with the crowdee information.
        $scope.crowd[crowdee.user_id] = {"name": crowdee.name, "direction": crowdee.direction, "weight": crowdee.weight};
        $scope.$apply(); //TODO - Replace with directive.
        $scope.aggregateDirections();
    };
    
    Room.create({room_id: $scope.room_id}, function(host_data)
        {
            //Extract the data to scope variables.
            $scope.room_key = host_data.room_key;
            $scope.user_id = host_data.user_id;
            $scope.user_name = host_data.user_name;
            $scope.tokbox_api_key = host_data.tokbox_api_key;
            $scope.tokbox_session_id = host_data.tokbox_session_id;
            $scope.tokbox_token = host_data.tokbox_token;
            $scope.channel_token = host_data.channel_token;
                        
            //Open the channel.
            $scope.openChannel();
        }
    );
    
    //Aggregates the directions of the crowd for the user's display.
    $scope.aggregateDirections = function()
    {
        var direction_list = {}
        angular.forEach($scope.crowd, function(crowdee)
        {
            if(direction_list.hasOwnProperty(crowdee.direction))
            {
                direction_list[crowdee.direction] += crowdee.weight; 
            }
            else
            {
                direction_list[crowdee.direction] = crowdee.weight;
            }
        });
        var max_value = 0;
        var max_direction = "Stop";
        angular.forEach(direction_list, function(value, direction)
        {
            if(value > max_value && direction != "Nothing")
            {
                max_value = value;
                max_direction = direction;
            }
        });
        $scope.aggregate_direction = max_direction;
        $scope.$apply(); //TODO - Change function so $apply is unnecessary.
    }
});


app.controller("HomePageCtrl", function ($scope, Room) {
    $scope.room_list = Room.query();
});