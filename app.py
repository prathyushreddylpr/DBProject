from flask import Flask, render_template, request;
from datetime import datetime
import pymysql
import sys
import random
app = Flask(__name__)

global username_final

class Database:
	def __init__(self):
		host = "localhost"
		user = "root"
		password = "Chintuus@1"
		db="PortfolioManager"
		self.con = pymysql.connect(host=host,user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
		self.cur = self.con.cursor()
	
	def get_investments(self):
		self.cur.execute("SELECT Name as InvestmentName, COUNT(*) as count FROM Investments i JOIN Transaction t ON i.InvestmentID = t.InvestmentID WHERE t.Date LIKE '%oct-22' AND t.Type = '1' GROUP BY Name ORDER BY count DESC LIMIT 15")
		result = self.cur.fetchall()
		return result
	def get_user_investments(self):
		self.cur.execute("SELECT InvestmentType, SUM(Transaction_Amount) as AmountInvested FROM Transaction T JOIN Investments I ON T.InvestmentID = I.InvestmentID WHERE T.UserName = 'CS1967' GROUP BY InvestmentType")
		result = self.cur.fetchall()

		return result


	def user_add(self,username,email,mobile,fname,lname,address,password,hint):
		self.cur.execute("INSERT INTO Users(UserName, Email, Mobile, First_Name, Last_Name, Address, Password, Hint) VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (str(username),str(email),str(mobile),str(fname),str(lname),str(address),str(password),str(hint)))
		self.con.commit()
		self.con.close()
		self.cur.close()
		return True

	def user_replace(self,username,email,mobile,fname,lname,address,password,hint):
		res = self.cur.execute("SELECT * FROM users WHERE UserName = \'%s\'" %(str(username_final)))
		if res == 0:
			return "ERROR"
		result = self.cur.fetchall()
		print("hi")
		print(email)
		
		result = result[0]
		print(result, file=sys.stdout)
		if(username==""):
			username = result['UserName']
		if(email==""):
			email = result['Email']
		if(mobile==""):
			mobile = result['Mobile']
		if(fname==""):
			fname = result['First_Name']
		if(lname==""):
			lname = result['Last_Name']
		if(password==""):
			password =result['Password']
		if(hint==""):
			hint = result['Hint']
		
		self.cur.execute("UPDATE users SET UserName =\'%s\' , Email = \'%s\' , Mobile = \'%s\' , First_Name = \'%s\' , Last_Name = \'%s\' , Address = \'%s\' , Password = \'%s\' , Hint = \'%s\' WHERE UserName = \'%s\'" % (str(username),str(email),str(mobile),str(fname),str(lname),str(address),str(password),str(hint),str(username_final)))		
		self.con.commit()
		self.con.close()
		self.cur.close()
		return True

	def authenticateUser(self, username, password):
		self.cur.execute("SELECT * FROM Users WHERE UserName = \'%s\' AND Password = \'%s\'" % (str(username), str(password)))
		result = self.cur.fetchall()
		if(len(result) == 0):
			return False
		username_final = str(username)
		return True
	
	def get_your_investments(self):
		global username_final
		self.cur.execute("SELECT InvestmentType, SUM(Transaction_Amount) as AmountInvested FROM Transaction T JOIN Investments I ON T.InvestmentID = I.InvestmentID WHERE T.UserName = \'%s\' GROUP BY InvestmentType" % (str(username_final)))
		print(str(username_final))
		result = self.cur.fetchall()
		if(len(result) == 0):
			return result
		return result
	def search_your_investments(self, querystring):
		self.cur.execute("SELECT InvestmentType, Name, UnitValue from investments where name like \'%s\' limit 1" % (str(querystring)))
		result = self.cur.fetchall()
		print(result, file = sys.stdout)
		if(len(result) == 0):
			return "NotFound"
		return result
	def delete(self, querystring):
		res = self.cur.execute("DELETE from investments where Name like \'%s\'" % (str(querystring)))
		self.con.commit()
		self.cur.close()
		self.con.close()
		return res
	
	def update_investments(self, name1, name2):
		res = self.cur.execute("UPDATE investments set name = \'%s\' where name = \'%s\'" % (str(name2), str(name1)))
		self.con.commit()
		self.cur.close()
		self.con.close()
		return res
	def insert_investments(self, investmendid, investmenttype,investmentdate,investmentname,unitvalue):
		print(investmendid)
		res = self.cur.execute("INSERT into investments values(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (str(investmendid), str(investmenttype),str(investmentname), str(investmentdate),str(unitvalue)))
		self.con.commit()
		self.cur.close()
		self.con.close()
		return res
	def search_user_details(self):
		res = self.cur.execute("SELECT * from users where UserName = \'%s\'" % (str(username_final)))
		result = self.cur.fetchall()
		self.cur.close()
		self.con.close()
		return result
	def get_investmentId(self, investmentname):
		res = self.cur.execute("SELECT InvestmentID from investments where name like \'%s\' limit 1" % (str(investmentname)))
		result = self.cur.fetchall()
		return result

	def transaction(self,invest_id,transaction_id,date,username_final,amount,in_type):
		res = self.cur.execute("INSERT into Transaction values(\'%s\',\'%s\',%d,%d,\'%s\',\'%s\')" % (str(username_final), str(date),amount, transaction_id,str(invest_id),str(in_type)))
		self.con.commit()
		self.cur.close()
		self.con.close()
		return res
	
	def createTrigger(self):
		self.cur.execute("DROP trigger if exists Trigger_Transaction")
		command = "CREATE TRIGGER Trigger_Transaction \
                    BEFORE INSERT ON Transaction \
                    FOR EACH ROW \
                    BEGIN \
                    SET @unitvalue = (SELECT UnitValue FROM Investments where InvestmentID = new.InvestmentID); \
                    IF new.Transaction_Amount < @unitvalue THEN SET new.Transaction_Amount = @unitvalue; \
                    END IF; \
                    END"
		self.cur.execute(command)
		self.con.commit()

	def stored_procedure(self):
		command = "CALL search_Investments();"
		self.cur.execute(command)
		result = self.cur.fetchall()
		self.cur.nextset()
		result1=self.cur.fetchall()
		self.con.commit()
		self.cur.close()
		self.con.close()
		res=[result,result1]
		return res

	def withdraw(self, investmentname):
		res = self.cur.execute("select InvestmentID from investments where Name = \'%s\'" % (str(investmentname)))
		print("here",file=sys.stdout)
		print(res, file=sys.stdout)
		result = self.cur.fetchall()
		if(len(result) == 0):
			return False
		res = self.cur.execute("Delete from transaction where InvestmentID = \'%s\' and UserName = \'%s\'" % (str(result[0]['InvestmentID']), str(username_final)))
		#res = self.cur.execute("Update transaction set isActive = 'N' where InvestmentID = \'%s\'" % (str(investmentname)))
		print("here again",file=sys.stdout)
		print(res, file=sys.stdout)
		self.con.commit()
		self.cur.close()
		self.con.close()
		return True

@app.route('/withdraw_investments', methods=["GET","POST"])
def withdraw_investments():
	if request.method == 'POST':
		investmentname = request.form.get("investmentname")
		print("inside withdraw",file=sys.stdout)
		db = Database()
		res = db.withdraw(investmentname)
		if(res):
			return render_template("withdraw_success.html")
		else:
			return render_template("withdraw_failure.html")

@app.route('/home_page', methods=["GET","POST"])
def home_page():
	return render_template("home1.html")

@app.route('/withdraw', methods=["GET","POST"])
def withdraw_inv():
	return render_template("withdraw.html")

@app.route('/signup', methods=["GET","POST"])
def insertUser():
	return render_template("signin.html")

@app.route('/users', methods=["GET","POST"])
def users():
	if request.method == 'POST':
		username = request.form.get("username")
		email = request.form.get("email")
		mobile = request.form["mobile"]
		fname = request.form["fname"]
		lname = request.form["lname"]
		address = request.form["address"]
		password = request.form["password"]
		hint = request.form["hint"]
		db = Database()
		res = db.user_add(username,email,mobile,fname,lname,address,password,hint)
		if(res):
			return render_template("home.html")
		else:
			return ""

@app.route('/edit_users', methods=["GET","POST"])
def edit_users():
	if request.method == 'POST':
		username = request.form.get("username")
		email = request.form.get("email")
		mobile = request.form["mobile"]
		fname = request.form["fname"]
		lname = request.form["lname"]
		address = request.form["address"]
		password = request.form["password"]
		hint = request.form["hint"]
		db = Database()
		res = db.user_replace(username,email,mobile,fname,lname,address,password,hint)
		if(res):
			return render_template("home.html")
		else:
			return ""

@app.route('/invest')
def invest():
	return render_template("invest.html")

@app.route('/most_investments')
def most_investments():
	return render_template("top_investments.html")

@app.route('/invest_amount', methods=["GET", "POST"])
def invest_amount():
	if request.method == 'POST':
		investmentname = request.form.get("investmentname")
		amount = int(request.form.get("amount"))
		in_type = '2'
		db = Database()
		investmentid = db.get_investmentId(investmentname)
		invest_id = investmentid[0].get('InvestmentID')
		today =datetime.today()
		y = datetime.now().strftime('%d')
		x = datetime.now().strftime('%h')
		z = datetime.now().strftime('%y')
		date=str(y)+"-"+str(x)+"-"+str(z)
		if(invest_id):
			global username_final
			transaction_id = random.randint(22000,50000)
			db.createTrigger()
			db.transaction(invest_id,transaction_id,date,username_final,amount,in_type)
		else:
			return render_template("investment_failure.html")
	return render_template("investment_success.html")

@app.route('/top_inv', methods=["GET", "POST"])
def top_inv():
	db = Database()
	res = db.stored_procedure()
	return render_template("topinvestments.html", result = res[1])

@app.route('/most_inv', methods=["GET", "POST"])
def most_inv():
	db = Database()
	res = db.stored_procedure()
	return render_template("investments.html", result = res[0])


@app.route('/get_your_investments', methods=["GET", "POST"])
def get_your_investments():
	db = Database()
	res = db.get_your_investments()
	

	return render_template("your_investments.html", result = res)
	
@app.route('/search_investments', methods=["GET", "POST"])
def search_investments():
	db = Database()
	res = db.search_your_investments(request.form.get("querystring"))
	print(res)
	if(res == "NotFound"):
		return "Investment Not Found"
	return render_template("search_investments.html", result = res)

@app.route('/delete_investments', methods=["GET", "POST"])
def delete_investments():
	db = Database()
	res = db.delete(request.form.get("querystring"))
	if res==0:
		return "no investments found with the given investmentID"
	return "Delete successful"

@app.route('/update_investments', methods=["GET", "POST"])
def update_investments():
	db = Database()
	res = db.update_investments(request.form.get("investmentid"),request.form.get("investmentname"))
	if res==0:
		return "No Investment exists with the given name"
	return "Update Successful"

@app.route('/edit_user_details', methods=["GET", "POST"])
def edit_user_details():
	db = Database()
	res = db.search_user_details()
	if res==0:
		return "ERROR OCCURED"
	return render_template("edit_details.html", result = res)

@app.route('/insert_investments', methods=["GET", "POST"])
def insert_investments():
	db = Database()
	res = db.insert_investments(request.form.get("investmendid"),request.form.get("investmenttype"),request.form.get("investmentdate"), request.form.get("investmentname"), request.form.get("unitvalue"))
	if res==0:
		return "insert failed"
	return "Insert Successful"

@app.route('/delete', methods=["GET", "POST"])
def delete():
	return render_template("delete.html")

@app.route('/update', methods=["GET", "POST"])
def update():
	return render_template("update.html")

@app.route('/insert', methods=["GET", "POST"])
def insert():
	return render_template("insert.html")

@app.route('/search', methods=["GET", "POST"])
def search():
	return render_template("search.html")

@app.route('/edit', methods=["GET", "POST"])
def edit():
	return render_template("edit_details.html")

@app.route('/home', methods=["GET","POST"])
def home():
	return render_template("home.html")

@app.route('/login', methods=["GET","POST"])
def login():
	if request.method == 'POST':
		username = request.form.get("uname")
		password = request.form.get("pass")
		print(username)
		global username_final
		username_final = username
		print(username_final)
		db = Database()
		res = db.authenticateUser(username, password)
		if(res):
			if(username=="admin"):
				return render_template("update.html")
			else:
				return render_template("home1.html")
		else:
			return "Not authenticated user"

if __name__ == "__main__":
	app.run(debug=True)
