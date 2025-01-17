from flask import Flask,render_template,request, redirect, url_for ,flash ,session, jsonify
from markupsafe import escape
from models import *
from database import session as db_session  
import datetime
import hashlib
from werkzeug.utils import secure_filename

import os
import json
import uuid
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
import seaborn as sns



app=Flask(__name__)
app.secret_key = 'ekjjaejkfr84384834i435dajdk2338998f9afdja'


@app.route('/', methods=['GET', 'POST'])
def index():
    product_list = db_session.query(Product).filter(Product.is_deleted == False).all()  
    category_list = db_session.query(Category).filter(Category.is_deleted == False).all()  
    
    if request.method == 'POST':
        search = request.form.get('search', '')  
        
        if search: 
            product_list = db_session.query(Product).filter(
                Product.is_deleted == False,
                Product.name.like(f"%{search}%")  
            ).all()
   
    return render_template("index.html", product_list=product_list, category_list=category_list,old_value=request.form)

# If user not logged , cart item will store to localStorage when user logged in and have cart item then these will 
# insered to user's cart
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        cart = data.get('cart', [])
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()
        # Check if the user exists in the database
        user = db_session.query(User).filter_by(email=email, password=password).first()

        if user:
            # Store user information in the session
            if user.role=='customer':
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role']= user.role
                for item in cart:
                    existing_cart_item = db_session.query(Cart).filter(
                        Cart.user_id == session['user_id'],
                        Cart.product_id == item['product_id'],
                        Cart.is_deleted == False
                    ).first()

                    if existing_cart_item:
                        # Update the quantity if the product already exists
                        existing_cart_item.quantity += 1
                        existing_cart_item.updated_at = datetime.datetime.now()
                        
                    else:
                        # Add a new cart item if the product does not exist
                        new_cart_item = Cart(
                            user_id=session['user_id'],
                            product_id=item['product_id'],
                            quantity=1,
                            created_at=datetime.datetime.now(),
                            updated_at=datetime.datetime.now(),
                            is_deleted=False
                        )
                        db_session.add(new_cart_item)
                        
            elif user.role == 'super_admin':
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role']= user.role
            # elif user.role == 'admin':
            #     session['user_id'] = user.id
            #     session['user_name'] = user.name
            # Save cart data to the Cart model


            db_session.commit()

            # Respond with success
            return jsonify({'success': True})
        else:
            # Respond with error message
            return jsonify({'success': False, 'error': 'Invalid email or password'})





@app.route('/user_logout', methods=['GET', 'POST'])
def user_logout():
    session.clear()
    return redirect('/')






@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contact_no = request.form['contact_no']
        email = request.form['email']
        dob = request.form['dob']
        gender = request.form['gender']
        password = request.form['password']

        # Calculate age from DOB
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d')  # Convert string to datetime object
        today = datetime.datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()

        new_user = User(
            name=name,
            address=address,
            contact_no=contact_no,
            email=email,
            dob=dob_date,
            gender=gender,
            age=age,
            role="customer",
            password=password,  
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )

        db_session.add(new_user)
        db_session.commit()
        return redirect(url_for('user_login'))  
    
    return render_template('user_signup.html')




