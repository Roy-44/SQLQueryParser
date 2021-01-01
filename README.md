# SQL Parser
The app will decide whether a SQL query is valid.
Accepted schemes: Customers(Name: STRING, Age: INTEGER), Orders(CustomerName: STRING, Product: STRING, Price: INTEGRER).
The query must end with ';' and must contain 'SELECT', 'FROM' and 'WHERE'.

Examples:
=========
Valid queries:
--------------
SELECT Customers.Name FROM Customers WHERE Customers.Age=25;
SELECT Customers.Name FROM Customers WHERE Customers.Name=’Mike’;
SELECT DISTINCT Customers.Name FROM Customers WHERE Customers.Age=25;
SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE Customers.Name=Orders.CustomerName;
SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE Customers.Name=Orders.CustomerName AND Orders.Price>1000;
SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) AND Orders.Price>1000;
SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>59);

Invalid queries:
----------------
SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>1000;
SELECT Customers.Color,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>1000);
