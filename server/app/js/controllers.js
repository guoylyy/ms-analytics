'use strict';

/* Controllers */
var MyAppController = angular.module('myApp.controllers', []);
  

MyAppController.controller('MainPageController', ['$scope','DataService',function($scope,DataService) {
	var _scope = $scope;
	var categories = ['ME-1','ME','ME+1'];
	_scope.current_month = new Date().format("yyyy-MM");
	_scope.current_data_src = "memos";
	_scope.current_tab = "recent";

	DataService.loadData(function(){
        /*
            Initial Current Chart
        */
		_scope.start_month = DataService.start_month;
		_scope.end_month = DataService.end_month;
        if(_scope.current_month.toString() == _scope.end_month){
		    _scope.need_update = false;
        }else{
            _scope.need_update = true;
        }
		_scope.recent_data =  DataService.getCurrentData(_scope.current_data_src+"_predict",_scope.end_month);
		_scope.recent_chart = initialResentChart(_scope.recent_data,categories,_scope.end_month);
	});

	_scope.compare = function(){
        /*
            Compare the current prediction value with actual value 
        */
		var input_data = getInputData();
		if(input_data!=null){
			//start change current chart
			_scope.recent_chart.series[0].show();
			var apes = calApes(_scope.recent_data,input_data);
			_scope.recent_chart.series[1].setData(input_data);
			_scope.recent_chart.series[2].setData(apes);
		}
	}
	_scope.actual = function(){
		/*
            clear or hidden the data of input
        */
		if(_scope.recent_chart.series[0].visible){
			_scope.recent_chart.series[0].hide();
		}else{
			_scope.recent_chart.series[0].show();
		}
	}
	_scope.change_src = function(target){
		_scope.recent_data =  DataService.getCurrentData(_scope.current_data_src+'_real',_scope.end_month);
        _scope.recent_chart.series[0].setData(_scope.recent_data);
		_scope.recent_chart.series[2].setData([0,0,0]);
		_scope.recent_chart.series[1].hide();
		_scope.recent_chart.series[2].hide();
        var title = 'Month End Projection of ' + _scope.current_data_src;
        _scope.recent_chart.setTitle({text: title});        
	}
}]);
  
MyAppController.controller('HistroyCtrl', ['$scope','DataService', function($scope,DataService) {
	var _scope = $scope;
	var categories = ['ME-1','ME','ME+1'];
	_scope.current_month = new Date().format("yyyy-MM");
	_scope.current_data_src = "memos";
	_scope.current_data_me = "mem1";

	_scope.current_tab = "recent";
	DataService.loadData(function(){
		_scope.start_month = DataService.start_month;
		_scope.end_month = DataService.end_month;
		//Initial Current Chart
		var rc = DataService.getHistoryData(_scope.current_data_src,mePickerType(_scope.current_data_me));

		if(rc.length>0){
			var apes = calApes(rc[0],rc[1]);
			rc.push(apes);
			_scope.history_chart = initialHistoryChart(rc,DataService.month_list,_scope.start_month,_scope.end_month);

		}else{
			alert("Fail to load Data!");
		}
		//
	});

	_scope.change_options = function(){
		var rc = DataService.getHistoryData(_scope.current_data_src,mePickerType(_scope.current_data_me));
		var apes = calApes(rc[0],rc[1]);
		if(rc.length>0){
			rc.push(apes);
		}else{
			alert("Fail to load Data!");
		}
		_scope.history_chart.series[0].setData(rc[0]);
		_scope.history_chart.series[1].setData(rc[1]);
		_scope.history_chart.series[2].setData(rc[2]);
        var title = 'History Projection of ' + _scope.current_data_src + ' ('+ mePickerType(_scope.current_data_me) +')';
        _scope.history_chart.setTitle({text: title});      
	}

}]);


/*
 User defined function
*/

function calApes(predicts,reals){
	var rcs = [];
	for(var i=0;i<predicts.length;i++){
		var ape = Math.abs(predicts[i]-reals[i])/reals[i];
		rcs.push(ape*100);
	}
	return rcs;
}


function mePickerType(src){
	switch(src){
		case "mem1":
			return "me-1";
			break;
		case "me":
			return "me";
			break;
		case "mep1":
			return "me+1";
			break;
		default:
			return "";
			break;
	}	
}

function initialHistoryChart(data,categories,start_month,end_month){
	var sub_title = "From "+ start_month + " to "+end_month;
	var chart = new Highcharts.Chart({
            title: {
                text: 'History Projection of Memos',
                x: -20 //center
            },
            chart:{
            	renderTo: "historyChart"
            },
            subtitle: {
                text: sub_title,
                x: -20
            },
            xAxis: {
                categories: categories
            },
            yAxis: [{
                title: {
                    text: ''
                },
                min:0,
                plotLines: [{
                    value: 0,
                    color: '#808080'
                }]
                },
                {
                title: {
                    text: '%'
                },
                max:100,
                min:0,
                plotLines: [{
                    value: 0,
                    color: '#808080'
                }],
                opposite: true  
                }
            ],
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [
           {
                name: 'Projection',
                data: data[0]
            },{
                name: 'Actual',
                data: data[1]
            }, {
                name: 'APE',
                yAxis: 1,
                type: 'column',
                data: data[2]
            }
            ]
        });
    return chart;
}


function initialResentChart(data,categories,end_month){
	var chart = new Highcharts.Chart({
            title: {
                text: 'Month End Projection of Memos',
                x: -20 //center
            },
            chart:{
            	renderTo: "recentChart"
            },
            subtitle: {
                text: end_month,
                x: -20
            },
            xAxis: {
                categories: categories
            },
            yAxis: [{
                title: {
                    text: ''
                },
                min:0,
                plotLines: [{
                    value: 0,
                    color: '#808080'
                }]
                },
                {
                title: {
                    text: '%'
                },
                max:100,
                min:0,
                plotLines: [{
                    value: 0,
                    color: '#808080'
                }],
                opposite: true  
                }
            ],
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [     
             {
                name: 'Projection',
                data: data
            },{
                name: 'Actual',
                data: ["","",""]
            }, {
                name: 'APE',
                yAxis: 1,
                type: 'column',
                data: [0, 0, 0]
            }
            ]
        });
    return chart;
}


function getInputData(){
	var mem1 = $("#mem1").val();
	var me = $("#me").val();
	var mep1 = $("#mep1").val();
	if(IsNum(mem1)&&IsNum(me)&&IsNum(mep1)){
		return [Number(mem1),Number(me),Number(mep1)];
	}else{
		alert("Please enter number");
		return null;
	}
}

function IsNum(num){
  var reNum=/^\d*$/;
  if(num.length==0){
  	return false;
  }else{
  	return(reNum.test(num));
  }
}


Date.prototype.format =function(format)
{
    var o = {
    "M+" : this.getMonth()+1, //month
    "d+" : this.getDate(), //day
    "h+" : this.getHours(), //hour
    "m+" : this.getMinutes(), //minute
    "s+" : this.getSeconds(), //second
    "q+" : Math.floor((this.getMonth()+3)/3), //quarter
    "S" : this.getMilliseconds() //millisecond
    }
    if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
    (this.getFullYear()+"").substr(4- RegExp.$1.length));
    for(var k in o)if(new RegExp("("+ k +")").test(format))
    format = format.replace(RegExp.$1,
    RegExp.$1.length==1? o[k] :
    ("00"+ o[k]).substr((""+ o[k]).length));
    return format;
}