@app.route('/product_details/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    product = db_session.query(Product).filter(Product.is_deleted == False, Product.id == product_id).first()  # Not deleted
    is_logged_in = 'user_id' in session

    if request.method == "POST" and request.form['btn_add_to_cart'] == "Add to Cart":
        if is_logged_in:
            existing_cart_item = db_session.query(Cart).filter(
                Cart.user_id == session['user_id'],
                Cart.product_id == product_id,
                Cart.is_deleted == False
            ).first()

            if existing_cart_item:
                existing_cart_item.quantity += 1
                existing_cart_item.updated_at = datetime.datetime.now()
                db_session.commit()
                flash('Product Added to cart', 'success')
            else:
                new_cart_item = Cart(
                    user_id=session['user_id'],
                    product_id=product_id,
                    quantity=1,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                    is_deleted=False
                )
                db_session.add(new_cart_item)
                db_session.commit()
                flash('Product Added to cart', 'success')
            
            
        
        return redirect(url_for('product_details', product_id=product_id))

    if product is None:
        flash('Product not found', 'danger')
        return redirect(url_for('index'))  
    return render_template('product_details.html', product=product, is_logged_in=is_logged_in)

#Customer Login Check
def customer_login_check():
    if 'user_id' not in session or session.get('user_role') != 'customer':
        return redirect(url_for('user_login')) 
    return None  

#if user not logged , cart item stores to localStorage ,if user logged then cart item stores to user's account
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_list=''
    is_logged_in=False
    total_amt=''
    if 'user_id'  in session and session.get('user_role') == 'customer':
        is_logged_in=True
        cart_list = db_session.query(Cart).filter(Cart.is_deleted == False,Cart.user_id == session['user_id']).all()
        
        total_amt=0
        for data in cart_list:
            total_amt=total_amt+data.product.price
        if request.method=="POST" and request.form['btnremove_cart_item']=="Remove":
            product_id=request.form['product_id']
            cart_item = db_session.query(Cart).get(product_id)
            if cart_item:
                #cart_item.is_delete=True
                db_session.delete(cart_item)
                db_session.commit()
                flash('Category deleted successfully', 'success')
            return redirect(url_for('cart'))    
    return render_template('cart.html', cart_list=cart_list,is_logged_in=is_logged_in,total_amt=total_amt)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    # try:
    if True:
        # Parse JSON request data
        data = request.get_json()
        product_id = data.get('product_id')
        change = data.get('change', 0)

        # Find the cart item for the logged-in user
        cart_item = db_session.query(Cart).filter_by(
            user_id=session.get('user_id'),
            product_id=product_id,
            is_deleted=False
        ).first()

        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        # print('change',change, type(change)) ;exit()
        if change == 'delete':
            db_session.delete(cart_item)
            db_session.commit()
            return jsonify({'success': True, 'new_quantity': 0})
        # Update the quantity
        cart_item.quantity += change

        # Remove the item if quantity is 0 or less
        if cart_item.quantity <= 0:
            db_session.delete(cart_item)
            db_session.commit()
            return jsonify({'success': True, 'new_quantity': 0})


        db_session.commit()

        return jsonify({'success': True, 'new_quantity': cart_item.quantity,'price':cart_item.product.price})



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    redirect_response = customer_login_check()
    if redirect_response:  
        return redirect_response
    total_bill = 0
    cart_list = []
    is_logged_in = True
    cart_list = db_session.query(Cart).filter(Cart.is_deleted == False, Cart.user_id == session['user_id']).all()
    total_bill = sum(data.product.price for data in cart_list)

    if request.method == 'POST':
        billdet = orderBillDetails(
            trasaction_no =str(uuid.uuid4()),  # Unique transaction ID
            bill_no="BILL-" + str(uuid.uuid4())[:8],  
            full_name = request.form['name'],
            email= request.form['email'],
            shipping_address= request.form['address'],
            payment_method=request.form['payment_method'],
            payment_method_dtl=request.form['payment_method_dtl'],
            user_id=session['user_id'],
            total_pay_amount= request.form['total_pay_amount'],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            is_deleted=False
        )
        db_session.add(billdet)
        db_session.commit()

        orders = []
        for data in cart_list:
            order = OrderProduct(
                user_id=session['user_id'],
                product_id=data.product_id,
                order_bill_details_id=billdet.id,
                quantity  = data.quantity,
                price    = data.product.price,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                is_deleted=False
            )
            orders.append(order)

        db_session.add_all(orders)
        db_session.commit()

        # clear the cart after the checkout is complete
        for data in cart_list:
            data.is_deleted = True
        db_session.commit()
        return redirect(url_for('bill_detail', bill_id=billdet.id))
    return render_template('checkout.html', is_logged_in=is_logged_in, total_bill=total_bill, cart_list=cart_list)

@app.route('/bill_detail/<bill_id>', methods=['GET'])
def bill_detail(bill_id):
    redirect_response = customer_login_check()
    if redirect_response:  
        return redirect_response
    bill_dtl = db_session.query(orderBillDetails).filter(orderBillDetails.id == bill_id).first()
    order_products = db_session.query(OrderProduct).filter(OrderProduct.order_bill_details_id == bill_id).all()
    tota_amt=0
    for data in order_products:
        tota_amt+=(data.quantity * data.price)
    if not bill_dtl:
        return "Bill not found", 404
    return render_template('bill_detail.html', bill_dtl=bill_dtl, order_products=order_products,tota_amt=tota_amt)

@app.route('/order_history')
def order_history():
    redirect_response = customer_login_check()
    if redirect_response:  
        return redirect_response
    order_history_list = db_session.query(orderBillDetails).filter(orderBillDetails.is_deleted == False).all()
    return render_template('order_history.html', order_history_list=order_history_list,)


    ########################################
    ############# Admin Start ###################
    #########################################

# Admin login check function
def admin_login_check():
    if 'user_id' not in session or session.get('user_role') != 'super_admin':
        return redirect(url_for('admin_login')) 
    return None  

@app.route('/admin_login')
def admin_login():
    super_admin_record_exist= db_session.query(User).filter(User.role == 'super_admin').all()
    if not super_admin_record_exist:
        return redirect(url_for('admin_signup')) 
    return render_template('admin_login.html')

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contact_no = request.form['contact_no']
        email = request.form['email']
        dob = request.form['dob']
        gender = request.form['gender']
        password = request.form['password']

        # Calculate age from DOB
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d')  # Convert string to datetime object
        today = datetime.datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))


        new_user = User(
            name=name,
            address=address,
            contact_no=contact_no,
            email=email,
            dob=dob_date,
            gender=gender,
            age=age,
            role="super_admin",
            password=password,  
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )

        db_session.add(new_user)
        db_session.commit()
        return redirect(url_for('admin_login')) 
    
    return render_template('super_admin_signup.html')  



