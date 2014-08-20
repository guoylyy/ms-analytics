import xlrd



def main():
	data = xlrd.open_workbook('2013da.xlsx')
	sheets = data.sheets()
	for sheet in sheets: 
		print sheet.name #get name
		#print sheet.col_values(0)
		#print sheet.col_values(1)
		#print sheet.col_values(2)
		dates = sheet.col_values(0)
		mes = sheet.col_values(1)
		memos = sheet.col_values(2)
		transactions = sheet.col_values(3)
		l = [dates[i+1] for i in range(0, len(dates)-1)]
		print l

if __name__ == '__main__':
	main()
	pass