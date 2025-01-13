from sqlalchemy import Column, Integer, String,Date, DateTime, Boolean, ForeignKey,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = "tbl_category"
    
    id          = Column(Integer, primary_key=True)
    name        = Column(String(255), nullable=False)
    created_at  = Column(DateTime)
    updated_at  = Column(DateTime)
    is_deleted  = Column(Boolean, default=False)

    # Reverse relationship
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "tbl_product"
    
    id                  = Column(Integer, primary_key=True)
    name                = Column(String(255), nullable=False)
    category_id         = Column(Integer, ForeignKey("tbl_category.id"), nullable=False)
    product_image       = Column(String(255), nullable=False)
    product_description = Column(String(255), nullable=False)
    price               = Column(DECIMAL(10, 2), nullable=False)  # Define price as a decimal (10 digits, 2 decimal places)
    created_at          = Column(DateTime)
    updated_at          = Column(DateTime)
    is_deleted          = Column(Boolean, default=False)

    # Relationship to Category
    category = relationship("Category", back_populates="products")
    
    # Reverse relationship for Cart
    cart_items = relationship("Cart", back_populates="product")
    
    # Reverse relationship for OrderProduct
    orders = relationship("OrderProduct", back_populates="product")


class User(Base):
    __tablename__ ="tbl_user"
    id          = Column(Integer, primary_key=True)
    name        = Column(String(255), nullable=False)
    address     = Column(String(255), nullable=False)
    contact_no  = Column(String(255), nullable=False)
    email       = Column(String(255), nullable=False)
    password    = Column(String(255), nullable=False)
    role        = Column(String(255), nullable=False)
    dob = Column(Date)
    age = Column(Integer, nullable=False)  # Changed to Integer
    gender = Column(String(50), nullable=False)  # Reduced length
    created_at      = Column(DateTime)
    updated_at      = Column(DateTime)
    is_deleted      = Column(Boolean, default=False)


class Cart(Base):
    __tablename__ = "tbl_cart"
    
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    product_id  = Column(Integer, ForeignKey("tbl_product.id"), nullable=False)
    quantity    = Column(Integer)
    created_at  = Column(DateTime)
    updated_at  = Column(DateTime)
    is_deleted  = Column(Boolean, default=False)

    # Relationship to Product
    product = relationship("Product", back_populates="cart_items")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.product.price,
            'is_deleted': self.is_deleted
        }

class orderBillDetails(Base):
    __tablename__="tbl_order_bill_details"
    id              = Column(Integer, primary_key=True)
    trasaction_no   = Column(String(255), nullable=False)
    bill_no         = Column(String(255), nullable=False)
    full_name      = Column(String(255), nullable=False)
    email           =  Column(String(255), nullable=False)
    shipping_address = Column(String(255), nullable=False)
    payment_method  =  Column(String(255), nullable=False)
    payment_method_dtl= Column(String(255), nullable=False)
    total_pay_amount = Column(DECIMAL(10,2))
    user_id         = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    created_at      = Column(DateTime)
    updated_at      = Column(DateTime)
    is_deleted      = Column(Boolean, default=False)    

# class PaymentTransaction(Base):
#     __tablename__="tbl_payment_details"
#     id              = Column(Integer, primary_key=True)
#     order_bill_details_id   =  Column(Integer, ForeignKey("tbl_order_bill_details.id"), nullable=False)
#     created_at      = Column(DateTime)
#     updated_at      = Column(DateTime)
#     is_deleted      = Column(Boolean, default=False)    

class OrderProduct(Base):
    __tablename__ = "tbl_order"
    
    id                      = Column(Integer, primary_key=True)
    user_id                 = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    product_id              = Column(Integer, ForeignKey("tbl_product.id"), nullable=False)
    order_bill_details_id   = Column(Integer, ForeignKey("tbl_order_bill_details.id"), nullable=False)
    quantity                = Column(Integer)
    price                   = Column(DECIMAL(10, 2), nullable=False)
    created_at              = Column(DateTime)
    updated_at              = Column(DateTime)
    is_deleted              = Column(Boolean, default=False)

    # Relationship with the Product model
    product = relationship("Product", back_populates="orders")

    # Relationship with the OrderBillDetails model
    # order_bill_details = relationship("OrderBillDetails", back_populates="order_products")