@app.route('/category_master', methods=['GET', 'POST'])
def category_master():
    redirect_response = admin_login_check()
    if redirect_response: 
        return redirect_response

    category_list = db_session.query(Category).filter(Category.is_deleted == False).all()  
  
    if request.method == 'POST':

        if request.form.get('_method') == 'PUT':
            identity = request.form.get('identity') 
            name = request.form['name']

            item = db_session.query(Category).get(identity)

            if item:
                item.name = name
                item.updated_at = datetime.datetime.now()
                db_session.commit()
                flash('Category updated successfully', 'success')
            else:
                flash('Category not found', 'danger')

            return redirect(url_for('category_master'))  

        if request.form.get('_method') == 'DELETE':
            identity = request.form.get('identity')  

            item = db_session.query(Category).get(identity)
            if item:
                item.is_delete=True
                # db_session.delete(item)
                db_session.commit()

                flash('Category deleted successfully', 'success')
            else:
                flash('Category not found', 'danger')

            return redirect(url_for('category_master'))  

        else:
            name = request.form['name']
           
            item = Category(name=name, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            db_session.add(item)
            db_session.commit()
            flash('Category added successfully', 'success')
            return redirect(url_for('category_master')) 
    return render_template('admin_templates/category_master.html', data_list=category_list)



@app.route('/product_master', methods=['GET', 'POST'])
def product_master():
    redirect_response = admin_login_check()
    if redirect_response:  
        return redirect_response
    
    product_list = db_session.query(Product).filter(Product.is_deleted == False).all()  
    category_list = db_session.query(Category).filter(Category.is_deleted == False).all()  

    if request.method == 'POST':
        # Handle the PUT method (update an existing product)
        if request.form.get('_method') == 'PUT':
            identity = request.form.get('identity')
            name = request.form['name']
            category_id = request.form['category']
            product_image = request.files.get('product_image')  
            product_description = request.form['product_description']
            price = request.form['price']

            # Fetch product to update
            product = db_session.query(Product).get(identity)
            if product:
                product.name = name
                product.category_id = category_id
                product.price = price
                product.product_description = product_description

                if product_image and product_image.filename:  
                    ext = os.path.splitext(product_image.filename)[1]  
                    # Generate a unique filename using UUID and timestamp
                    unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                    # Secure the filename
                    filename = secure_filename(unique_name)
                    product_image.save(os.path.join('static/uploads/products', filename))
                    product.product_image = filename
                product.updated_at = datetime.datetime.now()
                db_session.commit()
                flash('Product updated successfully', 'success')
            else:
                flash('Product not found', 'danger')

            return redirect(url_for('product_master'))


        if request.form.get('_method') == 'DELETE':
            identity = request.form.get('identity')  
            product = db_session.query(Product).get(identity)

            if product:
                product.is_delete=True
                # db_session.delete(product)
                db_session.commit()
                flash('Product deleted successfully', 'success')
            else:
                flash('Product not found', 'danger')

            return redirect(url_for('product_master')) 

        
        else:
            name = request.form['name']
            category_id = request.form['category']
            product_image=request.files['product_image']
            product_description =request.form['product_description']
            price=request.form['price']
          

                # Ensure that a file was uploaded
            if product_image:
                ext = os.path.splitext(product_image.filename)[1]  
                unique_filename = f"{uuid.uuid4().hex}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                filename = secure_filename(unique_filename)
                file_path = os.path.join('static/uploads/products', filename)
                product_image.save(file_path)
                product = Product(
                    name=name,
                    category_id=category_id,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                    product_image=filename,  
                    product_description=product_description,
                    price=price
                )

                db_session.add(product)
                db_session.commit()
                flash('Product added successfully', 'success')
            else:
                flash('No image uploaded', 'danger')
                return redirect(url_for('product_master'))  
            return redirect(url_for('product_master'))  

    return render_template('admin_templates/product_master.html', data_list=product_list,category_list=category_list)


@app.route('/user_list')
def user_list():
    redirect_response = admin_login_check()
    if redirect_response:  
        return redirect_response
    
    user_list = db_session.query(User).filter(User.is_deleted == False,User.role != 'super_admin').all()
    return render_template('admin_templates/user_list.html',user_list=user_list)

@app.route('/user_alter/<string:action>/', defaults={'id': None}, methods=["GET", "POST"])
@app.route('/user_alter/<string:action>/<int:id>', methods=["GET", "POST"])
def user_alter(action, id):
    redirect_response = admin_login_check()
    if redirect_response:  
        return redirect_response
    
    # If 'id' is provided and action is not 'create', fetch the user
    if action != 'create' and id:
        user = db_session.query(User).filter(User.is_deleted == False, User.role != 'super_admin', User.id == id).first()
    else:
        user = None

    if action != 'create' and not user:
        return redirect(url_for('user_list'))  
    
    template_name = 'admin_templates/user_alter.html'

    if action == 'view':
        field_disable = "disabled='true'"
        return render_template(template_name, action=action, user=user, field_disable=field_disable)

    elif action == 'edit':
        if request.method == 'POST':
            # Get data from form
            user.name = request.form['name']
            user.address = request.form['address']
            user.contact_no = request.form['contact_no']
            user.email = request.form['email']
            user.password = request.form['password']
            user.role = request.form['role']
            user.updated_at = datetime.datetime.now()

            db_session.commit()
            return redirect(url_for('user_list'))  

        return render_template(template_name, action=action, user=user)

    elif action == 'delete':
        if request.method == 'POST':
            user.is_deleted = True
            db_session.commit()
            return redirect(url_for('user_list'))  

    elif action == 'create':
        if request.method == 'POST':
            # Create a new user
            user = User(
                name=request.form['name'],
                address=request.form['address'],
                contact_no=request.form['contact_no'],
                email=request.form['email'],
                password=request.form['password'],
                role=request.form['role'],
                updated_at=datetime.datetime.now(),
            )
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('user_list'))  

        return render_template(template_name, action=action)

    return redirect(url_for('user_list'))


