'use strict';

app.controller("CrowdeeRoomCtrl", function ($scope, $location, Channel, Room) {
	$scope.url_query = $location.search();
	$scope.room_id = $scope.url_query.room_id;
	
	$scope.user_id = null;
	$scope.user_weight = null;
	$scope.user_direction = "Nothing";
	$scope.aggregate_direction = "Nothing";
	$scope.room_key = null;
	$scope.crowd = {};
    
    $scope.onOpened = function()
    {
        Channel.send({command: "opened", room_id: $scope.room_id});
    };
    
    $scope.onMessage = function(crowdee)
    {
        //If it's a delete message...
        alert('check');
        if("delete" in crowdee)
        {
            //Delete the crowdee from the crowd.
            delete $scope.crowd[crowdee.user_id];
            return;
        }
        //Update the crowd with the crowdee information.
        $scope.crowd[crowdee.user_id] = {"name": crowdee.name, "direction": crowdee.direction, "weight": crowdee.weight};
        //alert(direction);
        //updateRoom();
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
			Channel.open($scope.channel_token, $scope.onOpened, $scope.onMessage);
	    }
    );
	
	/*Room.crowd({}, function(crowd)
	    {
			//Set the crowd.
			angular.forEach(crowd, function(crowdee, crowdee_id){
			    $scope.crowd[crowdee_id] = {"name": crowdee.name, "weight": $crowdee.weight, "direction": $crowdee.direction};
			});
	    }
    );*/
	
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
	
});
