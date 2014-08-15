'use strict';

/* Controllers */
var MyAppController = angular.module('myApp.controllers', []);
var me_types = ['mem1','me','mep1'];
var view_tags = {'memos':'Memos',
                 'transaction':'Transaction',
                 'mem1':'ME-1',
                 'me': 'ME',
                 'mep1':'ME+1'
                };

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
        var title = 'Month End Projection Of ' + view_tags[_scope.current_data_src];
		_scope.recent_data =  DataService.getCurrentData(_scope.current_data_src+"_predict",_scope.end_month);
        _scope.recent_chart = initialResentChart(_scope.recent_data,categories,_scope.end_month, title);
        _scope.real_data =  DataService.getCurrentData(_scope.current_data_src+"_real",_scope.end_month);  
        _scope.apes = calApes(_scope.recent_data,_scope.real_data);   

        _scope.lastM = DataService.getCurrentData(_scope.current_data_src+"_predict",_scope.end_month,'last_month');
        _scope.recent_chart.series[1].setData(_scope.lastM);

        _scope.lastY = DataService.getCurrentData(_scope.current_data_src+"_predict",_scope.end_month,'last_year');
        _scope.recent_chart.series[0].setData(_scope.lastY);        

	});

	_scope.change_options = function(target){
		_scope.recent_data =  DataService.getCurrentData(_scope.current_data_src+'_predict',_scope.end_month);
        _scope.real_data =  DataService.getCurrentData(_scope.current_data_src+"_real",_scope.end_month);  
        _scope.apes = calApes(_scope.recent_data, _scope.real_data);

        _scope.recent_chart.series[2].setData(_scope.recent_data);

        _scope.lastM = DataService.getCurrentData(_scope.current_data_src+"_predict",_scope.end_month,'last_month');
        _scope.recent_chart.series[1].setData(_scope.lastM);

        _scope.lastY = DataService.getCurrentData(_scope.current_data_src+"_predict",_scope.end_month,'last_year');
        _scope.recent_chart.series[0].setData(_scope.lastY);   
        var title = 'Month End Projection Of ' + view_tags[_scope.current_data_src];
        _scope.recent_chart.setTitle({text: title});   
	}
}]);
  
/*
    History Controller
*/  
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
            var month_list = DataService.getLastestMonthList();
            var title = 'Historical Trend Of ' + view_tags[_scope.current_data_src] 
                    + ' ('+ view_tags[_scope.current_data_me]+')';
			_scope.history_chart = initialHistoryChart(rc, month_list, month_list[0],_scope.end_month,title);
            _scope.results = rc;
            _scope.months = month_list;
		}else{
			alert("Fail to load Data!");
		}
	});

	_scope.change_options = function(){
		var rc = DataService.getHistoryData(_scope.current_data_src,mePickerType(_scope.current_data_me));
		var apes = calApes(rc[0],rc[1]);
		if(rc.length>0){
			rc.push(apes);
		}else{
			alert("Fail to load Data!");
		}
        _scope.results = rc;
		_scope.history_chart.series[0].setData(rc[0]);
		_scope.history_chart.series[1].setData(rc[1]);
		_scope.history_chart.series[2].setData(rc[2]);
        var title = 'Historical Trend Of ' + view_tags[_scope.current_data_src] 
                    + ' ('+ view_tags[_scope.current_data_me]+')';
        _scope.history_chart.setTitle({text: title});      
	}

}]);

/*
    Prediction Track Controller
*/

MyAppController.controller('TrackCtrl', ['$scope','DataService', function($scope,DataService) {
    var _scope = $scope;
    var categories = ['ME-1','ME','ME+1'];
    _scope.current_month = new Date().format("yyyy-MM");
    _scope.current_data_src = "memos";

    _scope.current_tab = "recent";
    DataService.loadData(function(){
        _scope.start_month = DataService.start_month;
        _scope.end_month = DataService.end_month;
        var track_result = [];
        var ape_result = [];
        _scope.month_list = DataService.getLastestMonthList();

        for(var key in me_types){
            var rc = DataService.getHistoryData(_scope.current_data_src,mePickerType(me_types[key]));
            var apes = calApes(rc[0],rc[1]);
            rc.push(apes);
            ape_result.push(apes);
        }
        var title = 'Predict Track Of ' + view_tags[_scope.current_data_src];
        _scope.apes = ape_result;
        _scope.history_chart = initialTrackChart(ape_result, _scope.month_list, _scope.month_list[0],_scope.end_month,title);
    });

    _scope.change_options = function(){
        var ape_result = [];
        for(var key in me_types){
            var rc = DataService.getHistoryData(_scope.current_data_src,mePickerType(me_types[key]));
            var apes = calApes(rc[0],rc[1]);
            rc.push(apes);
            ape_result.push(apes);
        }
        _scope.apes = ape_result;
        _scope.history_chart.series[0].setData(ape_result[0]);
        _scope.history_chart.series[1].setData(ape_result[1]);
        _scope.history_chart.series[2].setData(ape_result[2]);
        var title = 'Predict Track Of ' + view_tags[_scope.current_data_src];
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
		rcs.push(Number((ape*100).toFixed(2)));
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

function initialHistoryChart(data, categories, start_month, end_month, title){
	var sub_title = "From "+ start_month + " to "+end_month;
	var chart = new Highcharts.Chart({
            title: {
                text: title,
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
                    text: 'APE%'
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


function initialResentChart(data,categories,end_month, title){
	var chart = new Highcharts.Chart({
            type : 'column',
            title: {
                text: title,
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
                    text: 'APE%'
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
             tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            series: [     
             {
                name: 'Last Year',
                data: [],
                type: 'column'
             },
             {
                name: 'Last Month',
                data: [],
                type: 'column'
             },{
                name: 'Projection',
                data: data,
                type: 'column'
             }
            ]
        });
    return chart;
}


function initialTrackChart(data,categories,start_month,end_month,title){
    var sub_title = "From "+ start_month + " to "+end_month;
    var chart = new Highcharts.Chart({
            title: {
                text: title,
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
            yAxis: [
                {
                title: {
                    text: 'APE%'
                },
                max:100,
                min:0,
                plotLines: [{
                    value: 0,
                    color: '#808080'
                }]
                }
            ],
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            series: [
           {
                name: 'ME-1',
                data: data[0]
            },{
                name: 'ME',
                data: data[1]
            }, {
                name: 'ME+1',
                data: data[2]
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