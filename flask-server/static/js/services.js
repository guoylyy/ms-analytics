'use strict';

/* Services */
var lastMonthSize = 10;
var MyAppServices = angular.module('MyAppServices', []);

MyAppServices.service('DataService',['$http',function($http){
	var that = this;
	this.all_data = {};
	this.all_types = [];

	this.loadData = function(callback){

		$http.get("http://localhost:5000/predict_data")
		.success(function(data){
			//alert(data);
			var parse_rcs = parseData(data);
			that.all_data = parse_rcs[0];
			that.all_types = parse_rcs[1]; //store all of type in system
			if(data.length>0){
				that.end_month = data[0].endMonth;
				that.start_month = data[0].startMonth;
			}
			that.month_list = getMonths(data);
			callback();
		})
		.error(function(data, status) {
         	alert('Error Happen!');
     	});	
	}


	this.getLastestMonthList = function(){
		if(that.month_list.length > lastMonthSize){
			//Convert Month to Jan-2013 type
			var list = that.month_list.slice(0, that.month_list.length-1);
			return list.slice(list.length - lastMonthSize);
		}else{
			return that.month_list;
		}
	}

	this.getCurrentData = function(date_type, date_month, dt_type){
		var values = this.all_data[date_type];
		var rc = [];
		if(dt_type == 'last_month'){
			date_month = getLastMonth(date_month);
		}else if (dt_type == 'last_year'){
			date_month = getLastYearMonth(date_month);
		}else if (dt_type == 'last_quarter'){
			date_month = getLastQuarter(date_month);
		}
		for(var i=0;i<values.length;i++){
			if(values[i].month == date_month.toString()){
				var val = values[i];
				rc = [val['me-1'],val['me'],val['me+1']];
				break;
			}
		}
		return rc;
	}

	this.getHistoryData = function(data_type,me_type){
		var predict_datas = this.all_data[data_type+"_predict"].slice(1,this.all_data[data_type+"_predict"].length);
		var real_list = compositeList(this.all_data[data_type+"_real"],me_type);
		var predict_list = compositeList(predict_datas,me_type);

		return [predict_list.reverse(),real_list.reverse()];
	}
}]);

function convertDate(dtStr){
	var UTCMonth = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	var ym = dtStr.split("-");
	return UTCMonth[Number(ym[1])-1] + ' ' + ym[0];
}

function getLastMonth(dtStr){
	var ym = dtStr.split("-");
	if(Number(ym[1])==1){
		return Number(ym[0])-1 + '-12';
	}else{
		var m = Number(ym[1])-1;
		return joinYearMonth(ym[0], m);
	}
}

function getLastQuarter(dtStr){
	var ym = dtStr.split("-");
	var year = Number(ym[0]);
	var month = Number(ym[1]);
	if(month > 3){
		month = month - 3;
	}else{
		month = (month - 3) + 12;
		year = year - 1;
	}
	return joinYearMonth(year, month);
}

function joinYearMonth(year, month){
	if(month < 10){
		return year + '-0' + (month-1);
	}else{
		return year + '-' + (month-1);
	}
}

function getLastYearMonth(dtStr){
	var ym = dtStr.split("-");
	return (Number(ym[0])-1) + '-' + ym[1];
}



function getMonths(all_datas){
	var month_list = [];
	if(all_datas.length>0){
		var smaple = all_datas[0].values;
		for(var i=0;i<smaple.length;i++){
			var dict = smaple[i];
			month_list.push(dict.month);
		}	
		month_list.sort();
	}
	return month_list;
}


function compositeList(dicts,me_type){
	var data_list = [];
	var limit = dicts.length;
	if(dicts.length > lastMonthSize){
		limit = lastMonthSize;
	}
	for(var i = 0;i<limit;i++){
		var dict = dicts[i];
		data_list.push(Number(dict[me_type].toFixed(0)));
	}
	return data_list;
}


function parseData(data_obj){
	var rc_data = {};
	var pre_types = [];
	for(var i=0;i<data_obj.length;i++){
		var data_type = data_obj[i].type;
		var pre_type = getIsPredict(data_obj[i].isPredict);
		rc_data[data_type+"_"+pre_type] = data_obj[i].values;
		pre_types.push(data_type+"_"+pre_type);
	}
	return [rc_data,pre_types];
}

function getIsPredict(bool){
	return bool?"predict":"real";
}
