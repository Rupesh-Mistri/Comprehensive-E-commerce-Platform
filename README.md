# Comprehensive E-commerce Platform

The **Comprehensive E-commerce Platform** is a user-friendly online shopping solution designed to connect businesses with customers seamlessly.

## Features

### For Super Admin:
- **Product Management**: Categorise products using the category and Add, update, and delete using product master .
- **User Management**: Manage user accounts .
- **Analytics Dashboard**: Gain insights into product sales, user demographics, and trends using tools like NumPy, Pandas, Matplotlib, Seaborn, and Chart.js.

### For Customers:
- **Account Management**: Easy signup and login for a personalized experience.
- **Product Browsing**: Explore products with search options.
- **Shopping Cart**: Add items to a cart for streamlined purchasing.
- **Order Placement**: Simple and secure order processing.

## Technology Stack
- **Backend**: Python and Flask
- **Database**: MySQL
- **Analytics**: NumPy, Pandas, Matplotlib, Seaborn, and Chart.js
- **Frontend**: HTML, CSS, Bootstrap, and JavaScript

This platform simplifies online shopping and management, offering a complete solution for businesses and customers.


# Project Structure 

│   app.py
│   database.py
│   models.py
│   README.md
│   requirements.txt
│
├───static
│   ├───css
│   │       admin_style.css
│   │       bootstrap5.3.min.css
│   │       style.css
│   │
│   ├───icons
│   │       cart.svg
│   │
│   ├───images
│   │   │   slide_image1.png
│   │   │   slide_image2.png
│   │   │   slide_image3.png
│   │   │
│   │   └───analytics
│   │           plot_popular_products.png
│   │           plot_sales_trend.png
│   │           plot_user_demographics_histogram.png
│   │           plot_user_demographics_pie.png
│   │
│   └───js
│           admin_main.js
│           bootstrap.min.js
│           main.js
│
└───templates
    │   admin_login.html
    │   base_layout.html
    │   bill_detail.html
    │   cart.html
    │   checkout.html
    │   footer.html
    │   header.html
    │   index.html
    │   order_history.html
    │   product_details.html
    │   super_admin_signup.html
    │   user_login.html
    │   user_signup.html
    │
    └───admin_templates
            admin_base_layout.html
            admin_footer.html
            category_master.html
            dashboard.html
            order_transaction.html
            order_transaction_view.html
            product_master.html
            user_alter.html
            user_list.html

# Getting Started
## Prerequisites
To run project locally you need following
 -python
 -mysql

Installation
1.Clone the Repository 
   ```
  git clone https://github.com/Rupesh-Mistri/Comprehensive-E-commerce-Platform.git
    
  cd Comprehensive-E-commerce-Platform
  ```
2. install requirement 
```
   pip install -r requirements.txt
```
3. Environment variables:
```
    change SQLALCHEMY_DATABASE_URI_LOCAL = your_connection_string
```

4. Running the Application
```
  flask run
```


5. Set Up the App
- Admin Setup: On the first run, you'll need to add categories and products to the master data.
- Click on Admin Login. Since no records exist for the super admin initially, you will be prompted to sign up. After signing up, log in as the admin.
- Once logged in, you can add categories and products to the product master.
- After adding products, they will appear on the homepage. Customers will then be able to:
    -   Browse products
    -   Sign up and log in
    -   Add items to the cart
    -   Place orders