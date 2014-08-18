import xlrd



def main():
	data = xlrd.open_workbook('IOC.xlsx')
	sheets = data.sheets()
	for sheet in sheets: 
		print sheet.name #get name
		print sheet.col_values(1)

if __name__ == '__main__':
	main()
	pass