@app.route('/order_transaction', methods=["GET", "POST"])
def order_transaction():
    redirect_response = admin_login_check()
    if redirect_response:  
        return redirect_response
    
    order_transaction_list = db_session.query(orderBillDetails).filter(orderBillDetails.is_deleted == False).all()
    return render_template('admin_templates/order_transaction.html',order_transaction_list=order_transaction_list,request=request)

@app.route('/order_transaction_view/<bill_id>', methods=['GET'])
def order_transaction_view(bill_id):
    redirect_response = admin_login_check()
    if redirect_response:  
        return redirect_response
    bill_dtl = db_session.query(orderBillDetails).filter(orderBillDetails.id == bill_id).first()
    order_products = db_session.query(OrderProduct).filter(OrderProduct.order_bill_details_id == bill_id).all()
    tota_amt=0
    for data in order_products:
        tota_amt+=(data.quantity * data.price)
    if not bill_dtl:
        return "Bill not found", 404
    return render_template('admin_templates/order_transaction_view.html', bill_dtl=bill_dtl, order_products=order_products,tota_amt=tota_amt)


@app.route('/dashboard')
def dashboard():
    redirect_response = admin_login_check()
    if redirect_response:  # If admin_login_check returns a redirect, return it
        return redirect_response
    
    sales_df=fetch_sales_data()
    user_data = db_session.query(User.id, User.age, User.gender).filter(User.role != 'super_admin').all()
    user_df = pd.DataFrame(user_data, columns=["user_id", "age", "gender"])
    print(user_df)

    plot_popular_products(sales_df)
    plot_sales_trend(sales_df)

    plot_user_demographics(user_df)
    sale_analytics_data = plot_popular_products(sales_df)

    plot_products_qty =    chart_data = {
                                            'labels': sales_df['product_name'].tolist(),  # Product names as labels
                                            'data': sales_df['quantity'].tolist()  # Total sales as data
                                        }
    # sale_analytics_data=[]
    product_list = db_session.query(Product).filter(Product.is_deleted == False).all()
    
    return render_template('admin_templates/dashboard.html', product_list=product_list,sale_analytics_data=sale_analytics_data,plot_products_qty=plot_products_qty)


