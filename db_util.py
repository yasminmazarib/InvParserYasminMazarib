import sqlite3
from contextlib import contextmanager
import app


DB_PATH = "invoices.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():                       #Creating tables in DB
    with get_db() as conn:            #Connection opens → workers → saves → closes
        cursor = conn.cursor()     # Cursor=runs SQL commands
        #Table 1: invoices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (   
                InvoiceId TEXT PRIMARY KEY,
                VendorName TEXT,
                InvoiceDate TEXT,
                BillingAddressRecipient TEXT,
                ShippingAddress TEXT,
                SubTotal REAL,
                ShippingCost REAL,
                InvoiceTotal REAL
            )
        """)
        #REAL = float
        #This table stores:The main invoice data

#Table 2: confidences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confidences (
                InvoiceId TEXT PRIMARY KEY,
                VendorName REAL,
                InvoiceDate REAL,
                BillingAddressRecipient REAL,
                ShippingAddress REAL,
                SubTotal REAL,
                ShippingCost REAL,
                InvoiceTotal REAL,
                FOREIGN KEY (InvoiceId) REFERENCES invoices(InvoiceId)
            )
        """)
        #Table 3: items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                InvoiceId TEXT,
                Description TEXT,
                Name TEXT,
                Quantity REAL,
                UnitPrice REAL,
                Amount REAL,
                FOREIGN KEY (InvoiceId) REFERENCES invoices(InvoiceId)
            )
        """)

#Gets the JSON returned from /extract
def save_inv_extraction(result):
    data = result.get("data", {})           
    data_confidence = result.get("dataConfidence", {})
    
    invoice_id = data.get("InvoiceId") #Outputs the invoice ID
    if invoice_id: #Only if there is an InvoiceId – saved
        with get_db() as conn:
            cursor = conn.cursor()   #Opens a connection and prepares a cursor
            
            # Insert invoice
            cursor.execute("""
                INSERT OR REPLACE INTO invoices 
                (InvoiceId, VendorName, InvoiceDate, BillingAddressRecipient, 
                 ShippingAddress, SubTotal, ShippingCost, InvoiceTotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                data.get("VendorName"),
                data.get("InvoiceDate"),
                data.get("BillingAddressRecipient"),
                data.get("ShippingAddress"),
                data.get("SubTotal"),
                data.get("ShippingCost"),
                data.get("InvoiceTotal")
            ))
            
            # Insert confidences
            cursor.execute("""
                INSERT OR REPLACE INTO confidences 
                (InvoiceId, VendorName, InvoiceDate, BillingAddressRecipient,
                 ShippingAddress, SubTotal, ShippingCost, InvoiceTotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                data_confidence.get("VendorName"),
                data_confidence.get("InvoiceDate"),
                data_confidence.get("BillingAddressRecipient"),
                data_confidence.get("ShippingAddress"),
                data_confidence.get("SubTotal"),
                data_confidence.get("ShippingCost"),
                data_confidence.get("InvoiceTotal")
            ))
            
            # Insert line items
            line_items = data.get("Items", [])  #List of items
            cursor.execute("DELETE FROM items WHERE InvoiceId = ?", (invoice_id,)) #Deletes previous items (in case of UPDATE)
            for item in line_items:  #Goes through each item
                cursor.execute("""
                    INSERT INTO items 
                    (InvoiceId, Description, Name, Quantity, UnitPrice, Amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    item.get("Description"),
                    item.get("Name"),
                    item.get("Quantity"),
                    item.get("UnitPrice"),
                    item.get("Amount")
                ))

def get_invoices_by_vendor(vendor_name):  #Returns all invoices from a specific vendor
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("select InvoiceId from invoices where VendorName = ?",(vendor_name,)) #Looking for only the InvoiceId
        rows= cursor.fetchall() #Returns a list of results.
        invoices = []
        for r in rows:
            invoice_id = r[0]  #The first column (InvoiceId)
            invoices.append(getInvoiceById(invoice_id))   #Retrieve all invoice data and add to list

    return invoices

def getInvoiceById(invoice_id): #Returns one invoice
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM invoices
            WHERE InvoiceId = ?;
        """, (invoice_id,))  #Brings the entire invoice line
        row = cursor.fetchone() #Returns one row

        if not row:
            return None #If the invoice does not exist
    

        cursor.execute("""
            SELECT Description, Name, Quantity, UnitPrice, Amount
            FROM items
            WHERE InvoiceId = ?;
        """, (invoice_id,))
        items_rows = cursor.fetchall()
    
    items = []
    for item in items_rows:
        items.append({
            "Description": item[0],
            "Name": item[1],
            "Quantity": item[2],
            "UnitPrice": item[3],
            "Amount": item[4]
        })

    return {
        "InvoiceId": row[0],
        "VendorName": row[1],
        "InvoiceDate": row[2],
        "BillingAddressRecipient": row[3],
        "ShippingAddress": row[4],
        "SubTotal": row[5],
        "ShippingCost": row[6],
        "InvoiceTotal": row[7],
        "Items": items
    }

   