# Fetch sales data from the database
def fetch_sales_data():
    # Fetch sales data by joining OrderProduct, Product, and User
    sales_data = db_session.query(
        OrderProduct.created_at,
        OrderProduct.price,
        OrderProduct.quantity,
        Product.name.label('product_name'),
        User.id.label('user_id')
    ).join(Product).join(User).all()

    # Convert to pandas DataFrame
    sales_df = pd.DataFrame(sales_data, columns=["created_at", "price", "quantity", "product_name", "user_id"])
    sales_df['total_sales'] = sales_df['price'] * sales_df['quantity']
    sales_df['created_at'] = pd.to_datetime(sales_df['created_at'])
    sales_df['month'] = sales_df['created_at'].dt.to_period('M')
    return sales_df

# print(fetch_sales_data())

# Plot Popular Products (Bar Chart)
def plot_popular_products(sales_df):
    # Group by product name and calculate total sales
    product_sales = sales_df.groupby('product_name')['total_sales'].sum().reset_index()
    # print(product_sales)
    # Plot Top Products (Bar Chart)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=product_sales, x='product_name', y='total_sales', palette='viridis')
    plt.title('Popular Products Based on Sales', fontsize=16)
    plt.xlabel('Product', fontsize=14)
    plt.ylabel('Total Sales (₹)', fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/images/analytics/plot_popular_products.png")
    # plt.show()
    plt.close() 

    chart_data = {
        'labels': product_sales['product_name'].tolist(),  # Product names as labels
        'data': product_sales['total_sales'].tolist()  # Total sales as data
    }
    return chart_data
    

def plot_sales_trend(sales_df):
    # Resample the data by month and calculate total sales
    sales_df['month'] = sales_df['created_at'].dt.to_period('M').astype(str)  # Convert month to string format
    monthly_sales = sales_df.groupby('month')['total_sales'].sum().reset_index()

    # Ensure 'total_sales' is numeric
    monthly_sales['total_sales'] = pd.to_numeric(monthly_sales['total_sales'], errors='coerce')

    # Plot Sales Trend Over Time (Line Chart)
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=monthly_sales, x='month', y='total_sales', marker='o', color='b')
    plt.title('Sales Trend Over Time', fontsize=16)
    plt.xlabel('Month', fontsize=14)
    plt.ylabel('Total Sales (₹)', fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/images/analytics/plot_sales_trend.png")
    # plt.show()
    plt.close() 




# User Data for Demographics (Assume we fetch this data)
def plot_user_demographics(user_df):
    # User Age Distribution (Histogram)
    plt.figure(figsize=(10, 6))
    sns.histplot(user_df['age'], bins=10, kde=True, color='c')
    plt.title('User Age Distribution', fontsize=16)
    plt.xlabel('Age', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.tight_layout()
    plt.savefig("static/images/analytics/plot_user_demographics_histogram.png")
    # plt.show()
    plt.close() 

    # User Gender Distribution (Pie Chart)
    gender_counts = user_df['gender'].value_counts()
    plt.figure(figsize=(7, 7))
    gender_counts.plot.pie(autopct='%1.1f%%', colors=sns.color_palette('pastel'), legend=False)
    plt.title('User Gender Distribution', fontsize=16)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig("static/images/analytics/plot_user_demographics_pie.png")

    # plt.show()
    plt.close() 



    ########################################
    ############# Admin End ###################
    #########################################